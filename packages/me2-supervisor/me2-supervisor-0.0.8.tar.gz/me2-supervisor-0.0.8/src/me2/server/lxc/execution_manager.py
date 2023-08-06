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

import logging

from me2.server.execution_manager import ExecutionManagerBase, ContainerSupervisor

from mjsrpc2 import RPCBase, RPCService, UnixSocketConnector, jsonmethod, jsonattribute
from me2.packaging.package import expand_variables

from mako.template import Template
from pkg_resources import ResourceManager

import os
from lockfile import LockFile
import threading
import Queue
import pipes
import subprocess
import time
import sys
import shutil
from threading import ThreadError
import uuid

resource_manager = ResourceManager()

class LXCContainer(RPCBase):
    lxc_config_tmpl = Template(text = resource_manager.resource_string(__name__, "data/templates/lxc_config.mak"))
    lxc_fstab_tmpl = Template(text = resource_manager.resource_string(__name__, "data/templates/lxc_fstab.mak"))
    isStarted = False
    isRunning = False
    isStopped = True

    def __init__(self, context, lxc_manager, basedir, configdir, ident, config):
        super(LXCContainer, self).__init__()
        self.context = context
        self.log = logging.getLogger("LXCContainer").getChild("ident-%s" % ident)
        self._lxc_manager = lxc_manager
        self.basedir = basedir
        self.configdir = configdir
        self.ident = ident
        self.runtime_config = config
        self.rootfs = os.path.join(basedir, "rootfs")
        self.tools_dir = self.rootfs + "/" + expand_variables("${execution.options.tools-dir}", self._lxc_manager.config)
        self.lxc_config_file = os.path.join(self.configdir, "lxc.config")
        self.lxc_fstab_file = os.path.join(self.configdir, "lxc.fstab")
        self.socket_dir = os.path.join(self.configdir, "net")
        self.socket_file = os.path.join(self.socket_dir, "me2-server.sock")
        self.lock = LockFile(os.path.join(self.basedir))
        self.lxc_start_container_command_template = expand_variables("${execution.start-container}", self._lxc_manager.config)
        self.lxc_stop_container_command_template = expand_variables("${execution.stop-container}", self._lxc_manager.config)
        self.lxc_info_container_command_template = expand_variables("${execution.container-info}", self._lxc_manager.config)
        self._rpc_server = None

    def start(self):
        self.log.info("Starting up container")
        self.prepare()
        self._start_rpc_server()
        self._start()

    def _start(self):
        command = self.lxc_start_container_command_template
        command = command % {'container_name': pipes.quote(self.ident),
                             'lxc_config': pipes.quote(self.lxc_config_file)
                             }
        command = self._lxc_manager._elevate(command)
        self.log.debug("Running command: %s", command)
        subprocess.check_call(command, shell = True)
        self.isStarted = True

    def _start_rpc_server(self):
        if self._rpc_server is not None:
            self.log.warn("RPC Server is already started")
            return
        self.log.info("Starting RPC Service. Socket: %s", self.socket_file)
        self._rpc_service = RPCService(self)
        self._rpc_server = UnixSocketConnector(rpc = self._rpc_service, socket_path = self.socket_file)

    def prepare(self):
        self.log.info("Preparing container")
        self.lxc_config()
        self.lxc_fstab()
        self._copy_agent_bundle()

    def _copy_agent_bundle(self):
        try:
            os.makedirs(self.tools_dir)
        except OSError, e:
            pass
        dest_dir = os.path.join(self.tools_dir, "agent.pybundle")
        self.log.info("Copying agent to %s", dest_dir)
        shutil.copyfile(self.context.agent_bundle, dest_dir)

    def lxc_config(self):
        config = {'hostname': self.ident,
                  'rootfs': self.rootfs,
                  'fstab': self.lxc_fstab_file,
                  'agent_bundle': self.context.agent_bundle
                  }
        content = self.lxc_config_tmpl.render(**config)
        self.log.info("Saving LXC Config as: %s", self.lxc_config_file)
        with open(self.lxc_config_file, "w") as f:
            f.write(content)

        if not os.path.exists(self.socket_dir):
            os.makedirs(self.socket_dir, 0755)

    def lxc_fstab(self):
        config = {'rootfs': self.rootfs,
                  'host_mde_socketdir': self.socket_dir,
                  'agent_bundle': self.context.agent_bundle
                  }

        content = self.lxc_fstab_tmpl.render(**config)
        self.log.debug("Saving fstab to %s", self.lxc_fstab_file)
        with open(self.lxc_fstab_file, "w") as f:
            f.write(content)


class LxcExecutionManager(ExecutionManagerBase):
    log = logging.getLogger("LxcExecutionManager")

    def __init__(self, *args, **kw):
        super(LxcExecutionManager, self).__init__(*args, **kw)
        self.registry = ContainerSupervisor() # This should go to execution manager base
        self.lxc_info_container_command_template = expand_variables("${execution.container-info}", self.config)

    @jsonmethod
    @jsonattribute(name = "bottle_dir", kind = str, documentation = "The bottle directory in which the container should be started")
    @jsonattribute(name = "config_dir", kind = str, documentation = "The config directory for the bottle")
    @jsonattribute(name = "ident", kind = str, documentation = "The identifier of the bottle")
    @jsonattribute(name = "config", kind = object, documentation = "The running config")
    def start(self, bottle_dir, config_dir, ident, config):
        with self.lock:
            container = LXCContainer(self.context, self, bottle_dir, config_dir, ident, config)
            container = self.start_container(container)
            self.registry.add(container)
        return container

    @jsonmethod
    @jsonattribute(name = "container_id", kind = str, documentation = "The is of the container that should be stoped")
    def stop(self, container_id):
        with self.lock:
            container = self.registry.get(container_id)
            container.stop()

    @jsonmethod
    @jsonattribute(name = "container_id", kind = str, documentation = "The id of the container")
    def info(self, container_id):
        """Method for checking the status of a container. 
        @return: an dict with the information
        """
        container_id = uuid.UUID(container_id).get_hex()
        with self.lock:
            lxc_info = self.get_lxc_info(container_id)
            managed = False
            try:
                container = self.registry.get(container_id)
                if container:
                    managed = True
            except KeyError:
                pass
            lxc_info['managed'] = managed
            return lxc_info

    @jsonmethod
    def list(self):
        pass


    def start_container(self, container):
        self.log.debug("Starting container")
        container.start()
        return container

    def stop_container(self, container):
        self.log.debug("Stoping container")
        container.stop()
        return container

    def get_lxc_info(self, container_id):
        log = self.log.getChild("get_lxc_info")
        command = self._elevate(self.lxc_info_container_command_template % {'container_name':container_id})
        output = subprocess.check_output(command, shell = True)
        output = output.split("\n")
        output = [line.strip().split(":") for line in output if len(line) > 0]
        output = [line for line in output if len(line) == 2]
        output = [ (name.strip(), value.strip()) for name, value in output]
        output = dict(output)
        log.debug("Got output from lxc list: %s", output)
        running = output["state"] == "RUNNING"

        result = {'running': running}
        if running and 'pid' in output:
            result['pid'] = int(output['pid'])
        return result
