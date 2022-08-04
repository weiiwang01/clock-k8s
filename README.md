# Charmed Clock

World's first cloud native clock powered by Charmed Operator Framework.

# Installation
```shell
git clone https://github.com/weiiwang01/clock-k8s.git
cd clock-k8s
charmcraft pack
juju deploy ./clock-k8s_ubuntu-20.04-amd64.charm --resource node-image=node:latest
```

# Usage
Use Juju action to check time
```
$ juju run-action clock-k8s/0 get-time
Action queued with id: "2"

$ juju show-action-output 2
UnitId: clock-k8s/0
id: "2"
results:
  time: Thu Aug 04 2022 03:06:02 GMT+0000 (Coordinated Universal Time)
status: completed
timing:
  completed: 2022-08-04 03:06:03 +0000 UTC
  enqueued: 2022-08-04 03:06:03 +0000 UTC
  started: 2022-08-04 03:06:03 +0000 UTC
  
$ juju config clock-k8s timezone=Africa/Addis_Ababa

$ juju run-action clock-k8s/0 get-time
Action queued with id: "6"

$ juju show-action-output 6
UnitId: clock-k8s/0
id: "6"
results:
  time: Thu Aug 04 2022 06:15:39 GMT+0300 (East Africa Time)
status: completed
timing:
  completed: 2022-08-04 03:15:40 +0000 UTC
  enqueued: 2022-08-04 03:15:38 +0000 UTC
  started: 2022-08-04 03:15:39 +0000 UTC
```
