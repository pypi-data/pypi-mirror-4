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

from setuptools import setup, find_packages
import sys
import os
import glob

setup(name = "ratatosk.ext.scilife",
      version = "0.1.0",
      author = "Per Unneberg",
      author_email = "per.unneberg@scilifelab.se",
      description = "ratatosk addon for Science for Life Laboratory",
      license = "Apache",
      scripts = glob.glob('scripts/*.py') + glob.glob('scripts/*.pl'),
      install_requires = [
        "drmaa >= 0.5",
        "luigi",
        "nose",
        "ratatosk >= 0.1.0",
        "cutadapt",
        ],
      test_suite = 'nose.collector',
      packages=find_packages(exclude=['test']),
      # [
      #   'ratatosk.scilife'
      #   ],
      package_data = {
        'ratatosk':[
            'config/scilife/*',
            ]}
      )

