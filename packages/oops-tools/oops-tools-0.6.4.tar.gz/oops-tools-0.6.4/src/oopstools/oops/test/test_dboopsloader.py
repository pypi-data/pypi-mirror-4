# Copyright 2005-2011 Canonical Ltd.  All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from datetime import (
    date,
    datetime,
    )
import os
import urllib

from fixtures import TempDir
from oops_datedir_repo.serializer_bson import write as write_bson
from oops_datedir_repo.serializer_rfc822 import write
from pytz import utc
from testtools import TestCase

from oopstools.oops import helpers
from oopstools.oops.dboopsloader import (
    _find_dirs,
    OopsLoader,
    )
from oopstools.oops.models import (
    DBOopsRootDirectory,
    Oops,
    parsed_oops_to_model_oops,
    MAX_URL_LEN
    )


def create_directory_structure(root, structure):
    for directory in structure:
        os.makedirs(os.path.join(root, directory))


class TestDirFinder(TestCase):

    def _getExpectedDirs(self, root, dirs):
        return [os.path.join(root, directory) for directory in dirs]

    def setUp(self):
        super(TestDirFinder, self).setUp()
        self.root_dir = self.useFixture(TempDir()).path

    def test_find_dirs_no_matches(self):
        # Directories containing no subdirectories by date are not
        # considered as OOPS directories.
        create_directory_structure(self.root_dir, [
            'no-oopses/test',
            ])
        self.assertEqual([], _find_dirs([self.root_dir]))

    def test_find_dirs_matches(self):
        # Directories with subdirectories named YYYY-MM-DD are considered
        # to contain OOPSes.
        create_directory_structure(self.root_dir, [
            'oopses/2011-02-02',
            'more/deeper/2009-12-12',
            ])
        self.assertEqual(
            set(self._getExpectedDirs(self.root_dir,
                                      ['oopses', 'more/deeper'])),
            set(_find_dirs([self.root_dir])))

    def test_find_dirs_combined(self):
        # Directories with subdirectories named YYYY-MM-DD and other
        # subdirectories are considered to contain OOPSes, and their
        # non-date subdirectories can also contain OOPSes.
        create_directory_structure(self.root_dir, [
            'oopses/2011-02-02',
            'oopses/deeper/2009-12-12',
            ])
        self.assertEqual(
            set(self._getExpectedDirs(self.root_dir,
                                      ['oopses', 'oopses/deeper'])),
            set(_find_dirs([self.root_dir])))

    def test_find_dirs_symbolic_links_ignored(self):
        # Symbolic links are ignored.
        create_directory_structure(self.root_dir, [
            'oopses/2011-02-02',
            ])
        os.symlink(os.path.join(self.root_dir, 'oopses'),
                   os.path.join(self.root_dir, 'symlink'))
        self.assertEqual(
            self._getExpectedDirs(self.root_dir, ['oopses']),
            _find_dirs([self.root_dir]))

    def test_find_dirs_notexist(self):
        # Empty list is returned when requested root directory
        # does not exist.
        self.assertEqual(
            [],
            _find_dirs([self.root_dir + '/path/which/does/not/exist']))


class TestIncrementalLoading(TestCase):

    def test_nonsequential_filenames(self):
        # The new lock-free writer code makes no warranty about the order of
        # filenames on disk.
        helpers._today = date(2008, 01, 13)
        self.root_dir = self.useFixture(TempDir()).path
        os.mkdir(self.root_dir + '/2008-01-13')
        # Write and import a file.
        python_oops = {'id': 'OOPS-824S101', 'reporter': 'edge',
            'type': 'ValueError', 'value': 'a is not an int',
            'time': datetime(2008, 1, 13, 23, 14, 23, 00, utc)}
        with open(self.root_dir + '/2008-01-13/OOPS-824', 'wb') as output:
            write(python_oops, output)
        # Add our test dir to the db.
        oopsrootdir = DBOopsRootDirectory(
            root_dir=self.root_dir, last_date=None, last_oops=None)
        oopsrootdir.save()
        self.addCleanup(oopsrootdir.delete)
        loader = OopsLoader()
        self.assertEqual(1, len(loader.oopsdirs))
        start_date = date(2008, 01, 13)
        list(loader.find_oopses(start_date))
        # Should have loaded the oops.
        self.assertNotEqual(None, Oops.objects.get(oopsid='OOPS-824S101'))
        # Now we add a new oops with a disk path that sorts lower, but it
        # should still be picked up. For added value (we expect this to happen)
        # we make the new oops a bson oops.
        python_oops['id'] = 'OOPS-123S202'
        with open(self.root_dir + '/2008-01-13/OOPS-123', 'wb') as output:
            write_bson(python_oops, output)
        loader = OopsLoader()
        list(loader.find_oopses(start_date))
        self.assertNotEqual(None, Oops.objects.get(oopsid='OOPS-123S202'))


class TestParsedToModel(TestCase):

    def test_url_handling(self):
        unicode_url = u'http://example.com/foo\u2019s asset'
        report = { 'url': unicode_url, 'id': 'testurlhandling'}
        expected_url = urllib.quote(unicode_url.encode('utf8'))
        oops = parsed_oops_to_model_oops(report, 'test_url_handling')
        self.assertEqual(expected_url, oops.url)

    def test_no_topic_pageid_empty_bug_880641(self):
        report = { 'url': 'foo', 'id': 'testnotopichandling'}
        oops = parsed_oops_to_model_oops(report, 'bug_880641')
        self.assertEqual('', oops.pageid)

    def test_broken_header_handling(self):
        broken_url = '/somep\xe1th'
        user_agent = '\xf8\x07\x9e'
        report = { 'url': broken_url,
                   'id': 'testbrokenheader',
                   'req_vars': [
                       [ 'HTTP_USER_AGENT', user_agent ]
                   ]
        }
        # We handle such URL's by url quoting them, failing to do so being a
        # (not uncommon) producer mistake.
        expected_url = urllib.quote(broken_url)
        expected_user_agent = urllib.quote(user_agent)
        oops = parsed_oops_to_model_oops(report, 'test_broken_url_handling')
        self.assertEqual(expected_url, oops.url)
        self.assertEqual(expected_user_agent, oops.user_agent)

    def test_broken_reqvars_bug_885416(self):
        # If the tuples in req_vars have only one element the oops still needs
        # to be loaded - we need to tolerate some bad data.
        report = {'req_vars': [('foo',)], 'id': 'bug-885416'}
        oops = parsed_oops_to_model_oops(report, 'test-bug-885416')

    def test_dict_reqvars_bug_888866(self):
        # If req_vars is a dict, it still processes stuff.
        report = {
            'id': 'bug-888866',
            'req_vars': {'HTTP_USER_AGENT': 'myuseragent'}
        }
        oops = parsed_oops_to_model_oops(report, 'bug-888866')
        self.assertEqual('myuseragent', oops.user_agent)

    def test_nonlist_timeline(self):
        # A timeline that is nonzero and not a list is turned into a one-entry
        # timeline starting when the oops starts with no duration and category
        # badtimeline.
        report = {
            'id': 'bug-890001-1',
            'timeline': 'a'
        }
        oops = parsed_oops_to_model_oops(report, 'bug-890001-1')
        self.assertEqual(
            [(0, 0, 'badtimeline', 'a', 'unknown')], oops.statements)
        
    def test_short_timeline_row(self):
        # A timeline row that is short is padded with 'unknown' or 0's.
        report = {
            'id': 'bug-890001-2',
            'timeline': [
                (),
                (1,),
                (1, 2,),
                (1, 2, 'foo'),
                ],
        }
        oops = parsed_oops_to_model_oops(report, 'bug-890001-2')
        self.assertEqual([
            (0, 0, 'unknown', 'unknown', 'unknown'),
            (1, 0, 'unknown', 'unknown', 'unknown'),
            (1, 2, 'unknown', 'unknown', 'unknown'),
            (1, 2, 'foo', 'unknown', 'unknown'),
            ], oops.statements)

    def test_long_timeline_row(self):
        # A timeline row that is long is truncated.
        report = {
            'id': 'bug-890001-3',
            'timeline': [
                (1, 2, 'foo', 'bar', 'baz', 'quux'),
                ],
        }
        oops = parsed_oops_to_model_oops(report, 'bug-890001-3')
        self.assertEqual([
            (1, 2, 'foo', 'bar', 'baz'),
            ], oops.statements)

    def test_empty_report_long_id_uses_unknown_bug_889982(self):
        # Some hashes will match the regex that used to extract app server
        # names from oops ids. This is undesirable, because we don't want lots
        # of one-off instance ids. Rather we should use 'unknown' if its
        # unknown.
        report = {
            'id': 'OOPS-68383510f5054932567230492013ce90',
            'reporter': ''
        }
        oops = parsed_oops_to_model_oops(report, 'bug-889982')
        self.assertEqual('UNKNOWN', oops.appinstance.title)

    def test_u1_report_id_bug_891647(self):
        # Ubuntu One web apps use their own flavour of unique identifier for
        # the oopses: prefixZuuid_encoded. We need to make sure that prefix
        # does not end up being such a string.
        report = {
            'id': 'OOPS-2147appserver'\
                  'ZCeCCGJBHEHJCEdABaIIJDCbaJbaAbDce175347', 
        }
        oops = parsed_oops_to_model_oops(report, 'bug-891647')
        self.assertEqual('APPSERVER', oops.appinstance.title)

    def test_long_url_bug_915335(self):
        # URLs that are longer than 500 characters should be truncated
        # at all times.
        url = 'http://' + '\xFF' * 250

        report = {
            'id': 'OOPS-68383510f5054932567230492013ce91',
            'url': url
        }

        oops = parsed_oops_to_model_oops(report, 'bug-915335')
        oops.save()
        self.assertTrue(len(oops.url) < MAX_URL_LEN)

