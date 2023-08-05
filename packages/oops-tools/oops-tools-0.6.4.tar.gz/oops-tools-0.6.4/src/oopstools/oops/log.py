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


import os
import logging
import logging.handlers

from django.conf import settings


LOG_DIR = os.path.join(settings.ROOT, 'logs')
if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)


def get_logger(name, filename):
    """Returns a logger object set up to use a file and console."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    log_filename = os.path.join(LOG_DIR, filename)
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename, maxBytes=200000, backupCount=5)
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


def remove_console_handler(logger):
    """Remove the console logger so it can be used in tests."""
    handlers = logger.handlers[:]
    for handler in handlers:
        # RotatingFileHandler is a subclass of StreamHandler that's why this
        # can't be written in the form:
        # isinstance(handler, logging.StreamHandler) or we'll end up with no
        # handlers in logger.handlers.
        if not isinstance(handler, logging.handlers.RotatingFileHandler):
            logger.removeHandler(handler)
