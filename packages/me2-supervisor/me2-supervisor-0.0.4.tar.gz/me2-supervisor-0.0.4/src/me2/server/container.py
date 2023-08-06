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

import os
import logging
import json
import threading
import shutil
import time


from mjsrpc2 import RPCBase, jsonmethod, jsonattribute

from me2.server.storage_manager import BtrfsStorageManager
from me2.server.lxc.execution_manager import LxcExecutionManager
from me2.server.bundle_manager import BundleManager

from mako.template import Template
from pkg_resources import ResourceManager

resource_manager = ResourceManager()

class ContainerManager(RPCBase):
    log = logging.getLogger("ContainerManager")
    def __init__(self, context, config):
        RPCBase.__init__(self)
        self.context = context
        self.btrfs = BtrfsStorageManager(context, manager = self, config = config)
        self.lxc = LxcExecutionManager(context, manager = self, config = config)
        self.bundle = BundleManager(context, manager = self, config = config.get("bundles"), storage_manager = self.btrfs)
        self.config = config
        self.package_install_init = Template(text = resource_manager.resource_string(__name__, "data/package_install_init.mak"))
        self.lock = threading.Lock()

    @jsonmethod
    @jsonattribute(name = "bundle_id", kind = str, documentation = "the bundle that should be started")
    @jsonattribute(name = "config", kind = object, documentation = "instance configuration json")
    def start(self, bundle_id, config):
        with self.lock:
            base_bottles = self.btrfs.list_base_bottles()
            if not bundle_id in base_bottles['result']:
                self.bundle.import_bundle(bundle_specification = bundle_id)
            bottle = self.btrfs.clone(base = bundle_id)
            self.log.info("Bottle: %s", bottle)
            container = self.lxc.start(bottle_dir = bottle['path'], config_dir = bottle['configdir'], ident = bottle['uuid'], config = config)
            print container

    @jsonmethod
    @jsonattribute(name = "base_bundle", type = str)
    @jsonattribute(name = "new_bundle", type = str)
    @jsonattribute(name = "packages", type = object)
    @jsonattribute(name = "timeout", kind = int)
    def prepare_bundle(self, base_bundle, new_bundle, packages, timeout):
        base_bottles = self.btrfs.list_base_bottles()
        if not base_bundle in base_bottles['result']:
            self.bundle.import_bundle(bundle_specification = base_bundle)
        bottle = self.btrfs.clone(base = base_bundle)
        init_location = os.path.join(bottle["rootfs"], "sbin", "init")
        init_backup_location = os.path.join(bottle["rootfs"], "sbin", "init.old")
        shutil.move(init_location, init_backup_location)

        if isinstance(packages, basestring):
            packages = packages.split(",")
        content = self.package_install_init.render(packages = packages)
        with open(init_location, "w") as f:
            f.write(content)
        os.chmod(init_location, 755)
        container = self.lxc.start(bottle_dir = bottle['path'], config_dir = bottle['configdir'], ident = bottle['uuid'], config = {})
        start_time = time.time()
        state_file = os.path.join(container.rootfs, 'tmp', 'me2-package-install-state')
        state = None
        self.log.info('Waiting for package install to finish')
        self.log.debug("Timeout is %d", timeout)
        if timeout is None:
            timeout = 600

        while time.time() - start_time < timeout:
            if os.path.exists(state_file):
                state = int(open(state_file).read())
                break
            time.sleep(0.1)

        if state is None:
            self.log.critical("Packages could not be instaled.")
            raise Exception("Could not install packages (maybe an timeout ?)")

        if state == 1:
            self.log.critical("Failed to install packages")
            raise Exception("Package manager failed to install the packages")




class Deployer(RPCBase):
    log = logging.getLogger("Deployer")
    def __init__(self, context, config_file = None):
        RPCBase.__init__(self)
        self.context = context
        if config_file is None:
            self.log.info("No config file provided")
            config = {}
        else:
            self.log.debug("Loading config from %s", config_file)
            config = json.load(open(config_file))
        deployer_config = config.get("deployer", {})
        container_manager_config = deployer_config.get("container-manager", {})
        self.add_method('manager', ContainerManager(context, config = container_manager_config))
