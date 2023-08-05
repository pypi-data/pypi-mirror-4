#!/usr/bin/env python
#
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


import datetime

from oopstools.oops.dboopsloader import logger, OopsLoader
from oopstools.oops.models import Oops


def main():
    oops_store = OopsLoader()
    count = 0
    now = datetime.datetime.now()
    # For the start_date, we only care about the date, not the time.
    start_date = now.date() - datetime.timedelta(days=7)
    end_run = now + datetime.timedelta(minutes=5)
    for oops in oops_store.find_oopses(start_date):
        assert isinstance(oops, Oops)
        logger.info("Loaded %s into the database.", oops.oopsid)
        count += 1
        if datetime.datetime.now() > end_run:
            break
    logger.info("Loaded %d OOPS into the database.", count)
