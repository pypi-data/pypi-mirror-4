'''
Copyright 2012 Research Institute eAustria

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul <marian@ieat.ro>
@contact: marian@ieat.ro
@copyright: 2012 Research Institute eAustria
'''

import argparse
import logging
import daemon
import os

class PidFileException(Exception):
    pass

class PidfileManager(object):
    def __init__(self, fname):
        self.fname = fname
    def __enter__(self):
        if os.path.exists(self.fname):
            raise PidFileException("Pid file exists")
        self._pidfile = open(self.fname, 'w')
        self._pidfile.write(str(os.getpid()))
        self._pidfile.flush()
    def __exit__(self, type, value, traceback):
        self._pidfile.close()
        os.remove(self.fname)


def main():
    parser = argparse.ArgumentParser(description = 'mOSAIC deployment daemon')
    parser.add_argument('--stdout', '-o', type = str, default = None, help = 'File for storing stdout')
    parser.add_argument('--stderr', '-e', type = str, default = None, help = 'File for storing stderr')
    parser.add_argument('--verbose', '-v', action = 'count', default = 0, help = "The verbosity level. More v's means more logging")
    daemon_group = parser.add_argument_group('Daemon')
    daemon_group.add_argument('--chroot', '-c', type = str, default = None, help = 'Directory where we should chroot')
    daemon_group.add_argument('--workdir', '-w', type = str, default = "/", help = 'Working directory')
    daemon_group.add_argument('--pidfile', '-f', type = str, default = None, help = 'PID File')
    daemon_group.add_argument('--detach', '-d', default = False, action = 'store_true', help = 'Daemonize')
    daemon_group.add_argument('--logfile', '-l', type = str, default = None, help = 'File for storing log output (defaults to --stderr)')
    daemon_group.add_argument('--config-file', type = str, default = None, help = 'Configuration file (JSON)')

    app_group = parser.add_argument_group('Application')
    unix_group = parser.add_argument_group('Unix Domain Socket Server')
    tcp_group = parser.add_argument_group('TCP Server')
    agent_group = parser.add_argument_group('Agent')

    app_group.add_argument("--application", "-a", type = str, default = [], action = 'append', help = 'Enable an internal application')
    #app_group.add_argument("--noapi", default = False, action = 'store_true', help = 'Disable API server')
    app_group.add_argument("--enable-unix-server", '-u', action = 'store_true', default = False, help = 'Enable the unix socket server')
    unix_group.add_argument("--unix-socket", '-s', type = str, default = os.path.join(os.path.expanduser("~"), '.mde.socket'), help = 'The UNIX socket that should be used')
    app_group.add_argument("--enable-tcp-server", '-t', action = 'store_true', default = False, help = 'Enable TCP server')
    tcp_group.add_argument("--bind", '-b', type = str, default = '127.0.0.1', help = 'The address to bind to')
    tcp_group.add_argument("--port", '-p', type = str, default = '8099', help = 'The port to bind to')

    agent_group.add_argument('--agent-bundle', type = str, default = None, help = 'The agent bundle')


    args = parser.parse_args()

    # Setup logging
    if args.verbose > 4:
        log_level = 10
    else:
        log_level = 50 - args.verbose * 10

    logging.basicConfig(format = '[ %(levelname)-8s %(filename)s:%(lineno)d (%(name)s) ] --> %(message)s',
                        datefmt = '%d/%b/%Y %H:%M:%S',
                        level = log_level)


    from me2.server import daemon as mde_daemon

    context = daemon.DaemonContext()
    context.chroot_directory = args.chroot
    context.working_directory = args.workdir

    if args.pidfile is not None:
        context.pidfile = PidfileManager(args.pidfile)
    context.detach_process = args.detach

    if args.stdout is not None:
        context.stdout = open(args.stdout, 'w+')

    if args.stderr is not None:
        context.stderr = open(args.stderr, 'w+')
    elif context.stdout is not None:
        context.stderr = open(args.stdout, 'w+')


    context.application = args.application
    #context.noapi = args.noapi
    context.enable_unix_server = args.enable_unix_server
    context.unix_socket = args.unix_socket
    context.enable_tcp_server = args.enable_tcp_server
    context.tcp_bind = args.bind
    context.tcp_port = args.port
    if args.config_file:
        context.config_file = os.path.abspath(args.config_file)
    else:
        context.config_file = None

    context.agent_bundle = args.agent_bundle


    with context:
        if args.logfile is None:
            if args.stderr is not None:
                context.logfile = args.stderr
            elif args.stdout is not None:
                context.logfile = args.stdout
            else:
                context.logfile = "/dev/null" # Platform specific
        else:
            context.logfile = args.logfile

        logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)s %(threadName)-10s %(name)-16s %(levelname)-8s %(message)s',
                    datefmt = '%m-%d %H:%M',
                    filename = context.logfile,
                    filemode = 'w+'
                    )
        mde_daemon.main(context)

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
    main()
