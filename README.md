# gool

## Usage

gool is a cli logs clustering tool using drain3 library. It takes one or more log files as input and output clusters of your logs.

The user can tune some settings to build right size clusters :

- **similarity-threshold** :
  drain3 parameter (default 0.4) between 0 and 1. Value of 1 will lead to cluster with the same exact lines only. The higher, the more clusters you will get. This setting can be tunned in configuration file or on command line.
- **tree-depth** :
  drain3 parameter (default 4) which high value lead to more clusters. This setting can be tunned in configuration file or on command line.
- **pattern masking** :
  drain3 parameter to mask pattern so lines can be group easier. For example we can replace all IPs, or times before processing. This setting can only be tunned in configuration file.
- **filter** :
  filter to only parse some of the line of the input files. For example if the user is focuses on error we can imagine something like : '.\*(\| Warning |\| Error ).\*'.
- **time_max** :
  max time of log lines, line with higher timestamp are discarded
- **time_max** :
  max time of log lines, line with higher timestamp are discarded
- **time_pattern**:
  pattern used to capture timestamp of each log line. Default will be "(\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?)".
- **time_format**:
  Format code (for strptime) of the time extracted of each line to convert string into datetime to allow filtering. By default, it will be "%H:%M:%S.%f" or "%H:%M:%S".
- **baseline**:
  Generate another cluster as a baseline to compare with it.

For more details on drain3 parameters check the official repository :
https://github.com/logpai/Drain3.

Launch gool (config taken in ~/.drain3.ini):

```bash
gool tests/data/log/Zookeeper_2k.log
```

Launch gool and filter lines before processing (config taken in ~/.drain3.ini):

```bash
gool tests/data/log/Zookeeper_2k.log -f ".*WARN.*"
```

```bash
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

Launch gool and filter lines on specified time :

```bash
gool   /home/godardo/git/gool/tests/data/log/Apache_2k.log --time_format '%a %b %d %H:%M:%S %Y' --time_pattern '(\w{3} \w{3} \d{2} \d{2}:\d{2}:\d{2} \d{4})' --time_min 'Mon Dec 05 18:46:00 2005' --time_max 'Mon Dec 05 19:00:00 2005'
```

```bash
22:59:35.061049 INFO     log_clustering : Loading configuration from /home/godardo/.drain3.ini                                                                                                                                                                                log_clustering.py:266
22:59:35.069775 INFO     log_clustering : Running clustering.                                                                                                                                                                                                                 log_clustering.py:575
22:59:35.091847 INFO     logs_miner : Reached a log line with time after the specified maximum time. Stopping processing further lines.                                                                                                                                           logs_miner.py:155
22:59:35.092984 INFO     logs_miner : Processed 9 lines in 0.02 seconds (470.37 lines/second).                                                                                                                                                                                    logs_miner.py:164
Apache_2k.log ━━━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   9%
                                                  Log Clusters
┏━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Count ┃ Char Size (KB) ┃ Template                                                                             ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│     3 │              0 │ [Mon Dec 05 <TIME>] [notice] workerEnv.init() ok /etc/httpd/conf/workers2.properties │
│     3 │              0 │ [Mon Dec 05 <TIME>] [error] mod jk child workerEnv in error state 6                  │
│     2 │              0 │ [Mon Dec 05 <TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 8         │
│     1 │              0 │ [Mon Dec 05 <TIME>] [notice] jk2 init() Found child 6740 in scoreboard slot 7        │
└───────┴────────────────┴──────────────────────────────────────────────────────────────────────────────────────┘
```

Compare logs with a baseline :

```bash
gool /home/godardo/git/gool/tests/data/log/Apache_2K_MonDec05.log  --display_common --baseline /home/godardo/git/gool/tests/data/log/Apache_2K_SunDec04.log
```

```bash
23:04:06.371468 INFO     log_clustering : Loading configuration from /home/godardo/git/gool/tests/data/drain3_compare_baseline.ini                                                                                                                                            log_clustering.py:266
23:04:06.374091 INFO     log_clustering : Running clustering.                                                                                                                                                                                                                 log_clustering.py:575
23:04:06.389677 INFO     logs_miner : Processed 949 lines in 0.01 seconds (80002.33 lines/second).                                                                                                                                                                                logs_miner.py:164
Apache_2K_MonDec05.log ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
23:04:06.391483 INFO     log_clustering : Running baseline clustering.                                                                                                                                                                                                        log_clustering.py:588
23:04:06.406525 INFO     logs_miner : Processed 1051 lines in 0.01 seconds (79220.32 lines/second).                                                                                                                                                                               logs_miner.py:164
Apache_2K_SunDec04.log ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100%
                         Missing from baseline
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Template                                                            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ [<TIME>] [notice] jk2 init() Found child 1568 in scoreboard slot 13 │
│ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 11  │
└─────────────────────────────────────────────────────────────────────┘
                         Added from baseline
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Template                                                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 13 │
└────────────────────────────────────────────────────────────────────┘
                                Common with baseline
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Template                                                                         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ [<TIME>] [error] [client <IP>] Directory index forbidden by rule: /var/www/html/ │
│ [<TIME>] [error] jk2 init() Can't find child <*> in scoreboard                   │
│ [<TIME>] [error] mod jk child init 1 -2                                          │
│ [<TIME>] [error] mod jk child workerEnv in error state <*>                       │
│ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 10               │
│ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 12               │
│ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 6                │
│ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 7                │
│ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 8                │
│ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 9                │
│ [<TIME>] [notice] workerEnv.init() ok /etc/httpd/conf/workers2.properties        │
└──────────────────────────────────────────────────────────────────────────────────┘

                                            Baseline Log Clusters
┏━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Count ┃ Char Size (KB) ┃ Template                                                                         ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   298 │             27 │ [<TIME>] [notice] workerEnv.init() ok /etc/httpd/conf/workers2.properties        │
│   281 │             21 │ [<TIME>] [error] mod jk child workerEnv in error state <*>                       │
│    94 │              8 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 6                │
│    93 │              7 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 8                │
│    89 │              7 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 7                │
│    87 │              7 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 9                │
│    59 │              5 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 10               │
│    18 │              1 │ [<TIME>] [error] [client <IP>] Directory index forbidden by rule: /var/www/html/ │
│    16 │              1 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 11               │
│     6 │              0 │ [<TIME>] [error] jk2 init() Can't find child <*> in scoreboard                   │
│     6 │              0 │ [<TIME>] [error] mod jk child init 1 -2                                          │
│     3 │              0 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 12               │
│     1 │              0 │ [<TIME>] [notice] jk2 init() Found child 1568 in scoreboard slot 13              │
└───────┴────────────────┴──────────────────────────────────────────────────────────────────────────────────┘

                                                Log Clusters
┏━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Count ┃ Char Size (KB) ┃ Template                                                                         ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│   271 │             24 │ [<TIME>] [notice] workerEnv.init() ok /etc/httpd/conf/workers2.properties        │
│   258 │             19 │ [<TIME>] [error] mod jk child workerEnv in error state <*>                       │
│   105 │              8 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 7                │
│   101 │              8 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 8                │
│    95 │              8 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 6                │
│    73 │              6 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 9                │
│    16 │              1 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 10               │
│    14 │              1 │ [<TIME>] [error] [client <IP>] Directory index forbidden by rule: /var/www/html/ │
│     6 │              0 │ [<TIME>] [error] jk2 init() Can't find child <*> in scoreboard                   │
│     6 │              0 │ [<TIME>] [error] mod jk child init 1 -2                                          │
│     2 │              0 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 12               │
│     2 │              0 │ [<TIME>] [notice] jk2 init() Found child <*> in scoreboard slot 13               │
└───────┴────────────────┴──────────────────────────────────────────────────────────────────────────────────┘
```

More option details with :

```bash
gool --help
```

## Example of a drain3.ini file

gool try to load .drain3 file from your home. Otherwise you can use **--cfg-file** option. Without any configuration, gool will try to mask HEX, IPs and times.

Below an example of configuration file :

``` ini
[MASKING]
masking = [
    {"regex_pattern":"((?<=[^A-Za-z0-9])|^)(0[xX][0-9a-fA-F]+)((?=[^A-Za-z0-9])|$)", "mask_with": "HEX"},
    {"regex_pattern":"(\\d{2}:\\d{2}:\\d{2}(.\\d+|))", "mask_with": "TIME"},
    {"regex_pattern":"((?<=[^A-Za-z0-9])|^)(\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3})((?=[^A-Za-z0-9])|$)", "mask_with": "IP"}
    ]
mask_prefix = <:
mask_suffix = :>

[DRAIN]
sim_th = 0.9
depth = 7
max_children = 200
extra_delimiters = ["_"]

```

## Source Setup

The gool repository uses uv and git. Version is taken from git tag. The repo provide setup for VSCode.

Below the more useful commands.

Setup the uv virtual environment and install pre-commit hooks :

```bash
make install
```

Non regression tests on all supported environments :

```bash
tox -p
```

Generate and launch the documentation server :

```bash
make docs
```

All available commands :

```bash
make help
```

---

Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).
