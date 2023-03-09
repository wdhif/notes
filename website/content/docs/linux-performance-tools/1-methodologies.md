+++
title = "1. Methodologies"
description = " "
weight = 1
+++

# Methodologies

There are dozens of performance tools for Linux 
* Packages: sysstat, procps, coreutils, ...
* Commercial products 
Methodologies can provide guidance for choosing and using tools effectively, by giving you a starting point, a process, and an ending point in your diagnotics.

## Problem Statement Method

1. What makes you **think** there is a performance problem?
2. Has this system **ever** performed well?
3. What has **changed** recently? (Software? Hardware? Load?) 
4. Can the performance degradation be expressed in terms of **latency** or run time?
5. Does the problem affect **other** people or applications (or is it just you)?
6. What is the **environment**? Software, hardware, instance types? Versions? Configuration?

## Workload Characterization Method

1. **Who** is causing the load? PID, UID, IP addr, ...
2. **Why** is the load called? code path, stack trace
3. **What** is the load? IOPS, throughput, type, r/w
4. **How** is the load changing over time?

## The USE Method

For every resource, check:
1. Utilization: Busy
2. Saturation
3. Errors