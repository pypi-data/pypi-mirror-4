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
import uuid
import logging
import shutil
import pipes
import subprocess
import grp
import pwd

from mjsrpc2 import RPCBase, jsonmethod, jsonattribute

from me2.server.util import OperationResult, ContainerManagerException
from me2.packaging.package import expand_variables

class ContainerBottle(object):
    uuid = None
    path = None
    rootfs = None
    configdir = None

class StorageManagerException(ContainerManagerException, IOError):
    pass

class StorageManagerBase(RPCBase):
    log = logging.getLogger("StorageManagerBase")
    def __init__(self, context, manager, config):
        RPCBase.__init__(self)
        self.config = config
        self._manager = manager
        self._elevate_command = expand_variables("${elevate-privileges}", self.config, default = "")
        self.root_directory = expand_variables("${storage.root-directory}", config)
        if not os.path.exists(self.root_directory): self.create_subvolume(self.root_directory)
        base_directory = config.get("base-directory", "base")
        self.base_directory = os.path.join(self.root_directory, base_directory)
        if not os.path.exists(self.base_directory): self.create_subvolume(self.base_directory)
        instances_directory = config.get("instances-directory", 'instances')
        self.instances_directory = os.path.join(self.root_directory, instances_directory)
        if not os.path.exists(self.instances_directory): self.create_subvolume(self.instances_directory)
        self.log.debug("Root-directory: %s", self.root_directory)
        self.log.debug("Base-directory: %s", self.base_directory)
        self.log.debug("Instances directory: %s", self.instances_directory)

    def isbottle(self, directory):
        log = self.log.getChild("isbottle")
        if not os.path.exists(directory):
            log.info("Directory %s does not exist", directory)
            return False
        config_dir = os.path.join(directory, "config")
        if not os.path.exists(config_dir):
            log.info("Config directory %s is missing", config_dir)
            return False
        rootfs_dir = os.path.join(directory, "rootfs")
        if not os.path.exists(rootfs_dir):
            log.info("Rootfs directory %s is missing")
            return False
        try:
            uuid.UUID(os.path.basename(directory))
        except ValueError:
            log.exception("Invalid identifier for directory")
            return False

        parent_link = os.path.join(directory, "base")
        if not os.path.exists(parent_link): return False
        return True

    @jsonmethod
    @jsonattribute(name = "name", kind = str)
    def create_base_bottle(self, name):
        self.log.debug("Creating bottle %s", name)
        bottle_location = self._build_bottle_path(name)
        self.log.info("Creating new bottle in %s", bottle_location)
        if self.exists(name = name):
            self.log.warn("Bottle %s already exists!", name)
            return bottle_location
        try:
            self.create_subvolume(bottle_location)
        except:
            self.log.exception("Failed to create bottle %s cleaning up", name)
            self.delete_subvolume(bottle_location)
            raise # Rethrow the exception
        return bottle_location


    def promote_bottle(self, new_name, source):
        pass

    def _build_bottle_path(self, name):
        return os.path.join(self.base_directory, pipes.quote(name))

    @jsonmethod
    @jsonattribute(name = "name")
    def exists(self, name):
        path = self._build_bottle_path(name)
        if os.path.exists(path):
            return True
        else: # ToDo: really check that the file does not exist as os.path.exists return false if it can stat the path
            return False

    @jsonmethod
    def list_base_bottles(self):
        result = OperationResult()
        bottles = []
        status = False
        try:
            bottles = os.listdir(self.base_directory)
        finally:
            result.status = status
            result.result = bottles
        return vars(result)

    @jsonmethod
    def list_bottles(self):
        log = self.log.getChild("list_bottles")
        manager = self._manager
        lxc_manager = manager.lxc
        print dir(lxc_manager)
        print self.config
        response = OperationResult()
        bottle_names = [ subdir for subdir in os.listdir(self.instances_directory) if self.isbottle(os.path.join(self.instances_directory, subdir))]
        bottles = []
        for name in bottle_names[:]:
            bottle = {}
            bottle["uuid"] = str(uuid.UUID(name))
            base = os.path.basename(os.path.realpath(os.path.join(self.instances_directory, name, "base")))
            bottle["base-bottle"] = base
            bottles.append(bottle)
        response.status = True
        response.result = bottles
        return vars(response)

    @jsonmethod
    @jsonattribute(name = "base")
    def clone(self, base, bottle_id = None):
        bottle = ContainerBottle()
        if bottle_id is None:
            bottle_id = uuid.uuid4().get_hex()

        bottle.uuid = bottle_id
        clone_path = os.path.join(self.instances_directory, bottle_id)
        if os.path.exists(clone_path):
            raise StorageManagerException("Bottle already exists")
        bottle.path = clone_path
        bottle.rootfs = os.path.join(bottle.path, "rootfs")
        bottle.configdir = os.path.join(bottle.path, "config")

        base_container_path = os.path.join(self.base_directory, base)
        self.log.debug("Creating a new bottle in %s", bottle.path)
        self.create_snapshot(base_container_path, bottle.path)
        os.symlink(base_container_path, os.path.join(bottle.path, "base"))
        os.makedirs(bottle.configdir, mode = 0755)
        self.log.debug("Bottle dict: %s", vars(bottle))
        return vars(bottle)

    @jsonmethod
    @jsonattribute(name = "bottle_id", kind = str)
    def remove(self, bottle_id):
        hex_id = uuid.UUID(bottle_id).get_hex()
        bottle_path = os.path.join(self.instances_directory, hex_id)
        try:
            assert self.isbottle(bottle_path)
            self.delete_snapshot(bottle_path)
            if os.path.exists(bottle_path):
                shutil.rmtree(bottle_path)
        except:
            self.log.exception("Exception trying to remove bottle %s" % bottle_id)
            return False
        return True

    @jsonmethod
    @jsonattribute(name = "name")
    def remove_base_bottle(self, name):
        path = self._build_bottle_path(name)
        self.delete_subvolume(path)

    def create_snapshot(self, source, destination):
        """Creates a snapshot of source in destination
        
        @param source: The source that should be snapshot
        @param destination: The directory where the snapshot should go
        """
        raise NotImplementedError()

    def delete_snapshot(self, path):
        """Deletes a snapshot
        
        @param path: The path to the snapshot
        """
        raise NotImplementedError()

    def _elevate(self, command):
        return self._elevate_command % {'command': command}


    def create_subvolume(self, path):
        raise NotImplementedError()

    def delete_subvolume(self, path):
        raise NotImplementedError()

class BtrfsStorageManager(StorageManagerBase):
    log = logging.getLogger("BtrfsStorageManager")
    def __init__(self, *args, **kw):
        StorageManagerBase.__init__(self, *args, **kw)

    def set_permission(self, path, perms):
        if not os.path.abspath(path).startswith(self.root_directory):
            raise StorageManagerException("Path (%s) is not within me2 root directory", self.root_directory)
        command_template = expand_variables("${storage.chmod-command}", self.config)
        command = command_template % {"permissions": perms,
                                      "path": pipes.quote(path)}
        command = self._elevate(command)
        subprocess.check_call(command, shell = True)

    def set_owner(self, path, user):
        uid = pwd.getpwnam(user)[2]
        self._set_owner_uid(path, uid)
        raise NotImplementedError()

    def _set_owner_uid(self, path, uid):
        command_template = None
        raise NotImplementedError()

    def set_group(self, path, group):
        gid = grp.getgrnam(group)
        self._set_group_uid(path, gid)
        raise NotImplementedError()

    def _set_group_uid(self, path, gid):
        command = None
        raise NotImplementedError()

    def create_subvolume(self, path):
        path = os.path.abspath(path)
        if not path.startswith(self.root_directory):
            raise StorageManagerException("Path (%s) is not within me2 root directory", self.root_directory)
        if os.path.lexists(path):
            raise StorageManagerException("Subvolume already exists")

        self.log.debug("Creating a new subvolume in %s", path)
        volume_name = os.path.basename(path)
        directory_name = os.path.dirname(path)
        command_template = expand_variables("${storage.create-volume}", self.config)
        command = command_template % {'destination_path': pipes.quote(directory_name),
                                      'subvolume_name': pipes.quote(volume_name)}
        command = self._elevate(command)
        subprocess.check_call(command, shell = True)
        self.set_permission(path, expand_variables("${storage.volume-permissions}", self.config))

    def delete_subvolume(self, path):
        self.log.debug("Delete-ing subvolume %s", path)
        path = os.path.abspath(path)
        if not path.startswith(self.root_directory):
            raise StorageManagerException("Path is not within root directory")
        command_template = expand_variables("${storage.delete-volume}", self.config)
        command = command_template % {"subvolume_path": path}
        command = self._elevate(command)
        subprocess.check_call(command, shell = True)

    def create_snapshot(self, source, destination):
        self.log.debug("Creating BTRFS snapshot from %s to %s", source, destination)
        command = self.config.get('storage', {}).get("create-snapshot") % {'source_path': pipes.quote(source),
                                                                           'destination_path': pipes.quote(destination)}
        elevate_privileges = self.config.get('elevate-privileges', None)
        if elevate_privileges:
            command = elevate_privileges % {"command": command}
        self.log.debug("Command to be executed: %s", command)
        subprocess.check_call(command, shell = True)
        self.set_permission(pipes.quote(destination), expand_variables("${storage.volume-permissions}", self.config))

    def delete_snapshot(self, path):
        #ToDo: I should check that the absolute path is inside the base directory
        self.log.debug("Deleting BTRFS snapshot from %s", path)
        command = self.config.get('storage', {}).get('delete-snapshot') % {'path': pipes.quote(path)}
        elevate_privileges = self.config.get('elevate-privileges', None)
        if elevate_privileges:
            command = elevate_privileges % {"command": command}
        self.log.debug("Command to be executed: %s", command)
        subprocess.check_call(command, shell = True)
