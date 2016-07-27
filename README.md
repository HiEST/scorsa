# scorsa

Scheduler and orchestration simulator for Intel's [Rack Scale
Architecture][rackscale].

## Tools

- `bin/scorsa-sched`: Simulate the execution of a workload; requires a system
  configuration, a layout, and a workload description.
- `bin/scorsa-plot`: Plot a workload schedule; requires a system
  configuration, a workload description, a schedule file, and a stats file.
- `bin/swf2workload`: Convert SWF log to scorsa's workload file format.
- `bin/gen-layout`: Generate layout files.
- `bin/test-distance`: Generate distance tables between sockets for a given
  layout.

## Data

- `data/ricc-1272889970+1d.json`: Sample workload for testing, based on the
  [RICC workload][ricc] from the Parallel Workloads Archive.

## Usage

Executing the simulator involves running `bin/scorsa-sched` as follows:

```
./bin/scorsa-sched -c etc/sample-config.ini -w data/ricc-1272889970+1d.json \
    -l etc/layout-2r-064.csv
```

Which ganerates two JSON files in the current directory: `schedule.json` and
`stats.json`. The former contains the result of the scheduled simulation
itself, while the latter contains additional stats of the system collected
during the execution. These files can be used to visualize the simulation as
follows:

```
./bin/scorsa-plot -c etc/sample-config.ini -w data/ricc-1272889970+1d.json \
    -s schedule.json -t stats.json
```

## Formats

### Layout File

A CSV file containing the layout of sockets in the system. Each socket has a
unique integer identifier. Racks are denoted by columns separated by «`|`»,
while drawers are denoted by rows separated by «`--`». Empty slots are
identified with a `-1`. E.g.:

```
00,01,|,06,|,09
--,--,|,--,|,--
02,03,|,07,|,-1
04,05,|,08,|,-1
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
      "nodes" : NODES
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

## Maintainers

Jordà Polo `<jorda.polo@bsc.es>`, 2016.

[rackscale]: http://www.intel.com/content/www/us/en/architecture-and-technology/intel-rack-scale-architecture.html "rackscale"
[ricc]: http://www.cs.huji.ac.il/labs/parallel/workload/l_ricc/index.html "The RICC Log"
