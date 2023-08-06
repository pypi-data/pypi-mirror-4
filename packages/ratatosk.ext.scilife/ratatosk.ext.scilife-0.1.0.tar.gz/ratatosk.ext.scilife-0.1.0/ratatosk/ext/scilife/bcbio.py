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
import glob
import csv
import logging
import yaml
import cStringIO
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)

def bcbio_config_to_sample_sheet(config, save=True):
    """Convert bcbio config file to standard Illumina SampleSheet format. 

    :param config: bcbio config file
    :param save: save results to SampleSheet.csv

    :returns: SampleSheet-formatted configuration (list of lists)
    """
    keys = ["FCID", "Lane", "SampleID", "SampleRef", "Index",
              "Description" , "Control", "Recipe", "Operator", "SampleProject"]
    with open(config) as fh:
        runinfo_yaml = yaml.load(fh)
    runinfo = runinfo_yaml.get("details", None) if runinfo_yaml.get("details", None) else runinfo_yaml
    ssheet = []
    for info in runinfo:
        for mp in info["multiplex"]:
            item = {"FCID":info.get("flowcell_id", None),
                    "Lane":info.get("lane", None),
                    "SampleRef":info.get("genome_build", None),
                    "Control":"N",
                    "Recipe":"R1",
                    "Operator":"NN",
                    "SampleID":mp.get("name"),
                    "Index":mp.get("sequence"),
                    "Description":mp.get("sample_prj").replace(".", "__"),
                    "SampleProject":mp.get("sample_prj")
                    }
            ssheet.append(item)
    if save:
        logging.info("Saving SampleSheet.csv based on yaml file {}".format(config))
        fh = file(os.path.join(os.path.dirname(config), "SampleSheet.csv"), "w")
        fh.write("# Generated SampleSheet.csv from {} {} by {}\n".format(config, datetime.today().strftime("at %H:%M on %A %d, %B %Y"), __name__))
        fh.write(",".join(keys) + "\n")
        writer = csv.DictWriter(fh, fieldnames=keys)
        writer.writerows(ssheet)
        fh.close()
    return ssheet
