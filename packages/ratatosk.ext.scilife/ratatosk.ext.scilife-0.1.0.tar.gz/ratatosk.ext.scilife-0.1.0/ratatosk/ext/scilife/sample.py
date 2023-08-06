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
import re
from ratatosk.utils import rreplace
from ratatosk.ext.scilife.bcbio import bcbio_config_to_sample_sheet

logging.basicConfig(level=logging.DEBUG)

def collect_sample_runs(task):
    """Collect sample runs for a sample. Since it is to be used with
    MergeSamFiles it should return a list of targets.

    :param task: current task

    :return: list of bam files for each sample run in a flowcell directory
    """
    logging.debug("Collecting sample runs for {}".format(task.target))
    sample_runs = target_generator(os.path.dirname(os.path.dirname(task.target)), 
                                   sample=[os.path.basename(os.path.dirname(task.target))])
    src_suffix = task.parent()[0]().suffix
    bam_list = [x[2] + os.path.basename(rreplace(task.target.replace(x[0], ""), "{}{}".format(task.label, task.suffix), src_suffix, 1)) for x in sample_runs]
    logging.debug("Generated target bamfile list {}".format(bam_list))
    return bam_list

def generic_collect_sample_runs(task):
    """Collect sample runs for a sample. Since it is to be used with
    MergeSamFiles it should return a list of targets.

    :param task: current task

    :return: list of bam files for each sample run in a flowcell directory
    """
    logging.debug("Collecting sample runs for {}".format(task.target))
    sample_runs = generic_target_generator(os.path.dirname(os.path.dirname(task.target)), 
                                           sample=[os.path.basename(os.path.dirname(task.target))])
    src_suffix = task.parent()[0]().suffix
    bam_list = [x[2] + os.path.basename(rreplace(task.target.replace(x[0], ""), "{}{}".format(task.label, task.suffix), src_suffix, 1)) for x in sample_runs]
    logging.debug("Generated target bamfile list {}".format(bam_list))
    return bam_list


def collect_vcf_files(task, sample=None, flowcell=None, lane=None, **kwargs):
    logging.debug("Collecting vcf files for {}".format(task.target))
    sample_runs = target_generator(os.path.dirname(task.target))
    parent_cls = task.parent()[0]
    vcf_list = list(set([x[1] + task.adl() + parent_cls().sfx()  for x in sample_runs]))
    logging.debug("Generated target vcffile list {}".format(vcf_list))
    return vcf_list



def generic_target_generator(indir, sample=None, flowcell=None, lane=None, **kwargs):
    """Generic target generator. Uses the directory structure only to
    generate target names. Requires SciLife-like directory structure.
    
    :param indir: input directory
    :param sample: list of sample names to include
    :param flowcell: list of flowcells to include
    :param lane: list of lanes to include

    :returns: list of targets
    """
    targets = []
    if not os.path.exists(indir):
        logging.warn("No such input directory '{}'".format(indir))
        return targets
    samples = os.listdir(indir)
    # Only run this sample if provided at command line.
    if sample:
        samples = sample
    for s in samples:
        sampledir = os.path.join(indir, s)
        if not os.path.isdir(sampledir):
            continue
        flowcells = [fc for fc in os.listdir(sampledir) if os.path.isdir(os.path.join(sampledir, fc))]
        for fc in flowcells:
            if flowcell and not fc in flowcell:
                continue
            fc_dir = os.path.join(sampledir, fc)
            flist = []
            for root, dirs, files in os.walk(fc_dir):
                flist = flist + [os.path.join(root, x) for x in files]
            fqfiles = [x for x in flist if re.match(".*(.fastq$|.fastq.gz$|.fq$|.fq.gz$)", x)]
            for fq in fqfiles:
                logging.info("Adding sample '{0}' from flowcell '{1}' to analysis".format(s, fc))
                m = re.match("(.*)_[0-9]+(.fastq$|.fastq.gz$|.fq$|.fq.gz$)", fq)
                if not m:
                    logging.warn("File {} does not comply with format (.*)_[0-9]+(.fastq$|.fastq.gz$|.fq$|.fq.gz$); skipping".format(fq))
                    continue
                targets.append((s, os.path.join(sampledir, s), 
                                os.path.join(fc_dir, os.path.basename(m.group(1)))))
    return targets
    

def target_generator(indir, sample=None, flowcell=None, lane=None, **kwargs):
    """Make all desired target output names based on the final target
    suffix. 

    :param indir: input directory
    :param sample: list of sample names to include
    :param flowcell: list of flowcells to include
    :param lane: list of lanes to include

    :return: list of tuples consisting of sample, sample target prefix (merge target), sample run prefix (read pair prefix)
    """
    print "In target_generator"
    targets = []
    if not os.path.exists(indir):
        logging.warn("No such input directory '{}'".format(indir))
        return targets
    samples = os.listdir(indir)
    # Only run this sample if provided at command line.
    if sample:
        samples = sample
    for s in samples:
        sampledir = os.path.join(indir, s)
        if not os.path.isdir(sampledir):
            continue
        flowcells = [fc for fc in os.listdir(sampledir) if fc.endswith("XX")]
        for fc in flowcells:
            if flowcell and not fc in flowcell:
                continue
            fc_dir = os.path.join(sampledir, fc)
            ssheet = read_sample_sheet(fc_dir, s, fc)
            if not ssheet:
                continue
            for line in ssheet:
                logging.info("Adding sample '{0}' from flowcell '{1}' (barcode '{2}') to analysis".format(s, fc, line['Index']))
                targets.append((s, os.path.join(sampledir, s), 
                                os.path.join(fc_dir, "{}_{}_L00{}".format(s, line['Index'], line['Lane'] ))))
    return targets


def read_sample_sheet(fc_dir, sample=None, flowcell=None, ssheetname="SampleSheet.csv", runinfo_glob="*-bcbb-config.yaml"):
    """Read sample sheet if exists and return list of samples. Tries
    first Illumina SampleSheet style, then bcbio runinfo
    configuration.

    :param fc_dir: flowcell directory
    :param sample: sample name
    :param flowcell: flowcell name
    :param ssheetname: sample sheet name
    :param runinfo_glob: bcbio config glob name

    :returns: list of samples, or None
    """
    if os.path.exists(os.path.join(fc_dir, ssheetname)):
        fh = file(os.path.join(fc_dir, ssheetname))
        ssheet = csv.DictReader([x for x in fh if x[0] != "#"])
    else:
        logging.warn("No sample sheet for sample '{}' in flowcell '{}';  trying bcbio format".format(sample, flowcell))
        runinfo = glob.glob(os.path.join(fc_dir, "{}*-bcbb-config.yaml".format(sample)))
        if not runinfo:
            logging.warn("No sample information for sample '{}' in flowcell '{}';  skipping".format(sample, flowcell))
            return None
        if not os.path.exists(runinfo[0]):
            logging.warn("No sample information for sample '{}' in flowcell '{}';  skipping".format(sample, flowcell))
            return None
        else:
            ssheet = bcbio_config_to_sample_sheet(runinfo[0])
    return ssheet
