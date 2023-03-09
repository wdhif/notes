+++
title = "2. Tools"
description = " "
weight = 2
+++

# Tools

There are dozens of performance tools for Linux 
* Packages: sysstat, procps, coreutils, ...
* Commercial products 
Methodologies can provide guidance for choosing and using tools effectively, by giving you a starting point, a process, and an ending point in your diagnotics.

## Command Line Tools

Useful to study even if you never use them: GUIs and commercial products often use the same interfaces.

**Tool Types**

| Type          | Characteristic                                                           |
|---------------|--------------------------------------------------------------------------|
| Observability | Watch activity. Usually safe, depending on resource overhead.            |
| Benchmarking  | Load test. Caution: production tests can cause issues due to contention. |
| Tuning        | Change. Danger: changes could hurt performance, now or later with load.  |
| Static        | Check configuration. Should be safe                                      |


## Observability Tools

Basic Observability Tools:
* uptime
* top (or htop)
* ps
* vmstat
* iostat
* mpstat
* free

### uptime

* One way to print *load averages*:
```
$ uptime
07:42:06 up 8:16, 1 user, load average: 2.27, 2.84, 2.91
```
* A measure of resource demand: CPUs + disks
* * Other OSes only show CPUs: easier to interpret
* Exponentially-damped moving averages
* Time constants of 1, 5, and 15 minutes
* * Allow to have an historic trend without a line graph
* If the load is larger than the number of CPUs, it may indicate CPU saturation
* * Don’t spend more than 5 seconds studying these

### top (or htop)

* System and per-process interval summary:
```
$ top - 18:50:26 up 7:43, 1 user, load average: 4.11, 4.91, 5.22
Tasks: 209 total, 1 running, 206 sleeping, 0 stopped, 2 zombie
Cpu(s): 47.1%us, 4.0%sy, 0.0%ni, 48.4%id, 0.0%wa, 0.0%hi, 0.3%si, 0.2%st
Mem: 70197156k total, 44831072k used, 25366084k free,    36360k buffers
Swap:       0k total,        0k used,        0k free, 11873356k cached
 PID  USER    PR NI  VIRT  RES   SHR S %CPU %MEM   TIME+ COMMAND 
 5738 apiprod 20  0 62.6g  29g  352m S  417 44.2 2144:15 java
 1386 apiprod 20  0 17452 1388   964 R    0  0.0 0:00.02 top
    1 root    20  0 24340 2272  1340 S    0  0.0 0:01.51 init
    2 root    20  0     0    0     0 S    0  0.0 0:00.00 kthreadd
[…]
```
* `%CPU` is summed across all CPUs
* Can miss short-lived processes (`atop` won’t)
* Can consume noticeable CPU to read `/proc`

### ps

* Process status listing (eg, “ASCII art forest”): 

* Custom fields:

 