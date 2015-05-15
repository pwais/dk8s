#!/bin/bash

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

set -e
set -x

# Give Docker more loopback devices
echo "options loop max_loop=256" >> /etc/modprobe.d/loop.conf

service docker start
while ! docker ps -a
do
  echo "$(date) - waiting for docker"
  sleep 1
done
echo "$(date) - Docker up!"

# DNS is now on by default for most clusters (e.g. GCE, AWS)
# *except* local
export ENABLE_CLUSTER_DNS=true
export DNS_SERVER_IP="10.100.0.15"
export DNS_DOMAIN="kubernetes.local"
export DNS_REPLICAS=1

/opt/kubernetes/hack/local-up-cluster.sh &
while ! /opt/kubernetes/cluster/kubectl.sh get pods
do
  echo "$(date) - waiting for k8s"
  sleep 1
done
echo "$(date) - k8s up!"

# Start DNS
# Based upon kubernetes/cluster/ubuntu/deployAddons.sh
sed -e "s/{{ pillar\['dns_replicas'\] }}/${DNS_REPLICAS}/g;s/{{ pillar\['dns_domain'\] }}/${DNS_DOMAIN}/g" /opt/kubernetes/cluster/addons/dns/skydns-rc.yaml.in > ~/skydns-rc.yaml
sed -e "s/{{ pillar\['dns_server'\] }}/${DNS_SERVER_IP}/g" /opt/kubernetes/cluster/addons/dns/skydns-svc.yaml.in > ~/skydns-svc.yaml
/opt/kubernetes/cluster/kubectl.sh create -f ~/skydns-rc.yaml
/opt/kubernetes/cluster/kubectl.sh create -f ~/skydns-svc.yaml

tail -F /tmp/kube*
