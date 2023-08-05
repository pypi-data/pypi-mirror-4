# Copyright 2011 Canonical Ltd.  All rights reserved.
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

# Delete DB records of OOPSes that have no bug reports for them.

__metaclass__ = type

import datetime
import logging
import optparse
import sys
from textwrap import dedent

from oops_datedir_repo.prune import LaunchpadTracker
from pytz import utc

from oopstools.oops.models import (
    Oops,
    PruneInfo,
    )


def main(argv=None, tracker=LaunchpadTracker, logging=logging):
    """Console script entry point."""
    if argv is None:
        argv = sys.argv
    usage = dedent("""\
        %prog [options]

        The following options must be supplied:
        Either
         --project
        or
         --projectgroup

        e.g.
        %prog --projectgroup launchpad-project

        Will process every member project of launchpad-project.

        When run this program will ask Launchpad for OOPS references made since
        the last date it pruned up to, with an upper limit of one week from
        today. It then looks in the database for all oopses created during that
        date range, and if they are not in the set returned by Launchpad,
        deletes them. If the database has never been pruned before, it will
        pick the earliest date present in the repository as the start date.

        This does not delete OOPS files that are on disk (e.g. created by
        amqp2disk) - a separate pruner is available in oops-datedir-repo that
        should be used to prune them.
        """)
    description = \
        "Delete OOPS reports that are not referenced in a bug tracker."
    parser = optparse.OptionParser(
        description=description, usage=usage)
    parser.add_option('--project',
        help="Launchpad project to find references in.")
    parser.add_option('--projectgroup',
        help="Launchpad project group to find references in.")
    parser.add_option(
        '--lpinstance', help="Launchpad instance to use", default="production")
    options, args = parser.parse_args(argv[1:])
    def needed(*optnames):
        present = set()
        for optname in optnames:
            if getattr(options, optname, None) is not None:
                present.add(optname)
        if not present:
            if len(optnames) == 1:
                raise ValueError('Option "%s" must be supplied' % optname)
            else:
                raise ValueError(
                    'One of options %s must be supplied' % (optnames,))
        elif len(present) != 1:
            raise ValueError(
                    'Only one of options %s can be supplied' % (optnames,))
    needed('project', 'projectgroup')
    logging.basicConfig(
        filename='prune.log', filemode='w', level=logging.DEBUG)
    one_week = datetime.timedelta(weeks=1)
    one_day = datetime.timedelta(days=1)
    # Only prune OOPS reports more than one week old.
    prune_until = datetime.datetime.now(utc) - one_week
    # Ignore OOPS reports we already found references for - older than the last
    # prune date.
    try:
        info = PruneInfo.objects.all()[0]
    except IndexError:
        # Never been pruned.
        try:
            oldest_oops = Oops.objects.order_by('id')[0]
        except IndexError:
            # And has no oopses
            return 0
        info = PruneInfo(pruned_until=oldest_oops.date-one_day)
        info.save()
    prune_from = info.pruned_until
    if prune_from.tzinfo is None:
        # Workaround django tz handling bug:
        # https://code.djangoproject.com/ticket/17062
        prune_from = prune_from.replace(tzinfo=utc)
    # The tracker finds all the references for the selected dates.
    finder = tracker(options)
    references = finder.find_oops_references(
        prune_from, datetime.datetime.now(utc), options.project,
        options.projectgroup)
    # Then we can delete the unreferenced oopses.
    PruneInfo.prune_unreferenced(prune_from, prune_until, references)
    # And finally save the fact we have scanned up to the selected date.
    info.pruned_until = prune_until
    info.save()
    return 0
