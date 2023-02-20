+++
title = "4. Process Scheduling"
description = " "
weight = 4
+++

### The Scheduler

**The process scheduler decides which process runs, when, and for how long.**

The process scheduler (or simply the scheduler, to which it is often shortened) divides the finite resource of processor time between the runnable processes on a system. By deciding which process runs next, the scheduler is responsible for best utilizing the system and giving users the impression that multiple processes are executing simultaneously, AKA **Multitasking**.

The ideas behind the scheduler are simple:
* To best utilize processor time, assuming there are runnable processes, **a process should always be running**.
* If there are more runnable processes than processors in a system, some processes will not be running at a given moment. These processes are **waiting to run**.
* **Deciding which process runs next**, given a set of runnable processes, is the fundamental decision that the scheduler must make.

### Multitasking

A multitasking operating system is one that can simultaneously interleave execution of more than one process.
* **On single processor machines**, this gives the illusion of multiple processes running concurrently.
* **On multiprocessor machines**, such functionality enables processes to actually run concurrently, in parallel, on different processors.

On either type of machine, it also enables many processes to **block** or **sleep**, not actually executing until work is available.
**These processes, although in memory, are not runnable.**
Instead, such processes utilize the kernel to wait until some event (keyboard input, network data, passage of time, and so on) occurs.

Multitasking operating systems come in two flavors:
* **cooperative multitasking**: A process does not stop running until it voluntary decides to do so, it is called **yielding**. Ideally, processes yield often, giving each runnable process a decent chunk of the processor.
* **preemptive multitasking**: The scheduler decides when a process is to cease running and a new process is to begin running, it is called **preemption**. The time a process runs before it is preempted is usually predetermined, and it is called the **timeslice of the process**. The process is given a **slice** of processor's time to run.

The shortcomings of the **cooperative multitasking** approach are manifest, the scheduler cannot make global decisions regarding how long processes run. Processes can monopolize the processor for longer than the user desires, and a hung process that never yields can potentially bring down the entire system.

On **preemptive multitasking**, the scheduler manage each process timeslices, making global decisions for the system (e.g. priorization) and preventing any one process from monopolizing the processor.
The timeslice is dynamically calculated as a function of process behavior and configurable system policy.

**Linux, like all Unix variants and most modern operating systems, implements preemptive multitasking.**

### Linux's Process Scheduler

The current Linux scheduler is the **Completely Fair Scheduler**, or **CFS**. The **CFS** was introduced as a replacement for the **O(1)** scheduler, which was performant, but was lacking when dealing with interactive process, like on a desktop for example.

### Policy

The policy of a scheduler determines what runs when. Therefore it is very important.

### I/O-Bound Versus Processor-Bound Processes

Processes can be classified as two types:
* **I/O-bound**: A process that spend much of its time **waiting on I/O requests** (I/O here means any **blockable resources**, like keyboard inputs or network I/O, not only disk I/O). Such processes are runnable for only short durations before having to wait on requests, like GUI waiting on user inputs.
* **processor-bound**: **Processor-bound processes spend much of their time executing code.** They tend to run until they are **preempted** because they do not block on I/O requests very often.

Linux, aiming to provide good interactive response and desktop performance, optimizes for response time (low latency), thus favoring I/O-bound processes over processor-bound processors.
As we will see, this is done in a creative manner that does not neglect processor-bound processes.

### Process Priority

A common type of scheduling algorithm is priority-based scheduling. The goal is to **rank** processes based on their worth and need for processor time.
**Processes with a higher priority run before those with a lower priority**, whereas **processes with the same priority are scheduled in round-robin** (one after the next, repeating).

**The runnable process with timeslice remaining and the highest priority always runs.** Both the user and the system can set a process’s priority to influence the scheduling behavior of the system.

The Linux kernel implement two priority ranges:
* **Niceness**: A number from **-20 to +19 with a default at 0**. Larger nice values correspond to a lower priority, you are being “nice” to the other processes on the system. **Processes with a lower nice value (higher priority) receive a larger proportion of the system’s processor compared to processes with a higher nice value (lower priority).**
* **Real-time priority**: The values are configurable, but by default range from **0 to 99**, inclusive. **Higher real-time priority values correspond to a greater priority and all real-time processes are at a higher priority than normal processes.** By default, processes are not real-time, their value is "-", or null.

### Timeslice

**The timeslice is the numeric value that represents how long a task can run until it is preempted.** The scheduler policy must dictate a default timeslice, which is not a trivial exercise.
* Too long a timeslice causes the system to have poor interactive performance, the system will no longer feel as if applications are concurrently executed.
* Too short a timeslice causes significant amounts of processor time to be wasted on the overhead of switching processes.

Furthermore, the conflicting goals of I/O-bound versus processor-bound processes again arise:
* I/O-bound processes do not need longer timeslices (although they do like to run often)
* Processor-bound processes crave long timeslices (to keep their caches hot).

**To avoid thoses issues, Linux’s CFS scheduler does not directly assign timeslices to processes.** **Instead, it will assign to processes a proportion of the processor**, therefore, the amount of processor time that a process receives is a function of the load of the system.
**This assigned proportion is further affected by each process’s nice value.** The nice value acts as a weight, changing the proportion of the processor time each process receives.

**When a process enters the runnable state, it becomes eligible to run.** Whether the process runs immediately, preempting the currently running process, is a function of how much of a proportion of the processor the newly runnable processor has consumed.
* If **it has consumed a smaller proportion of the processor than the currently executing process, it runs immediately**, preempting the current process. 
* If not, it is scheduled to run at a later time.

### The Scheduling Policy in Action

Consider two runnable processes:
* **A text editor: I/O-bound.** It will spend nearly all its time waiting for user key presses.
* **A video encoder: Processor-bound.** Aside from waiting on disk to read the video at first, it will then spend all its time encoding the video, consuming 100% of the processor.

The **text editor**, despite spending most of its time waiting on user input, **when the text editor does receive a key press, the user expects the editor to respond immediately**. **Latency is a primary concern.**
The **video encoder doesn't have strong time constraint**, we don't really care if it runs now or at the next CPU cycle. The sooner it finishes the better, but **latency is not a primary concern**.

If both processes are runnable and have the same nicelevel, they would be awarded both with the same proportion of the processor's time. But since the **text editor** spend a lot of time waiting, it would almost always have more processor time left than the **video encoder**. And because of that, **CFS would let the text editor run in priority, therefore limiting latency**.

This will allow the **text editor** to run everytime it's ready, and the **video encoder** to run the rest of the time, assuming no other process needs to run.

### The Linux Scheduling Algorithm

### Scheduler Classes

The Linux scheduler is modular, enabling different algorithms to schedule different types of processes. 
**This modularity is called scheduler classes.** Scheduler classes enable different, pluggable algorithms to coexist, scheduling their own types of processes. Each scheduler class has a priority.

The **base scheduler** code, iterates over each scheduler class in order of priority. **The highest priority scheduler class that has a runnable process wins, selecting who runs next.**
The **Completely Fair Scheduler (CFS) is the registered scheduler class for normal processes**, called **SCHED_NORMAL** in Linux.

### Fair Scheduling

CFS is based on a simple concept: Model process scheduling as if the system had an ideal, perfectly multitasking processor.
**In such a system, each process would receive 1/n of the processor’s time, where n is the number of runnable processes.** We’d schedule them for infinitely small durations, so that in any measurable period we’d have run all n processes for the same amount of time.

### The Linux Scheduling Implementation

### Time Accounting

All process schedulers must account for the time that a process runs. Most Unix systems do so, as discussed earlier, by assigning each process a timeslice.
On each tick of the system clock, the timeslice is decremented by the tick period. **When the timeslice reaches zero, the process is preempted in favor of another runnable process with a nonzero timeslice.**

**CFS does not have the notion of a timeslice, but it must still keep account for the time that each process runs**, because it needs to ensure that each process runs only for its fair share of the processor. This information is embedded in the process descriptor. We discussed the process descriptor in Chapter 3, “Process Management.”

### The Virtual Runtime

**The Virtual Runtime (vruntime) of a process the actual runtime (the amount of time spent running) normalized (or weighted) by the number of runnable processes, in nanoseconds.**
**The Virtual Runtime update is triggered periodically by the system timer and also whenever a process becomes runnable or blocks**, becoming unrunnable. In this manner, vruntime is an accurate measure of the runtime of a given process and an indicator of what process should run next.

### Process Selection

On an ideal processor, the Virtual Runtime of all processes of the same priority would be identical, all tasks would have received an equal, fair share of the processor.
In reality, we cannot perfectly multitask, so CFS attempts to balance a process’s Virtual Runtime with a simple rule: **When CFS is deciding what process to run next, it picks the process with the smallest vruntime.** The CFS maintains a red-black tree for the Virtual Runtimes.

### Preemption and Context Switching

**Context switching, the switching from one runnable task to another, is handled by the scheduler.** It is called when a new process has been selected to run.
It does two basic jobs:
* **Switch the virtual memory mapping** from the previous process’s to that of the new process.
* **Switch the processor state** from the previous process’s to the current’s. This involves saving and restoring stack information and the processor registers and any other architecture-specific state that must be managed and restored on a per-process basis.

**The kernel, however, must know when to call the scheduler.**
If it called it only when code explicitly did so, user-space programs could run indefinitely.

Instead, the kernel provides the need_resched flag to signify whether a reschedule should be performed.
* This flag is set by scheduler_tick() (which is ran by a timer) when a process should be preempted.
* This flag is set by try_to_wake_up() when a process that has a higher priority than the currently running process is awakened.

**Upon returning to user-space or returning from an interrupt, the kernel checks the need_resched flag. If it is set, the kernel invokes the scheduler (using schedule()) before continuing.** The flag is a message to the kernel that the scheduler should be invoked as soon as possible because another process deserves to run.

### User preemption

**User preemption occurs when the kernel is about to return to user-space**, need_resched is set, and therefore, the scheduler is invoked.
If the kernel is returning to user-space, it knows it is safe to continue executing the current task or to pick a new task to execute.

Consequently, whenever the kernel is preparing to return to user-space either on return from an interrupt or after a system call, the value of need_resched is checked. If it is set, the scheduler is invoked to select a new (more fit) process to execute.

User preemption can occur
* When returning to user-space from a system call.
* When returning to user-space from an interrupt handler.

### Kernel Preemption

**The Linux kernel, unlike most other Unix variants and many other operating systems, is a fully preemptive kernel.**
In nonpreemptive kernels, kernel code runs until completion, the scheduler cannot reschedule a task while it is in the kernel.
Kernel code runs until it finishes (returns to user-space) or explicitly blocks. However, the Linux kernel is able to preempt a task at any point, so long as the kernel is in a state in which it is safe to reschedule.

So when is it safe to reschedule? **The kernel can preempt a task running in the kernel so long as it does not hold a lock.** That is, locks are used as markers of regions of nonpreemptibility. If a lock is not held, the current code is reentrant and capable of being preempted.

Kernel preemption can occur
* When an interrupt handler exits, before returning to kernel-space.
* When kernel code becomes preemptible again, when all locks are released.
* If a task in the kernel explicitly calls schedule().
* If a task in the kernel blocks (which results in a call to schedule()).

### Real-Time Scheduling Policies

Linux provides two real-time scheduling policies
* SCHED_FIFO
* SCHED_RR

The normal, not real-time scheduling policy is SCHED_NORMAL (using the CFS). Via the scheduling classes framework, these real-time policies are managed not by the Completely Fair Scheduler, but by a special real-time scheduler.

**SCHED_FIFO implements a simple first-in, first-out scheduling algorithm without timeslices.**

* A runnable SCHED_FIFO task is always scheduled over any SCHED_NORMAL tasks.
* When a SCHED_FIFO task becomes runnable, it continues to run until it blocks or explicitly yields the processor; it has no timeslice and can run indefinitely.
* Only a higher priority SCHED_FIFO or SCHED_RR task can preempt a SCHED_FIFO task.
* Two or more SCHED_FIFO tasks at the same priority run round-robin, but only yielding the processor when they explicitly choose to do so.
* If a SCHED_FIFO task is runnable, all other tasks at a lower priority cannot run until the SCHED_FIFO task becomes unrunnable.

**SCHED_RR is identical to SCHED_FIFO except that each process can run only until it exhausts a predetermined timeslice. In other words, SCHED_RR is SCHED_FIFO with timeslices. It is a real-time, round-robin scheduling algorithm.**

* When a SCHED_RR task exhausts its timeslice, any other real-time processes at its priority are scheduled round-robin. The timeslice is used to allow only rescheduling of same-priority processes.
* As with SCHED_FIFO, a higher-priority process always immediately preempts a lower-priority one, and a lower-priority process can never preempt a SCHED_RR task, even if its timeslice is exhausted.

Both real-time scheduling policies implement static priorities. The kernel does not calculate dynamic priority values for real-time tasks. This ensures that a real-time process at a given priority always preempts a process at a lower priority.

Two types of real-time behavior exists:

* Soft real-time, meaning that the kernel tries to schedule applications within timing deadlines, but the kernel does not promise to always achieve these goals.
* Hard real-time systems are guaranteed to meet any scheduling requirements within certain limits.

**The real-time scheduling policies in Linux provide soft real-time behavior.** Linux makes no guarantees on the capability to schedule real-time tasks. Despite not having a design that guarantees hard real-time behavior, the real-time scheduling performance in Linux is quite good.

Real-time priorities range inclusively from 0 to MAX_RT_PRIO - 1. By default, this range is 0 to 99, since MAX_RT_PRIO is 100.
This priority space is shared with the nice values of SCHED_NORMAL tasks. They use the space from MAX_RT_PRIO to (MAX_RT_PRIO + 40). By default, this means the –20 to +19 nice range maps directly onto the priority space from 100 to 139.

Default priority ranges:

* 0 to 99: real-time priorities.
* 100 to 139: normal priorities.

### Scheduler-Related System Calls

Linux provides a family of system calls for the management of scheduler parameters.
These system calls allow manipulation of process priority, scheduling policy, and processor affinity, as well as provide an explicit mechanism to yield the processor to other tasks.
