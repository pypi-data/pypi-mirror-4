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

import threading
import logging
import sys
import os

from mjsrpc2 import RPCService, UnixSocketConnector

from me2.server.container import Deployer
from me2.common.util import QueuePair


class DaemonManager(threading.Thread):
    log = logging.getLogger("DaemonManager")
    def __init__(self, context):
        threading.Thread.__init__(self)
        self.context = context
        self.command_queue = QueuePair()
        self.deployer = Deployer(context = context, config_file = context.config_file)
        self.deployer_rpc = RPCService(self.deployer)

    def run(self):
        # Wait for incomming messages on command queue
        # The messages should be of the following form
        # {'command': '', **}
        self.log.info("Waiting for commands")
        context = self.context
        apps = context.application[:]

        self.start_connectors()
        self.start_apps(apps)

        while True:
            msg = self.command_queue.get(block = True)
            self.log.debug("Received command: %s", msg)
            if msg['command'] == 'shutdown':
                self.shutdown()
                break

    def start_apps(self, apps):
        pass

    def start_connectors(self):
        context = self.context
        if context.enable_unix_server:
            socketPath = context.unix_socket
            self.log.info("Starting UNIX Domain Socket Server on %s", socketPath)
            if os.path.exists(socketPath):
                self.log.error("Socket %s exists. It will be removed if possible", socketPath)
                os.remove(socketPath)
                self.log.debug("Socket %s was removed", socketPath)
            unix_connector = UnixSocketConnector(self.deployer_rpc, socketPath)
            unix_connector.setDaemon(True)
            unix_connector.start()
        if context.enable_tcp_server:
            self.log.info("Starting HTTP Server on %s:%s", self.context.tcp_bind, self.context.tcp_port)
            from me2.server.web import server
            from jsonrpc2 import JsonRpcApplication
#            app = JsonRpcApplication()
#            app.rpc = self.deployer_rpc
            app = JsonRpcApplication()
            app.rpc = self.deployer_rpc
            server.start_server(self.context.tcp_bind, self.context.tcp_port, self.deployer, app)
            self.log.info("HTTP Monster started!")

    def shutdown(self):
        pass


def main(context):
    manager = DaemonManager(context)
    logging.debug("Starting daemon manager")
    manager.setDaemon(True)
    manager.start()
    while True:
        try:
            if not manager.is_alive():
                break
            manager.join(timeout = 0.10)
        except KeyboardInterrupt:
            logging.critical("KeyboardInterrupt cought. Exiting!")
            sys.exit(1)
        except Exception:
            logging.exception("Cought exception")

