#!/usr/bin/python

# Copyright 2015 Maintainers of dk8s
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import sys
import subprocess
import urllib2
from optparse import OptionParser
from optparse import OptionGroup

USAGE = (
"""%prog [options]
 
 * Requires local docker
 * Tested in Python 2.7
""")

LOG_FORMAT = "%(asctime)s\t%(name)-4s %(process)d : %(message)s"

if __name__ == "__main__":
  
  # Direct all script output to a log
  log = logging.getLogger("dk8s")
  log.setLevel(logging.INFO)
  console_handler = logging.StreamHandler(stream=sys.stderr)
  console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
  log.addHandler(console_handler)


  def run_in_shell(cmd):
    log.info("Running %s ..." % cmd)
    subprocess.check_call(cmd, shell=True)
    log.info("... done")
  
  
  # Flags! No, wait, they"re *options* ...
  option_parser = OptionParser(usage=USAGE)
  
  config_group = OptionGroup(
                    option_parser,
                    "Config",
                    "Configuration")
  config_group.add_option(
    "--tag", default="dk8s",
    help="Use this image tag [default %default]")
  config_group.add_option(
    "--name", default="dk8s",
    help="Use this container name [default %default]")
  config_group.add_option(
    "--k8s", default=None,
    help="Copy this checkout of Kubernetes to /opt/kubernetes in the container."
         "If no path is given, check out master k8s from git.")
  option_parser.add_option_group(config_group)
  
  action_group = OptionGroup(
                    option_parser,
                    "Local",
                    "Local Actions")
  action_group.add_option(
    "--build", default=False, action="store_true",
    help="Build the k8s container")
  action_group.add_option(
    "--up", default=False, action="store_true",
    help="Start up the container")
  action_group.add_option(
    "--shell", default=False, action="store_true",
    help="Drop into bash inside the test container")
  action_group.add_option(
    "--rm", default=False, action="store_true",
    help="Remote the test container")
  option_parser.add_option_group(action_group)

  
  opts, args = option_parser.parse_args()
  
  
  assert os.path.exists("DOCKERFILE"), "Please run from local_k8s directory"
  
  
  if opts.build:
    # Get k8s
    if not os.path.exists(".kubernetes"):
      if opts.k8s:
        log.info("Copying kubernetes for inclusion in Docker image ...")
        
        # Normalize source
        src = opts.k8s if not opts.k8s.endswith('/') else opts.k8s[:-1]
        run_in_shell("mkdir .kubernetes && cp -vr " + opts.k8s +"/* .kubernetes/")
        
        log.info("... done copying.")
      else:
        log.info("Fetching latest kubernetes ...")
        
        """
        # Use below for a *release*. But right now local
        # cluster stuff is only in git.
        
        # Use the get.k8s.io trick
        LATEST_TAG_URL = "https://storage.googleapis.com/kubernetes-release/release/stable.txt"
        latest = urllib2.urlopen(LATEST_TAG_URL).read().strip()
        k8s_url = (
          "https://storage.googleapis.com/kubernetes-release/release/" +
          latest + "/kubernetes.tar.gz")
        run_in_shell(
          "wget -O .kubernetes.tar.gz " + k8s_url + " && " +
          "tar -xzf .kubernetes.tar.gz && " +
          "mv kubernetes .kubernetes && " +
          "rm .kubernetes.tar.gz")
        """
        
        run_in_shell(
          "git clone --depth=1 https://github.com/GoogleCloudPlatform/kubernetes.git .kubernetes")
        
        log.info("... done fetching k8s.")
    
    run_in_shell("docker build -t " + opts.tag + " .")

  if opts.up:
    run_in_shell(
      "docker run --privileged=true -d --name=" + opts.name + " -t " + opts.tag)
  
  if opts.shell:
    CMD = "docker exec --interactive --tty " + opts.name + " bash"
    os.execvp("docker", CMD.split(" "))

  if opts.rm:
    run_in_shell("docker kill " + opts.name + " && docker rm " + opts.name)
