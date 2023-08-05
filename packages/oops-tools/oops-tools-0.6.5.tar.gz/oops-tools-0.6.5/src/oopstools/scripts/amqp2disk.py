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

# Receive OOPS reports from AMQP and publish them into the oops-tools
# repository.

__metaclass__ = type

from functools import partial
import sys
import optparse
from textwrap import dedent

import amqplib.client_0_8 as amqp
from oops import Config
import oops_amqp
import oops_datedir_repo

from oopstools.oops.models import (
    Oops,
    parsed_oops_to_model_oops,
    )


def main(argv=None):
    if argv is None:
        argv=sys.argv
    usage = dedent("""\
        %prog [options]

        The following options must be supplied:
         --output
         --host
         --username
         --password
         --vhost
         --queue

        e.g.
        amqp2disk --output /srv/oops-tools/amqpoopses --host "localhost:3472" \\
            --username "guest" --password "guest" --vhost "/" --queue "oops"

        The AMQP environment should be setup in advance with a persistent queue
        bound to your exchange : using transient queues would allow OOPSes to
        be lost if the amqp2disk process were to be shutdown for a non-trivial
        duration. The --bind-to option will cause the queue (and exchange if
        necessary) to be created and bound together. This is only needed the
        first time as it is created persistently. Running it when the exchange
        already exists (to setup a second worker, or because you manually
        created it with a different setup) is fine. The default setup is a
        fanout exchange.
        """)
    description = "Load OOPS reports into oops-tools from AMQP."
    parser = optparse.OptionParser(
        description=description, usage=usage)
    parser.add_option('--output', help="Root directory to store OOPSes in.")
    parser.add_option('--host', help="AQMP host / host:port.")
    parser.add_option('--username', help="AQMP username.")
    parser.add_option('--password', help="AQMP password.")
    parser.add_option('--vhost', help="AMQP vhost.")
    parser.add_option('--queue', help="AMQP queue name.")
    parser.add_option(
        '--bind-to', help="AMQP exchange to bind to (only needed once).")
    parser.add_option("-v", "--verbose", action="store_true",
        help="Print more information about what is going on.")
    options, args = parser.parse_args(argv[1:])
    def needed(optname):
        if getattr(options, optname, None) is None:
            raise ValueError('option "%s" must be supplied' % optname)
    needed('host')
    needed('output')
    needed('username')
    needed('password')
    needed('vhost')
    needed('queue')
    factory = partial(
        amqp.Connection, host=options.host, userid=options.username,
        password=options.password, virtual_host=options.vhost)
    if options.bind_to:
        connection = factory()
        try:
            channel = connection.channel()
            try:
                channel.exchange_declare(
                    options.bind_to, type="fanout", durable=True, auto_delete=False)
                channel.queue_declare(
                    options.queue, durable=True, auto_delete=False)
                channel.queue_bind(options.queue, options.bind_to)
            finally:
                channel.close()
        finally:
            connection.close()
    config = make_amqp_config(options.output)
    if options.verbose:
        def print_oops(report):
            print ("Received %s" % report['id'])
            sys.stdout.flush()
        config.publishers.append(print_oops)
    receiver = oops_amqp.Receiver(config, factory, options.queue)
    try:
        receiver.run_forever()
    except KeyboardInterrupt:
        pass


def db_publisher(report):
    """Publish OOPS reports to the oops-tools django store."""
    # the first publisher will either inherit or assign, so this should be
    # impossible.
    assert report['id'] is not None
    # Some fallback methods could lead to duplicate paths into the DB: exit
    # early if the OOPS is already loaded.
    try:
        res = Oops.objects.get(oopsid__exact=report['id'])
    except Oops.DoesNotExist:
        oops_path = report['datedir_repo_filepath']
        try:
            res = parsed_oops_to_model_oops(report, oops_path)
            return res.oopsid
        except:
            sys.stderr.write('Failed while processing %s\n' % oops_path)
            raise
    return None


def make_amqp_config(output_dir):
    """Create an OOPS Config for republishing amqp OOPSes.

    An OOPS published to this config will be written to disk and then loaded
    into the database.

    :param output_dir: The directory to write OOPSes too.
    """
    config = Config()
    disk_publisher = oops_datedir_repo.DateDirRepo(
        output_dir, inherit_id=True, stash_path=True)
    config.publishers.append(disk_publisher.publish)
    config.publishers.append(db_publisher)
    return config
