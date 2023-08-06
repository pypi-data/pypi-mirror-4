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

import re
import os
import sys
import argparse
import itertools
import logging
import copy
from ratatosk.ext.scilife.sample import target_generator
from ratatosk.utils import make_fastq_links, opt_to_dict

logging.basicConfig(level=logging.INFO)

has_drmaa=False
try:
    import drmaa
    has_drmaa=True
except:
    pass

# Called script
RATATOSK_RUN = "ratatosk_run_scilife.py"
RATATOSKD = "ratatoskd"

## yes or no: http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
def query_yes_no(question, default="yes", force=False):
    """Ask a yes/no question via raw_input() and return their answer.
    
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
    It must be "yes" (the default), "no" or None (meaning
    an answer is required of the user). The force option simply
    sets the answer to default.
    
    The "answer" return value is one of "yes" or "no".
    
    :param question: the displayed question
    :param default: the default answer
    :param force: set answer to default
    :returns: yes or no
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        if not force:
            choice = raw_input().lower()
        else:
            choice = "yes"
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                                 "(or 'y' or 'n').\n")

def dry(message, func, dry_run=True, *args, **kw):
    """Wrapper that runs a function (runpipe) if flag dry_run isn't set, otherwise returns function call as string
    
    :param message: message describing function call
    :param func: function to call
    :param *args: positional arguments to pass to function
    :param **kw: keyword arguments to pass to function
    """
    if dry_run:
        logging.info("(DRY_RUN): " + str(message) + "\n")
        return "(DRY_RUN): " + str(message) + "\n"
    return func(*args, **kw)

def drmaa_wrapper(cmd_args, pargs, capture=True, ignore_error=False, cwd=None):
    kw = vars(pargs)
    job_args = make_job_template_args(opt_to_dict(pargs.extra), **kw)
    command = "\n".join([" ".join(x) for x in cmd_args])
    def runpipe():
        s = drmaa.Session()
        s.initialize()
        jt = s.createJobTemplate()
        jt.remoteCommand = command
        jt.jobName = job_args['jobname']

        if os.path.isdir(job_args['outputPath']):
            jt.outputPath = ":" + drmaa.JobTemplate.HOME_DIRECTORY + os.sep + os.path.join(os.path.relpath(job_args['outputPath'], os.getenv("HOME")), jt.jobName + "-drmaa.log")
        else:
            jt.outputPath = ":" + drmaa.JobTemplate.HOME_DIRECTORY + os.sep + os.path.join(os.path.relpath(job_args['outputPath'], os.getenv("HOME")))
        if os.path.isdir(job_args['errorPath']):
            jt.errorPath = ":" + drmaa.JobTemplate.HOME_DIRECTORY + os.sep + os.path.join(os.path.relpath(job_args['errorPath'], os.getenv("HOME")), jt.jobName + "-drmaa.err")
        else:
            jt.errorPath = ":" + drmaa.JobTemplate.HOME_DIRECTORY + os.sep + os.path.join(os.path.relpath(job_args['errorPath'], os.getenv("HOME")))

        jt.workingDirectory = drmaa.JobTemplate.HOME_DIRECTORY + os.sep + os.path.relpath(job_args['workingDirectory'], os.getenv("HOME"))
        jt.nativeSpecification = "-t {time} -p {partition} -A {account} {extra}".format(**job_args)
        if kw.get('email', None):
            jt.email=[kw.get('email')]
        logging.info("Submitting job with native specification {}".format(jt.nativeSpecification))
        logging.info("Working directory: {}".format(jt.workingDirectory))
        logging.info("Output logging: {}".format(jt.outputPath))
        logging.info("Error logging: {}".format(jt.errorPath))
        jobid = s.runJob(jt)
        logging.info('Your job has been submitted with id ' + jobid)
        s.deleteJobTemplate(jt)
        s.exit()
    dry(command, runpipe, dry_run=kw.get("dry_run"))

def convert_to_drmaa_time(t):
    """Convert time assignment to format understood by drmaa.

    In particular transforms days to hours if provided format is
    d-hh:mm:ss. Also transforms mm:ss to 00:mm:ss.

    :param t: time string

    :returns: converted time string formatted as hh:mm:ss or None if
    time string is malformatted
    """
    if not t:
        return None
    m = re.search("(^[0-9]+\-)?([0-9]+:)?([0-9]+):([0-9]+)", t)
    if not m:
        return None
    days = None
    if m.group(1):
        days = m.group(1).rstrip("-")
    hours = None
    if m.group(2):
        hours = m.group(2).rstrip(":")
    minutes = m.group(3)
    seconds = m.group(4)
    if days:
        hours = 24 * int(days) + int(hours)
    else:
        if not hours:
            hours = "00"
        if len(str(hours)) == 1:
            hours = "0" + hours
        if len(str(minutes)) == 1:
            minutes = "0" + minutes
    t_new = "{}:{}:{}".format(hours, minutes, seconds)
    return t_new

def make_job_template_args(opt_d, **kw):
    """Given a dictionary of arguments, update with kw dict that holds arguments passed to argv.

    :param opt_d: dictionary of option key/value pairs
    :param kw: dictionary of program arguments

    :returns: dictionary of job arguments
    """
    job_args = {}
    job_args['jobname'] = kw.get('jobname')
    job_args['time'] = kw.get('time')
    job_args['time'] = convert_to_drmaa_time(job_args['time'])
    job_args['partition'] = kw.get('partition')
    job_args['account'] = kw.get('account', None)
    job_args['outputPath'] = kw.get('outputPath')
    job_args['errorPath'] = kw.get('errorPath')
    job_args['workingDirectory'] = kw.get('workingDirectory')
    job_args['email'] = kw.get('email', None)

    invalid_keys = ["--mail-user", "--mail-type", "-o", "--output", "-D", "--workdir", "-J", "--job-name", "-p", "--partition", "-t", "--time", "-A", "--account", "-e", "--error"]
    extra_keys = [x for x in opt_d.keys() if x not in invalid_keys]
    extra_args = ["{}={}".format(x, opt_d[x]) if x.startswith("--") else "{} {}".format(x, opt_d[x]) for x in extra_keys]
    job_args['extra'] = " ".join(extra_args)

    return job_args


if __name__ == "__main__":
    if not os.getenv("DRMAA_LIBRARY_PATH"):
        logging.warn("No environment variable $DRMAA_LIBRARY_PATH: loading {} failed".format(__name__))
        sys.exit()
    if not has_drmaa:
        logging.warn("No 'drmaa' module: please install drmaa before proceeding.".format(__name__))
        sys.exit()
    parser = argparse.ArgumentParser(description='ratatosk submit job arguments.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Basic options
    group = parser.add_argument_group("Common options")
    group.add_argument('-n', '--dry_run', action="store_true", default=False, help="do a dry run (prints commands without actually running anything)")

    # Drmaa parser group
    group = parser.add_argument_group("Drmaa options")
    group.add_argument('-A', '--account', type=str, required=True,
                        help='UPPMAX project account id')
    group.add_argument('-p', '--partition', type=str, default="node",
                        help='partition type.', choices=["node", "core", "devel"])
    # nodes and num_cores are currently set via the nativeSpecification
    # group.add_argument('-N', '--nodes', type=int, default=1,
    #                     help='number of nodes to use. NB: currently only 1 node allowed', choices=[1])
    # group.add_argument('-n', '--num_cores', type=int, default=1,
    #                     help='number of cores to use.', choices=xrange(1,9))
    group.add_argument('-t', '--time', type=str, default="10:00:00",
                        help='run time')
    group.add_argument('-J', '--jobname', type=str, default="ratatosk",
                        help='job name')
    group.add_argument('-D', '--workingDirectory', type=str, default=os.curdir,
                        help='working directory')
    group.add_argument('-o', '--outputPath', type=str, default=os.curdir,
                        help='output path for stdout')
    group.add_argument('-e', '--errorPath', type=str, default=os.curdir,
                        help='output path for stderr')
    group.add_argument('--email', type=str, default=None,
                        help='email address to send job information to')
    group.add_argument('--extra', type=str, default=[],
                        help='Extra specification args to submit via drmaa, provided as string (e.g. "--ntasks 4 --nodes 2 -C fat" for running 4 tasks on 2 nodes on fat partitions)')

    # Sample parser group
    sample_group = parser.add_argument_group("Sample options")
    sample_group.add_argument('-O', '--outdir', type=str, default=None, help='Output directory. Defaults to input directory, (i.e. runs analysis in input directory). Setting this will create symlinks for all requested files in input directory, mirroring the input directory structure.')
    sample_group.add_argument('--sample', type=str, default=None, nargs="*",
                              help='samples to process')
    sample_group.add_argument('--sample_file', type=str, default=None,
                              help='file containing samples to process, one per line')
    sample_group.add_argument('--lane', type=int, choices=xrange(1,9), default=None,
                              help='lanes to process', nargs="*")
    sample_group.add_argument('--flowcell', type=str, default=None, nargs="*",
                              help='flowcells to process')
    sample_group.add_argument('-B', '--batch_size', type=int, default=4,
                              help='number of samples to process per node')
    sample_group.add_argument('-1', '--sample-target-suffix', type=str, default=None,
                              help='target suffix to add to the sample target (position 1 in target generator tuple)')
    sample_group.add_argument('-2', '--run-target-suffix', type=str, default=None,
                              help='target suffix to add to the sample run target (position 2 in target generator tuple)')

    # Ratatosk parser group
    # These arguments are directly passed to ratatosk
    ratatosk_group = parser.add_argument_group("Ratatosk options. These arguments are passed directly to ratatosk_run_scilife.py")
    ratatosk_group.add_argument('--config-file', type=str, default=None,
                                help='configuration file')
    ratatosk_group.add_argument('--custom-config', type=str, default=None,
                                help='custom configuration file')
    ratatosk_group.add_argument('--workers', type=int, default=4,
                                help='number of workers to use')
    ratatosk_group.add_argument('--scheduler-host', type=str, default="localhost",
                                help='host that runs scheduler')

    # Add positional arguments. The order in which they are listed
    # defines the order they should appear on the command line
    ratatosk_group.add_argument('task', type=str,
                              help='Task to run.')
    sample_group.add_argument('indir', type=str,
                              help='Input directory. Assumes that data in input directory is organized by sample/flowcell/sequences.fastq.gz')

    # Parse arguments
    pargs = parser.parse_args()

    # Collect information about what samples to run, and on how many
    # nodes. This is somewhat convoluted since ratatosk_run_scilife
    # also collects sample information, but this step is necessary as
    # we need to wrap ratatosk_run_scilife.py in drmaa
    targets = target_generator(indir=pargs.indir, sample=pargs.sample,
                               flowcell=pargs.flowcell, lane=pargs.lane)
    # After getting run list, if output directory is different to
    # input directory, link raw data files to output directory and
    # remember to use this directory for ratatosk tasks. In this way
    # we actually can run on subsets of sample runs or flowcells
    if not pargs.outdir:
        pargs.outdir = pargs.indir
    if pargs.outdir != pargs.indir:
        targets = make_fastq_links(targets, pargs.indir, pargs.outdir)

    # Group samples
    sorted_samples = sorted(targets, key=lambda t:t[0])
    samples = {}
    for k, g in itertools.groupby(sorted_samples, key=lambda t:t[0]):
        samples[k] = list(g)

    # Initialize command
    cmd = [RATATOSK_RUN, pargs.task, '--indir', pargs.indir, '--outdir', pargs.outdir, 
           '--workers', pargs.workers, '--scheduler-host', pargs.scheduler_host]
    if pargs.config_file:
        logging.info("setting config to {}".format(pargs.config_file))
        cmd += ['--config-file', pargs.config_file]
    if pargs.custom_config:
        logging.info("setting custom config to {}".format(pargs.custom_config))
        cmd += ['--custom-config', pargs.custom_config]
    if pargs.flowcell:
        for fc in pargs.flowcell:
            cmd += ['--flowcell', fc]
    if pargs.lane:
        for lane in pargs.lane:
            cmd += ['--lane', lane]

    # If devel job requested, set time to 1 h if pargs.time is greater
    if pargs.partition == "devel":
        t = convert_to_drmaa_time(pargs.time)
        (hh, mm, ss) = t.split(":")
        mm = int(hh) * 60 + int(mm)
        if mm > 60:
            logging.info("resetting devel job time from {} to 01:00:00".format(pargs.time))
            pargs.time = "01:00:00"

    # Submit batch jobs
    batches = [sorted(samples.keys())[x:x+pargs.batch_size] for x in xrange(0, len(samples.keys()), pargs.batch_size)]
    batchid = 1
    jobname_default = pargs.jobname
    if len(batches) > 0 and query_yes_no("Going to start {} jobs... Are you sure you want to continue?".format(len(batches))):
        for sample_batch in batches:
            drmaa_cmd = []
            # Use the local scheduler; start ratatoskd on node, wait
            # 10 seconds to make sure it has started before running
            # commands
            if pargs.scheduler_host == "localhost":
                drmaa_cmd.append([RATATOSKD, "&"])
                drmaa_cmd.append(["sleep 10"])
            batch_cmd = copy.deepcopy(cmd)
            if len(batches) > 1:
                pargs.jobname = "{}_{}".format(jobname_default, batchid)
                batchid += 1
            # Decide whether to use explicit target names or sample names
            if pargs.sample_target_suffix or pargs.run_target_suffix:
                sfx = pargs.sample_target_suffix.lstrip("\\")
                l = [samples[x] for x in sample_batch]
                tasktargets = ["{}{}".format(y[0][1], sfx) for y in l]
                # Needs rethinking: basically need a generic wrapper
                # task that takes as input a list of targets and a
                # class name
                # 
                # for t in tasktargets:
                #     batch_cmd += ['--target', t]
                #     batch_cmd = [str(x) for x in batch_cmd]
                #     drmaa_cmd.append(batch_cmd)
            else:
                l = [samples[x] for x in sample_batch]
                samplelist = [item for sublist in l for item in sublist] 
                for s in sample_batch:
                    batch_cmd += ['--sample', s]
                batch_cmd = [str(x) for x in batch_cmd]
                drmaa_cmd.append(batch_cmd)
            logging.info("passing command '{}' to drmaa...".format("\n".join([" ".join(x) for x in drmaa_cmd])))
            drmaa_wrapper(drmaa_cmd, pargs)
            if pargs.partition == "devel":
                logging.warn("only submitting 1 devel job... skipping remaining tasks")
                break
