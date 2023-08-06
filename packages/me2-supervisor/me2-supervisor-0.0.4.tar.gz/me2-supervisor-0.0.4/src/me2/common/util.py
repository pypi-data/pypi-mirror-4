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

from Queue import Queue


class QueuePair(object):
    def __init__(self, in_q = None, out_q = None):
        if in_q is None:
            self.inq = Queue()
        else:
            self.inq = in_q
        if out_q is None:
            self.outq = Queue()
        else:
            self.outq = out_q

    def put(self, item, block = True, timeout = None):
        self.outq.put(item, block, timeout)

    def get(self, block = True, timeout = None):
        self.inq.get(block, timeout)

    def invert(self):
        return QueuePair(in_q = self.outq, out_q = self.outq)
