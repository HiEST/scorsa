# scorsa

Scheduler and orchestration simulator for Intel's [Rack Scale
Architecture][rackscale].

## Tools

- `bin/scorsa-sched`: Simulate the execution of a workload; requires a system
  configuration, and a workload description.
- `bin/scorsa-plot`: Plot a workload schedule; requires a system
  configuration, a workload description, and a schedule.
- `bin/swf2workload`: Convert SWF log to scorsa's workload file format.

## Data

- `data/sample-workload.json`: Sample workload for testing.

## Formats

### Layout File

A CSV file containing the layout of CPUs in the system. Each CPU has a unique
integer identifier. Racks are denoted by columns separated by «`|`», while
drawers are denoted by rows separated by «`--`». Empty slots are identified
with a `-1`. E.g.:

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
      "color" : COLOR,
      "times" : TIMES
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
  number of CPUs that the job requires (generally one core per task).
- MEM is an unsigned integer, e.g. `16`. It stands for the amount of memory
  that the job requires, in MiB.
- COLOR is a color in hex code, e.g. `"#79F1F2"`.
- TIMES is a dictionary that describes the performance model of the job. It's
  indexed by family names (e.g. `xeon-e7-v2`, `atom`), and each entry is a
  dictionary that includes execution times in seconds for different
  configurations of numbers of CPUs per node, e.g.:
```
"xeon-e7-v2" : {
   "1" : 100.0,
   "2" : 120.0,
   "4" : 200.0,
}
```

### Schedule File

A JSON file containing a dict indexed by job IDs with the following schema:

```
{
   ID : {
      "start" : TIME,
      "end" : TIME,
      "family" : FAMILY,
      "nodes" : INT,
      "cpus" : INT,
   },
   ...
}
```

Where:

- `"start"` and `"end"` denote the points in time in which a particular job
  started running and completed its execution, respectively.  TIME can be a
  float in the range between 0.0 and the simulator's maximum length as defined
  in the configuration file, e.g. 4.0.
- FAMILY is a family name as defined by the configuration file, e.g.
  `xeon-e7-v2`.
- `"nodes"` and `"cpus"` are unsigned integers. The former denotes how many
  composed nodes were used to run the job, while the latter denotes the amount
  of CPUs that make up the nodes.

## Maintainers

Jordà Polo `<jorda.polo@bsc.es>`, 2016.

[rackscale]: http://www.intel.com/content/www/us/en/architecture-and-technology/intel-rack-scale-architecture.html "rackscale"
