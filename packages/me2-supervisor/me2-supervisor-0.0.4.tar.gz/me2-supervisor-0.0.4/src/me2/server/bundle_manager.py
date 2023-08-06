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

from me2.packaging.dric import MetaRepository
from me2.packaging.package import parse_artifact_spec
from me2.packaging.package import Bundle

from mjsrpc2 import RPCBase, jsonmethod, jsonattribute


class BundleManager(RPCBase):
    log = logging.getLogger("BundleManager")
    def __init__(self, context, manager, config, storage_manager):
        RPCBase.__init__(self)
        self._manager = manager
        self.context = context
        self._config = config
        self._storage_manager = storage_manager
        self.repo = MetaRepository(repositorys = self._config.get("sources", []))

    @jsonmethod
    @jsonattribute(name = "bundle_specification", type = str)
    def import_bundle(self, bundle_specification):
        self._import_bundle(bundle_specification)

    def _import_bundle(self, bundle_specification):
        groupId, artifactId, version, classifier = parse_artifact_spec(bundle_specification)
        # Download file
        local_file = self.repo.fetch(groupId, artifactId, version, classifier)
        bundle = Bundle(local_file)
        # Create the base bundle
        bottle_location = self._storage_manager.create_base_bottle(name = bundle_specification)
        # Extract the content
        self.explode_bundle(bundle, bottle_location)
        return bottle_location



    def explode_bundle(self, bundle, destination):
        self.log.info("Exploding %s to %s", bundle, destination)
        bundle.extract(destination)


