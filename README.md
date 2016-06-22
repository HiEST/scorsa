# scorsa

Scheduler and orchestration simulator for Intel's [Rack Scale
Architecture][rackscale].

## Tools

- `bin/scorsa-sched`: Schedule a workload on a system; requires a system
  configuration, and a workload to run.

## Data

- `data/sample-workload.json`: Sample workload for testing.

## Formats

### Workload File

A JSON file containing an array of jobs with the following schema:


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
  length as defined in the configuration file `config.ini`, e.g. `2.0`.
- TASKS is an unsigned integer, e.g. `64`. TASKS represents the number of
  tasks that the job can execute concurrently. It's used to determine the
  number of CPUs that the job requires (generally one core per task).
- MEM is an unsigned integer, e.g. `16`. It stands for the amount of memory
  that the job requires, in MiB.
- COLOR is a color in hex code, e.g. `"#79F1F2"`.
- TIMES is a dictionary that describes the performance model of the job. It's
  indexed by family names (e.g. xeon-e7-v2, atom), and each entry is a
  dictionary that includes execution times in seconds for different
  configurations of numbers of CPUs per node, e.g:
```
"xeon-e7-v2" : {
   "1" : 100.0,
   "2" : 120.0,
   "4" : 200.0,
}
```

## Maintainers

Jordà Polo `<jorda.polo@bsc.es>`, 2016.

[rackscale]: http://www.intel.com/content/www/us/en/architecture-and-technology/intel-rack-scale-architecture.html "rackscale"
