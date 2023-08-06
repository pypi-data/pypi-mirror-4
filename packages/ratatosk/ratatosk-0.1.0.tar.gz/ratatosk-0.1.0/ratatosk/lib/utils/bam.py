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
import os
import luigi
import logging
from contextlib import closing
import pysam
import ratatosk.lib.files.external
from ratatosk import backend
from ratatosk.job import InputJobTask, JobTask, DefaultShellJobRunner
from ratatosk.utils import rreplace

logger = logging.getLogger('luigi-interface')

class BamJobRunner(DefaultShellJobRunner):
    pass

class InputBamFile(InputJobTask):
    """Wrapper task that serves as entry point for bam tasks"""

    parent_task = luigi.Parameter(default="ratatosk.lib.files.external.BamFile")
    

class BamJobTask(JobTask):
    """Main bam job task"""
    executable = luigi.Parameter(default=None)
    parent_task = luigi.Parameter(default="ratatosk.lib.tools.samtools.InputBamFile")
    target_suffix = luigi.Parameter(default=".bam")
    source_suffix = luigi.Parameter(default=".bam")
    target_region = luigi.Parameter(default=None)

    def job_runner(self):
        return BamJobRunner()

class SplitBam(BamJobTask):
    parent_task = luigi.Parameter(default="ratatosk.lib.utils.bam.InputBamFile")
    label = luigi.Parameter(default="-variants")

    def _split(self):
        """Split file into regions"""
        pass

    def _make_source_file_name(self):
        """Assume pattern is {base}-split/{base}-{ref}{ext}, as in
        CombineVariants.

        FIX ME: well, generalize
        """
        base = rreplace(os.path.join(os.path.dirname(os.path.dirname(self.target)), os.path.basename(self.target)), self.label, "", 1).split("-")
        return "".join(base[0:-1]) + self.target_suffix

    def requires(self):
        cls = self.set_parent_task()
        source = self._make_source_file_name()
        return [cls(target=source)]

    def run(self):
        source = self._make_source_file_name()
        with closing (pysam.Samfile(source, "rb")) as work_bam:
            pass
            
        
