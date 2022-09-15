# Charmed Clock

World's first cloud native clock powered by Charmed Operator Framework.

# Installation
```shell
git clone https://github.com/weiiwang01/clock-k8s.git
cd clock-k8s
charmcraft pack
juju deploy ./clock-k8s_ubuntu-20.04-amd64.charm --resource node-image=node:latest

juju deploy nginx-ingress-integrator
juju add-relation nginx-ingress-integrator clock-k8s
```

# Usage
```
$ curl -H "Host: clock-k8s" http://127.0.0.1
Thu Sep 15 2022 02:42:18 GMT+0000 (Coordinated Universal Time)
```
