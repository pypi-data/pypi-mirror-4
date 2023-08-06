#!/usr/bin/env python
#
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
import luigi
import os
import sys
from ratatosk import backend
from ratatosk.config import setup_config
from ratatosk.handler import setup_global_handlers
from ratatosk.utils import opt_to_dict, dict_to_opt
import ratatosk.lib.align.bwa
import ratatosk.lib.tools.gatk
import ratatosk.lib.tools.samtools
import ratatosk.lib.tools.picard
import ratatosk.lib.annotation.annovar
import ratatosk.lib.utils.cutadapt
from ratatosk.pipeline.haloplex import HaloPlex, HaloPlexSummary
from ratatosk.pipeline.seqcap import SeqCap, SeqCapSummary
from ratatosk.pipeline.align import Align, AlignSummary
from ratatosk.ext.scilife.config import config_dict

if __name__ == "__main__":
    task_cls = None
    opt_dict = {}
    if len(sys.argv) > 1:
        task = sys.argv[1]
        task_args = sys.argv[2:]
        if task in config_dict.keys():
            # Reset config-file if present
            if "--config-file" in task_args:
                i = task_args.index("--config-file")
                task_args[i+1] = config_dict[task]['config']
            else:
                task_args.append("--config-file")
                task_args.append(config_dict[task]['config'])
            task_cls = config_dict[task]['cls']
    else:
        task = None

    config_file = None
    custom_config_file = None
    if "--config-file" in task_args:
        config_file = task_args[task_args.index("--config-file") + 1]
    if "--custom-config" in task_args:
        custom_config_file = task_args[task_args.index("--custom-config") + 1]

    setup_config(config_file=config_file, custom_config_file=custom_config_file)
    setup_global_handlers()

    if task_cls:
        luigi.run(task_args, main_task_cls=task_cls)
    # Whatever other task/config the user wants to run
    else:
        luigi.run()
