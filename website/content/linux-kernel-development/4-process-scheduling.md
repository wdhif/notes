+++
title = "4. Process Scheduling"
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

The current Linux scheduler is the **Completely Fair Scheduler**, or **CFS**. The **CFS** was introduced as a replacement for the **O(1)**, which was performant, but was lacking when dealing with interactive process, like on a desktop for example.

### Policy

The policy of a scheduler determines what runs when. Therefor it is very important.

### I/O-Bound Versus Processor-Bound Processes

Processes can be classified as two types:
* **I/O-bound**: A process that spend much of its time **waiting on I/O requests** (I/O here means any **blockable resources**, like keyboard inputs or network I/O, not only disk I/O). Such process are runnable for only short duration before having to wait on requests, like GUI waiting on user inputs.
* **processor-bound**: **Processor-bound processes spend much of their time executing code.** They tend to run until they are **preempted** because they do not block on I/O requests very often.

### Process Priority

A common type of scheduling algorithm is priority-based scheduling. The goal is to **rank** processes based on their worth and need for processor time.
**Processes with a higher priority run before those with a lower priority**, whereas **processes with the same priority are scheduled in round-robin** (one after the next, repeating).

**The runnable process with timeslice remaining and the highest priority always runs.** Both the user and the system can set a process’s priority to influence the scheduling behavior of the system.

The Linux kernel implement two priority ranges:
* **Niceness**: A number from **-20 to +19 with a default at 0**. Larger nice values correspond to a lower priority, you are being “nice” to the other processes on the system. **Processes with a lower nice value (higher priority) receive a larger proportion of the system’s processor compared to processes with a higher nice value (lower priority).**
* **Real-time priority**: The values are configurable, but by default range from **0 to 99**, inclusive. **Higher real-time priority values correspond to a greater priority and all real-time processes are at a higher priority than normal processes.** By default, processes are not real-time, their value is "-", or null.**
* **Real-time priority**: The values are configurable, but by default range from **0 to 99**, inclusive. **Higher real-time priority values correspond to a greater priority and all real-time processes are at a higher priority than normal processes.** **By default, processes are not real-time**, their value is "-", or null.

### Timeslice

**The timeslice is the numeric value that represents how long a task can run until it is preempted.** The scheduler policy must dictate a default timeslice, which is not a trivial exercise.
* Too long a timeslice causes the system to have poor interactive performance, the system will no longer feel as if applications are concurrently executed.
* Too short a timeslice causes significant amounts of processor time to be wasted on the overhead of switching processes.

Furthermore, the conflicting goals of I/O-bound versus processor-bound processes again arise:
* I/O-bound processes do not need longer timeslices (although they do like to run often)
* Processor-bound processes crave long timeslices (to keep their caches hot).

**To avoid thoses issues, Linux’s CFS scheduler does not directly assign timeslices to processes.** **Instead, it will assigns processes a proportion of the processor**, therefore, the amount of processor time that a process receives is a function of the load of the system.
**This assigned proportion is further affected by each process’s nice value.** The nice value acts as a weight, changing the proportion of the processor time each process receives.

**When a process enters the runnable state, it becomes eligible to run.** Whether the process runs immediately, preempting the currently running process, is a function of how much of a proportion of the processor the newly runnable processor has consumed.
* If **it has consumed a smaller proportion of the processor than the currently executing process, it runs immediately**, preempting the current process. 
* If not, it is scheduled to run at a later time.

### The Scheduling Policy in Action

Consider two runnable processes:
* **A text editor: I/O-bound.** It will spend nearly all its time waiting for user key presses.
* **A video encoder: Processor-bound.** Aside from waiting on disk to read the video at first, it will then spends all its time encoding the video, consuming 100% of the processor.

The **text editor**, despite spending most of its time waiting on user input, **when the text editor does receive a key press, the user expects the editor to respond immediately**. **Latency is a primary concern.**
The **video encoder doesn't have strong time constraint**, we don't really care if it run now or at the next CPU cycle. The sooner it finishes the better, but **latency is not a primary concern**.

If both processes are runnable and have the same nicelevel, they would be awarded both with the same proportion of the processor's time. But since the **text editor** spend a lot of time waiting, it would almost always have more processor time left than the **video encoder**. And because of that, **CFS would let the text editor run in priority, therefor limiting latency**.

This will allow the **text editor** to run everytime it's ready, and the **video encoder** to run the rest of the time, assuming no other process need to run.

### The Linux Scheduling Algorithm
