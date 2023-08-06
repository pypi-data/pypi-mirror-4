#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 Rodolphe Quiédeville <rodolphe@quiedeville.org>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
tsung2graphite.py reads tsung's log in json format, export datas to graphite
server.
Your tsung scenario must begin with option backend="json" to force
tsung dumping log data in json format instead of tsung native format :

<tsung loglevel="notice" dumptraffic="false" version="1.0" backend="json">

"""
import sys
import os
from optparse import OptionParser
import json
from socket import socket
from time import sleep

__version__ = "0.4.0"


def arg_parse():
    """ Parse command line arguments """
    arg_list = "-i FILENAME -t TARGETNAME -s GRAPHITE_SERVER [-vh]"
    usage = "Usage: %prog " + arg_list
    parser = OptionParser(usage, version=__version__)
    parser.add_option("-c", "--cycle", dest="cycle",
                      action="store_true",
                      help="run in cycle mode",
                      default=False)
    parser.add_option("-n", "--nb-cycle", dest="nb_cycle",
                      action="store",
                      type=int,
                      help="number of cycle",
                      default=10)
    parser.add_option("-t", "--target", dest="target",
                      help="target name",
                      default=None)
    parser.add_option("-i", "--infile", dest="infile",
                      help="input file",
                      default=None)
    parser.add_option("-s", "--server", dest="hostname",
                      help="graphite hostname",
                      default="localhost")
    parser.add_option("-p", "--port", dest="port",
                      help="graphite port",
                      default=2003)
    parser.add_option("--sleep-time", dest="sleep",
                      type=int,
                      help="sleep time in secondes between cycle",
                      default=30)
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="store_true",
                      help="be verbose",
                      default=False)

    return parser.parse_args()[0]


def check_options(options):
    """Check mandatory options"""
    if options.infile is None:
        print """Input file or url is required, use -i or -u on command line"""
        sys.exit(1)

    if options.target is None:
        print """Target name required, use -t or --target"""
        sys.exit(1)


def parse_file(fpath):
    """
    Parse the content of a requirements.txt

    Parameters:
     - fpath (string): filepath containing tsung log

    Return a json object
    """
    content = open(fpath, 'r').read()
    try:
        datas = json.loads(content)
    except:
        # when tsung is running the log file does not contains valid json
        datas = json.loads("%s]}]}" % content)

    return datas


def prepare_datas(datas, target):
    """
    Prepare datas to be pushed

    Parameters:
     - datas (array)
     - target (string) : graphite target name
    datas : json
    """
    blob = []
    stats = datas['stats']

    i = 0
    nbd = len(stats)

    while i < nbd:
        if 'samples' in stats[i]:
            for value in stats[i]['samples']:
                for elem in value:
                    if elem != 'name':
                        blob.append(append_data(target, value, stats[i], elem))
        i = i + 1

    return blob


def append_data(target, value, stat, dname):
    """

    Parameters:
     - target (string)
     - value (array)
     - stat (json)
     - dname (string)

    return : string
    """
    line = "%s.tsung.%s.%s %s %s\n" % (target,
                                       value['name'],
                                       dname,
                                       value[dname],
                                       stat['timestamp'])
    return line


def send_graphite(datas, carbon_server, carbon_port, verbose):
    """
    send datas to graphite server

    Parameters :
     - verbose (boolean)
    """
    blocksize = 60
    nb_blocks = 0
    blob = ''
    for data in datas:
        blob = blob + data

        if nb_blocks == blocksize:
            sendg(carbon_server, carbon_port, blob, verbose)
            nb_blocks = 0
            blob = ''
        nb_blocks = nb_blocks + 1

    if nb_blocks > 0:
        sendg(carbon_server, carbon_port, blob, verbose)

    # clean stdout
    if verbose:
        print ''

    return len(datas)


def sendg(carbon_server, carbon_port, data, verbose):
    sock = socket()
    try:
        sock.connect((carbon_server, carbon_port))
    except:
        print "Couldn't connect to %s on port %d" % (carbon_server,
                                                     carbon_port)
        sys.exit(1)

    sock.sendall(data)
    sock.close()
    if verbose:
        sys.stdout.write('.')
        sys.stdout.flush()


def manage(datas):
    """
    Find start and stop timestamp
    """

    start = datas['stats'][0]['timestamp']
    stop = datas['stats'][-1]['timestamp']
    return start, stop


def process(options):
    if options.infile is not None:
        if not os.path.exists(options.infile):
            sys.exit(1)
        else:
            # parse file and return nodes
            datas = parse_file(options.infile)

    jsond = parse_file(options.infile)
    start, stop = manage(jsond)
    datas = prepare_datas(jsond, options.target)

    if len(datas) > 0:
        nb_data = send_graphite(datas,
                                options.hostname,
                                options.port,
                                options.verbose)

    print "Pushed %d datas to graphite server" % nb_data
    print "./manage create_update_bench start=%d stop=%d target=%s" % (start, stop, options.target)

def main():
    """Main programm"""
    options = arg_parse()
    check_options(options)

    if options.cycle:
        cyc = 0
        while cyc < options.nb_cycle:
            print "Cycle %d/%d with sleep time %d" % (cyc + 1,
                                                      options.nb_cycle,
                                                      options.sleep)
            process(options)
            sleep(options.sleep)
            cyc += 1
    else:
        process(options)


if __name__ == '__main__':
    main()
