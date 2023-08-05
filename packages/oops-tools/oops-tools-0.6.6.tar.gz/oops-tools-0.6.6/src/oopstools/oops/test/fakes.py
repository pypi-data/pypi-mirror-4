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

import tarfile
import tempfile
import os

from bzrlib.branch import Branch

LPLIB_ROOT="https://api.edge.launchpad.net/beta"


class SampleBranch:
    """Convenience class to untar the sample data branch."""

    # XXX: fix this hardcoded path
    TEST_DATA = "tests/sample_data/branch_data.tar.bz2"

    def __init__(self):
        tar_file = tarfile.open(self.TEST_DATA)
        tmp_dir = tempfile.mkdtemp()
        tar_file.extractall(tmp_dir)
        self.path = tmp_dir
        self.branch_name = 'devel'
        self.branch_path = os.path.join(tmp_dir, self.branch_name)
        self.branch = None

    def open_branch(self):
        self.branch = Branch.open(self.branch_path)
        return self.branch


class FakeBug:

    def __init__(self, bug_id):
        self.id = bug_id
        self.title = ""
        self.bug_tasks = []
        self.messages = []
        self.self_link = "%s/bugs/%s" % (LPLIB_ROOT, bug_id)

    def addBugTask(self, bug_id, target_name, status):
        bug_task = FakeBugTask(bug_id, target_name, status)
        bug_task.bug = self
        bug_task.addTarget(target_name)
        self.bug_tasks.append(bug_task)

    def newMessage(self, subject, content):
        self.messages.append((subject, content))

    def lp_save(self):
        pass


class FakeBugTask:

    def __init__(self, bug_id, target_name, status=u"Fix Committed"):
        self._bug_id = bug_id
        self.bug = None
        self.bug_target_name = target_name
        self.status = status
        self.assignee = None
        self.target = None
        self.milestone = None
        self.tags = []
        self.self_link = "%s/%s/+bug/%s" % (LPLIB_ROOT, target_name, bug_id)

    def addTarget(self, target_name):
        self.target = FakeTarget(target_name)

    def transitionToAssignee(self, assignee):
        self.assignee = assignee

    def transitionToMilestone(self, milestone):
        self.milestone = milestone


class FakeTarget:

    def __init__(self, target_name):
        self.self_link = "%s/%s" % (LPLIB_ROOT, target_name)


class FakePeople:

    def __init__(self):
        self._people = {}

    def getByEmail(self, email):
        try:
            person = self._people[email]
            return person
        except:
            return None


class FakePerson:

    def __init__(self, name, display_name, email):
        self.name = name
        self.display_name = display_name
        self.preferred_email = email
        self.self_link = "%s/~%s" % (LPLIB_ROOT, name)


class FakeBranches:

    def __init__(self):
        self._branches = {}

    def getByUrl(self, url):
        try:
            branch = self._branches[url]
            return branch
        except:
            return None


class FakeBranch:

    def __init__(self, branch_nick, owner, project, linked_bugs):
        self.owner = owner
        self.url = "lp:%s/%s/%s" % (owner.name, project, branch_nick)
        self.project = project
        self.linked_bugs = linked_bugs
        self.properties = {}
        self.properties["branch-nick"] = branch_nick


class FakeMilestone:

    def __init__(self, milestone_name, target, active=True):
        self.name = milestone_name
        self.target = target
        self.is_active = active


class FakeProject:

    def __init__(self, project_name, milestone=None):
        self.name = project_name
        self.milestone = milestone
        self.self_link = "%s/%s" % (LPLIB_ROOT, project_name)

    def getMilestone(self, name):
        return FakeMilestone(name, self, True)


class FakeLP:

    def __init__(self):
        self.people = FakePeople()
        self.bugs = {}
        self.branches = FakeBranches()
        self.projects = {}

    def createBugWithBugTask(self, bug_id, target_name, status):
        fake_bug = FakeBug(bug_id)
        fake_bug.addBugTask(bug_id, target_name, status)
        self.bugs[bug_id] = fake_bug
        return fake_bug

    def createPerson(self, name, display_name, email):
        fake_person = FakePerson(name, display_name, email)
        self.people._people[email] = fake_person
        return fake_person

    def createBranch(self, branch_nick, owner, project, linked_bugs):
        fake_branch = FakeBranch(branch_nick, owner, project, linked_bugs)
        self.branches._branches[fake_branch.url] = fake_branch
        return fake_branch

    def createProject(self, name):
        fake_project = FakeProject(name)
        self.projects[name] = fake_project
        return fake_project
