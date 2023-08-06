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
import shutil
import unittest
import logging
import ratatosk.lib.tools.picard
from ratatosk.ext.scilife.sample import *

class PTask(object):
    def __init__(self):
        self.suffix = ".parent_suffix"

class Task(object):
    suffix = ".source_suffix"
    def __init__(self, target, label, source_suffix, target_suffix):
        self._target = target
        self._label = label
        self._source_suffix = source_suffix
        self._target_suffix = target_suffix

    @property
    def target(self):
        return self._target

    @property
    def label(self):
        return self._label

    @property
    def target_suffix(self):
        return self._target_suffix

    @property
    def source_suffix(self):
        return self._source_suffix

    def parent(self):
        return [ratatosk.lib.tools.picard.InputBamFile]
        

class TestFunctions(unittest.TestCase):
    def setUp(self):
        self.project = os.path.join("projects", "J.Doe_00_01")
        self.sample = 'P001_101_index3'
        self.flowcell = '120924_AC003CCCXX'

    def tearDown(self):
        if os.path.exists("tmp"):
            shutil.rmtree("tmp")

    def test_tg_all(self):
        """Test getting all sample runs from a project"""
        tl = target_generator(indir=self.project)
        self.assertEqual(sorted([x[0] for x in tl]), ['P001_101_index3', 'P001_101_index3', 'P001_101_index3', 'P001_102_index6', 'P001_102_index6'])
        self.assertEqual(list(set([x[0] for x in tl])), ['P001_101_index3', 'P001_102_index6'])

    def test_tg_subset_sample(self):
        """Test getting a subset of samples"""
        tl = target_generator(indir=self.project, sample=[self.sample])
        self.assertEqual(sorted([x[0] for x in tl]), ['P001_101_index3', 'P001_101_index3', 'P001_101_index3'])

    def test_tg_subset_flowcell(self):
        """Test getting samples subsetted by flowcell"""
        tl = target_generator(indir=self.project, flowcell=[self.flowcell])
        self.assertNotIn("121015_BB002BBBXX",  sorted([os.path.basename(os.path.dirname(x[2])) for x in tl]))

    def test_tg_subset_sample_flowcell(self):
        """Test getting samples subsetted by flowcell and sample"""
        tl = target_generator(indir=self.project, flowcell=[self.flowcell], sample=[self.sample])
        self.assertEqual(sorted([os.path.basename(os.path.dirname(x[2])) for x in tl]), ['120924_AC003CCCXX', '120924_AC003CCCXX'])
        self.assertEqual(sorted([os.path.basename(x[0]) for x in tl]), ['P001_101_index3', 'P001_101_index3'])

    def test_collect_sample_runs(self):
        """Test function that collects sample runs"""
        t = Task(target=os.path.join(self.project, "P001_101_index3", "P001_101_index3.sort.merge.bam"), label=".merge", source_suffix=".bam", target_suffix=".bam")
        bam_list = collect_sample_runs(t)
        #self.assertEqual('P001_101_index3_TGACCA_L001.sort.bam', os.path.basename(bam_list[0]))
