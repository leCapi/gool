# gool

<!-- [![Release](https://img.shields.io/github/v/release/leCapi/gool)](https://img.shields.io/github/v/release/leCapi/gool)
[![Build status](https://img.shields.io/github/actions/workflow/status/leCapi/gool/main.yml?branch=main)](https://github.com/leCapi/gool/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/leCapi/gool)](https://img.shields.io/github/commit-activity/m/leCapi/gool)
[![License](https://img.shields.io/github/license/leCapi/gool)](https://img.shields.io/github/license/leCapi/gool) -->

gool is a cli logs clustering tool using drain3 library. It takes one or more log files as input and output clusters of your logs.

The user can tune some settings to build right size clusters :

- **similarity-threshold** :
  drain3 parameter (default 0.4) between 0 and 1. Value of 1 will lead to cluster with the same exact lines only. The higher, the more clusters you will get. This setting can be tunned in configuration file or on command line.
- **tree-depth** :
  drain3 parameter (default 4) which high value lead to more clusters. This setting can be tunned in configuration file or on command line.
- **pattern masking** :
  drain3 parameter to mask pattern so lines can be group easier. For example we can replace all IP, or time before processing. This setting can only be tunned in configuration file.
- **filter** :
  filter to only parse some of the line of the input files. For example if the user is focuses on error we can imagine something like : '.*(\| Warning |\| Error ).*'.

For more details on drain3 parameters check the official repository :
https://github.com/logpai/Drain3.

Launch gool (config taken in ~/.drain3.ini):
```
gool tests/data/log/Zookeeper_2k.log
```

Launch gool and filter lines before processing (config taken in ~/.drain3.ini):
```
gool tests/data/log/Zookeeper_2k.log -f ".*WARN.*"
```
which produces something like :
```
11:34:48.805482 INFO     log_clustering : Loading configuration from /home/godardo/.drain3.ini                                                       log_clustering.py:111
11:34:48.829732 INFO     log_clustering : Processed 1318 lines in 0.02 seconds (64798.84 lines/second).                                              log_clustering.py:226
Zookeeper_2k.log ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
                                                                               Log Clusters
┏━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Count ┃ Char Size (KB) ┃ Template                                                                                                                                      ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   313 │             43 │ 2015-07-29 <TIME> - WARN [SendWorker:188978561024:QuorumCnxManager$SendWorker@679] - Interrupted while waiting for message on queue           │
│   289 │             43 │ 2015-07-29 <TIME> - WARN [RecvWorker:188978561024:QuorumCnxManager$RecvWorker@762] - Connection broken for id 188978561024, my id = <*> error │
│       │                │ =                                                                                                                                             │
│   265 │             30 │ 2015-07-29 <TIME> - WARN [RecvWorker:188978561024:QuorumCnxManager$RecvWorker@765] - Interrupting SendWorker                                  │
│   262 │             31 │ 2015-07-29 <TIME> - WARN <*> - Send worker leaving thread                                                                                     │
│    45 │              7 │ <*> <TIME> - WARN [QuorumPeer[myid=1]/0:0:0:0:0:0:0:0:2181:QuorumCnxManager@368] - Cannot open channel to 2 at election address /<IP>:3888    │
│    39 │              7 │ <*> <TIME> - WARN [NIOServerCxn.Factory:<IP>/<IP>:2181:ZooKeeperServer@793] - Connection request from old client <*> will be dropped if       │
│       │                │ server is in r-o mode                                                                                                                         │
│    37 │              4 │ <*> <TIME> - WARN [NIOServerCxn.Factory:<IP>/<IP>:2181:NIOServerCnxn@349] - caught end of stream exception                                    │
│    22 │              3 │ 2015-08-25 <TIME> - WARN <*> - Cannot open channel to 3 at election address /<IP>:3888                                                        │
│    14 │              2 │ 2015-08-24 <TIME> - WARN <*> - Cannot open channel to 3 at election address /<IP>:3888                                                        │
│     3 │              0 │ 2015-07-30 <TIME> - WARN [WorkerSender[myid=1]:QuorumCnxManager@368] - Cannot open channel to <*> at election address /<IP>:3888              │
│     3 │              0 │ 2015-08-20 <TIME> - WARN [NIOServerCxn.Factory:<IP>/<IP>:2181:NIOServerCnxn@354] - Exception causing close of session <HEX> due to            │
│       │                │ java.io.IOException: ZooKeeperServer not running                                                                                              │
│     1 │              0 │ 2015-07-30 <TIME> - WARN [LearnerHandler-/<IP>:35276:LearnerHandler@575] - ******* GOODBYE /<IP>:35276 ********                               │
│     1 │              0 │ 2015-07-30 <TIME> - WARN [RecvWorker:3:QuorumCnxManager$RecvWorker@765] - Interrupting SendWorker                                             │
│     1 │              0 │ 2015-08-25 <TIME> - WARN [RecvWorker:3:QuorumCnxManager$RecvWorker@762] - Connection broken for id 3, my id = 1, error =                      │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:52264:LearnerHandler@575] - ******* GOODBYE /<IP>:52264 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:52308:LearnerHandler@575] - ******* GOODBYE /<IP>:52308 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:59060:LearnerHandler@575] - ******* GOODBYE /<IP>:59060 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:59103:LearnerHandler@575] - ******* GOODBYE /<IP>:59103 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:57247:LearnerHandler@575] - ******* GOODBYE /<IP>:57247 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:57319:LearnerHandler@575] - ******* GOODBYE /<IP>:57319 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:52476:LearnerHandler@575] - ******* GOODBYE /<IP>:52476 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:59203:LearnerHandler@575] - ******* GOODBYE /<IP>:59203 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:59211:LearnerHandler@575] - ******* GOODBYE /<IP>:59211 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:52502:LearnerHandler@575] - ******* GOODBYE /<IP>:52502 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:57458:LearnerHandler@575] - ******* GOODBYE /<IP>:57458 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:57502:LearnerHandler@575] - ******* GOODBYE /<IP>:57502 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:52703:LearnerHandler@575] - ******* GOODBYE /<IP>:52703 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:59406:LearnerHandler@575] - ******* GOODBYE /<IP>:59406 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:57580:LearnerHandler@575] - ******* GOODBYE /<IP>:57580 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:52818:LearnerHandler@575] - ******* GOODBYE /<IP>:52818 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:52844:LearnerHandler@575] - ******* GOODBYE /<IP>:52844 ********                               │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [LearnerHandler-/<IP>:57653:LearnerHandler@575] - ******* GOODBYE /<IP>:57653 ********                               │
│     1 │              0 │ 2015-07-31 <TIME> - WARN [SendWorker:1:QuorumCnxManager$SendWorker@679] - Interrupted while waiting for message on queue                      │
│     1 │              0 │ 2015-08-07 <TIME> - WARN [QuorumPeer[myid=2]/0:0:0:0:0:0:0:0:2181:QuorumCnxManager@368] - Cannot open channel to 3 at election address        │
│       │                │ /<IP>:3888                                                                                                                                    │
│     1 │              0 │ 2015-08-20 <TIME> - WARN [LearnerHandler-/<IP>:42241:Leader@576] - First is <HEX>                                                             │
│     1 │              0 │ 2015-07-29 <TIME> - WARN [WorkerSender[myid=3]:QuorumCnxManager@368] - Cannot open channel to 2 at election address /<IP>:3888                │
│     1 │              0 │ 2015-07-30 <TIME> - WARN [RecvWorker:1:QuorumCnxManager$RecvWorker@762] - Connection broken for id 1, my id = 3, error =                      │
└───────┴────────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

More option details with :
```
gool --help
```
