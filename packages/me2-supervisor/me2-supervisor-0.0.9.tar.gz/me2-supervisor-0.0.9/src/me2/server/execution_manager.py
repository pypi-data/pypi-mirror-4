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
import time
from mjsrpc2 import RPCBase, jsonmethod, jsonattribute

from me2.packaging.package import expand_variables

class ContainerSupervisor(threading.Thread, RPCBase):
    log = logging.getLogger("ContainerSupervisor")
    _supervisor_started = False

    def __init__(self):
        threading.Thread.__init__(self)
        RPCBase.__init__(self)
        self.lock = threading.Lock()
        self.map = {}
        self.setDaemon(True)
        self.start()

    def run(self):
        with self.lock:
            if self._supervisor_started:
                self.log.warn("Thread already started")
                return

        self.log.critical("FIXME!!!! Started dummy container supervisor")
        while True:
            time.sleep(1)
            pass


    def add(self, container):
        with self.lock:
            self.log.debug("Registering %s", container.ident)
            if container.ident in self.map:
                raise ValueError("Container already registered!")
            self.map[container.ident] = container
            method_name = "ns_%s" % container.ident
            self.add_method(method_name, container)

    def remove(self, container):
        with self.lock:
            self.log.debug("UnRegistering %s", container.ident)
            return self.map.pop(container.ident)

    def get(self, container_ident):
        with self.lock:
            if container_ident in self.map:
                self.log.error("Container with id=%s is registered!", container_ident)
                return self.map[container_ident]
            else:
                self.log.error("Container with id=%s is NOT registered!", container_ident)
                raise KeyError("Container with id=%s is NOT registered!" % container_ident)

class ExecutionManagerBase(RPCBase):
    log = logging.getLogger("ExecutionManagerBase")
    lock = threading.Lock()
    def __init__(self, context, manager, config):
        super(ExecutionManagerBase, self).__init__()
        self.context = context
        self._manager = manager
        self.config = config
        self._elevate_command = expand_variables("${elevate-privileges}", self.config)

    def _elevate(self, command):
        return self._elevate_command % {'command': command}

    @jsonmethod
    @jsonattribute(name = "bottle_dir", kind = str, documentation = "The bottle directory in which the container should be started")
    @jsonattribute(name = "config_dir", kind = str, documentation = "The config directory for the bottle")
    @jsonattribute(name = "ident", kind = str, documentation = "The identifier of the bottle")
    @jsonattribute(name = "config", kind = object, documentation = "The running config")
    def start(self, bottle_dir, config_dir, ident, config):
        raise NotImplementedError()




