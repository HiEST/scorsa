# scorsa

Scheduler and orchestration simulator for Intel's [Rack Scale
Architecture][rackscale].

## Tools

- `bin/scorsa_sched.py`: Simulate the execution of a workload; requires a system
  configuration, a layout, and a workload description.
- `bin/scorsa_plot.py`: Plot a workload schedule; requires a system
  configuration, a workload description, a schedule file, and a stats file.
- `bin/swf2workload.py`: Convert SWF log to scorsa's workload file format.
- `bin/gen_layout.py`: Generate layout files.
- `bin/test_distance.py`: Generate distance tables between sockets for a given
  layout.

## Data

- `data/ricc-1272889970+1d.json`: Sample workload for testing, based on the
  [RICC workload][ricc] from the Parallel Workloads Archive.

## Usage

Executing the simulator involves running `bin/scorsa_sched.py` as follows:

```
./bin/scorsa_sched.py -c etc/sample-config.ini -w data/ricc-1272889970+1d.json \
    -l etc/layout-2r-064.csv
```

For convenience, you can achieve the same outcome of the above command line by just running the bash script `run.sh`:

```
source run.sh
```

Which ganerates three JSON files in the current directory: `metrics.json`, `schedule.json` and `stats.json`. The file `metrics.json` contains the distance and fragmentation summary of the simulation (the same information is printed on the console), `schedule.json` contains the result of the scheduled simulation itself, while the `stats.json` contains additional statistics of the system collected during the execution. These files can be used to visualize the simulation as follows:

```
./bin/scorsa_plot.py -c etc/sample-config.ini -w data/ricc-1272889970+1d.json \
    -s schedule.json -t stats.json
```

For convenience, you can achieve the same outcome of the above command line by just running the bash script `plot.sh`:

```
source plot.sh
```



## Formats

### Layout File

A CSV file containing the layout of sockets in the system. Each socket has a
unique integer identifier. Sleds can be denoted as a set of sockets separated
by «`+`». Drawers are denoted by rows containing «`--`», while racks are
denoted by columns separated by «`|`». Empty slots can be identified with a
`-1`. E.g.:

```
00,01,|,06,|,09
--,--,|,--,|,--
02,03,|,07,|,-1
04,05,|,08,|,-1
```

Generation of layouts can be automated using `bin/gen_layout.py`. A layout of 32
sockets in 2 racks, with 4 drawers per rack, and 2 sockets per sled:

```
$ ./bin/gen-layout -n 32 -r 2 -d 4 -s 2
00+01,02+03,|,16+17,18+19
-----,-----,|,-----,-----
04+05,06+07,|,20+21,22+23
-----,-----,|,-----,-----
08+09,10+11,|,24+25,26+27
-----,-----,|,-----,-----
12+13,14+15,|,28+29,30+31
```

### Workload File

A JSON file containing an list of jobs with the following schema:

```
[
   {
      "id" : ID,
      "arrival" : ARRIVAL,
      "tasks" : TASKS,
      "mem" : MEM,
      "scale" : SCALE,
      "color" : COLOR,
      "times" : TIME
   },
   ...
]

```

Where:

- ID is a unique string, which can be an incremental number, e.g. `"1"`.
- ARRIVAL is a float in the range between 0.0 and the simulator's maximum
  length as defined in the configuration file, e.g. `2.0`.
- TASKS is an unsigned integer, e.g. `64`. TASKS represents the number of
  tasks that the job can execute concurrently. It's used to determine the
  number of sockets that the job requires (generally one core per task).
- MEM is an unsigned integer, e.g. `16`. It stands for the amount of memory
  that the job requires, in MiB.
- SCALE is a string with one of the following values: `"no"` (job doesn't
  scale), `"up"` (job scales-up), `"out"` (job scales-out), `"both"` (job
  scales up and out).
- COLOR is a color in hex code, e.g. `"#79F1F2"`.
- TIME is a the execution times in seconds, e.g `3200.0`.

### Schedule File

A JSON file containing a dict indexed by job IDs with the following schema:

```
{
   ID : {
      "start" : TIME,
      "end" : TIME,
      "family" : FAMILY,
      "nodes" : NODES,
      "reused" : REUSED
   },
   ...
}
```

Where:

- TIME can be a float in the range between 0.0 and the simulator's maximum
  length as defined in the configuration file, e.g. 4.0. `"start"` and `"end"`
  denote the points in time in which a particular job started running and
  completed its execution, respectively.
- FAMILY is a family name as defined by the configuration file, e.g.
  `xeon-e7-v2`.
- NODES is a list of nodes containing the sockets assigned to the job. Each
  node is a list of unique socket identifiers. E.g. `[ [SOCKET, SOCKET],
  [SOCKET, SOCKET], ...  ]`.
- REUSED is a boolean that is set to `false` when the nodes for the job are
  created from scracth, and `true` when the nodes already existed and have
  been reused.

## Environment

SCORSA uses Python 3.6. [Conda](https://docs.conda.io/en/latest/) allows you to have different environments installed on your computer to access different versions of Python and different libraries. Sometimes libraries conflict which causes errors and packages not to work. To avoid conflicts, we created an environment specifically for this simulator that contains all of the libraries that you will need.

To install the SCORSA environment, you will need to follow these steps:

1. Fork and clone the Github repository. This repository contains a file called [environment.yml](environment.yml) that is needed for the installation. 
2. Open the Terminal on your computer (e.g. Git Bash for Windows or Terminal on a Mac/Linux).
3. In the Terminal, navigate to the SCORSA directory, then, type in the Terminal: ```conda env create -f environment.yml```

## Maintainers

Jordà Polo `<jorda.polo@bsc.es>`, 2016.

[rackscale]: http://www.intel.com/content/www/us/en/architecture-and-technology/intel-rack-scale-architecture.html "rackscale"
[ricc]: http://www.cs.huji.ac.il/labs/parallel/workload/l_ricc/index.html "The RICC Log"
