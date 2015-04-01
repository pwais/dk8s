# dk8s: Dockerized Kubernetes

This project contains a Docker container for running Kubernetes (k8s) locally.
Useful for local testing on non-linux machines (e.g. Mac OS X).

This solution is an alternative to the k8s [Vagrant-based local mode](https://github.com/GoogleCloudPlatform/kubernetes/blob/master/docs/getting-started-guides/vagrant.md).
Using this project is somewhat faster but does not expose the root host
to the k8s minion machines.

To use, run `$ ./dk8s.py --build --up`.

# Testing the Container

1. Start a test container:

    ```$ ./setup.py --up```

It may take a minute or two for k8s to build inside the container.  Use `$ docker logs local_k8s_test` to follow along.  Wait until you see a message like:
  
  ```
  To start using your cluster, open up another terminal/tab and run:

  cluster/kubectl.sh config set-cluster local --server=http://127.0.0.1:8080 --insecure-skip-tls-verify=true --global
  cluster/kubectl.sh config set-context local --cluster=local --global
  cluster/kubectl.sh config use-context local
  cluster/kubectl.sh
  ```

If the startup process fails with something like

   ```
   !!! Error in /opt/kubernetes/hack/local-up-cluster.sh:33
   '${DOCKER[@]} ps 2> /dev/null > /dev/null' exited with status 1
   ```

in the logs, then use `$ docker ps -a` to find and delete any containers using the `dk8s` image.

2. Start a shell inside the container: 

    ```$ ./setup.py --shell```

3. Try running nginx.  First start nginx through k8s:

  ```
  % cd /opt/kubernetes
  % cluster/kubectl.sh run-container my-nginx --image=dockerfile/nginx --replicas=2 --port=80
  ```

Wait for k8s to deploy nginx.  Poll `% cluster/kubectl.sh get pods` until the pods' status is in the `Running` state.

Now see if you can see the nginx welcome page: `% curl http://10.0.0.2:80`

4. To remove the test cluster, use `$ ./dk8s.py --rm`

# Troubleshooting

In this local setup, Kubernetes and Docker may try to claim IP addresses in the
same range.  You may need to change `hack/local-up-cluster.sh` to use `--portal_net="10.100.0.0/16"` as noted
in [the k8s docs](https://github.com/GoogleCloudPlatform/kubernetes/blob/master/docs/getting-started-guides/locally.md#i-cant-reach-service-ips-on-the-network).

# References
* https://github.com/ghodss/kubernetes-macosx-development
* https://github.com/GoogleCloudPlatform/kubernetes/blob/master/docs/getting-started-guides/locally.md
* https://github.com/GoogleCloudPlatform/golang-docker/blob/master/base/Dockerfile
* https://github.com/jpetazzo/dind

