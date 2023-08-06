# Copyright (c) 2013 Per Unneberg
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

class ISample(object):
    """A sample interface class"""
    def id(self):
        """Sample identifier"""
        raise NotImplementedError
    def merge_output(self):
        """Output location prefix of merge operation"""
        raise NotImplementedError
    def sample_run_output(self):
        """Output location prefix of sample run"""
        raise NotImplementedError
    def level(self):
        """Factor level"""
        raise NotImplementedError

class Sample(ISample):
    """A class describing a sample."""
    pass
