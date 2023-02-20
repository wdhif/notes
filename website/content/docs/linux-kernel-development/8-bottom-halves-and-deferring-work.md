+++
title = "8. Bottom Halves and Deferring Work"
description = " "
weight = 8
+++

# Bottom Halves and Deferring Work

Interrupt handlers, can form only the first half of any interrupt processing solution, with the following limitations:

* **Interrupt handlers run asynchronously and interrupt other potentially important code, including other interrupt handlers.** Therefore, to avoid stalling the interrupted code for too long, interrupt handlers need to run as quickly as possible.
* Interrupt handlers are often timing-critical because they deal with hardware.
* **Interrupt handlers do not run in process context.** Therefore, they cannot block. This limits what they can do.

Operating systems need a quick, asynchronous, and simple mechanism for immediately responding to hardware and performing any time-critical actions. Interrupt handlers serve this function well. Less critical work can and should be deferred to a later point when interrupts are enabled.

**Consequently, managing interrupts is divided into two parts, or halves. Interrupt handlers are the top halves.**

## Bottom Halves

**The job of bottom halves is to perform any interrupt-related work not performed by the interrupt handler.** You want the interrupt handler to perform as little work as possible and in turn be as fast as possible. By offloading as much work as possible to the bottom half, **the interrupt handler can return control of the system to whatever it interrupted as quickly as possible.**

The interrupt handler must perform some of the work. For example, the interrupt handler almost assuredly needs to acknowledge to the hardware the receipt of the interrupt.
It may need to copy data to or from the hardware. This work is timing sensitive, so it makes sense to perform it in the interrupt handler.
Almost anything else can be performed in the bottom half. For example, if you copy data from the hardware into memory in the top half, it makes sense to process it in the bottom half.

No hard and fast rules exist about what work to perform where. The decision is left entirely up to the device-driver author. 

The point of a bottom half is not to do work at some specific point in the future, but simply to defer work until any point in the future when the system is less busy and interrupts are again enabled.
**Often, bottom halves run immediately after the interrupt returns.** The key is that they run with all interrupts enabled.

## A World of Bottom Halves

While the top half is implemented entirely via the interrupt handler, multiple mechanisms are available for implementing a bottom half. These mechanisms are different interfaces and subsystems that enable you to implement bottom halves.

### The Original "Bottom Half"

In the beginning, Linux provided only the "bottom half" for implementing bottom halves. This name was logical because at the time that was the only means available for deferring work. The infrastructure was also known as BH to avoid confusion with the generic term bottom half.

The BH interface was simple. It provided a statically created list of 32 bottom halves for the entire system. Each BH was globally synchronized. No two could run at the same time, even on different processors.
**This was simple and easy to use, but was also inflexible and a bottleneck.**

### Task Queues

The kernel developers later introduced `task queues` both as a method of deferring work and as a replacement for the BH mechanism.

The kernel defined a family of queues.
* Each queue contained a linked list of functions to call.
* The queued functions were run at certain times, depending on which queue they were in.
* Drivers could register their bottom halves in the appropriate queue.

**This worked fairly well, but it was still too inflexible to replace the BH interface entirely.** It also was not lightweight enough for performance-critical subsystems, such as networking.

### Softirqs and Tasklets

The `softirqs` and `tasklets` were later introduced to completely replace the BH interface.

* Softirqs are a set of statically defined bottom halves that can run simultaneously on any processor; even two of the same type can run concurrently.
* Tasklets are flexible, dynamically created bottom halves built on top of softirqs.
* * Two different tasklets can run concurrently on different processors, but two of the same type of tasklet cannot run simultaneously.

**Tasklets are a good trade-off between performance and ease of use. For most bottom-half processing, the tasklet is sufficient.**
**Softirqs are useful when performance is critical, such as with networking.** Using softirqs requires more care, however, because two of the same softirq can run at the same time. In addition, softirqs must be registered statically at compile time. Conversely, code can dynamically register tasklets.

All BH users were converted to the other bottom-half interfaces. Additionally, the task queue interface was replaced by the work queue interface. Work queues are a simple yet useful method of queuing work to later be performed in process context.

**Consequently, the 2.6 kernel has three bottom-half mechanisms in the kernel:**
* Softirqs
* Tasklets
* Work queues

**Tasklets are built on softirqs and work queues are their own subsystem.**

### Kernel Timers

Kernel timers is another mechanism for deferring work. Unlike other mechanisms seen previously, timers defer work for a specified amount of time. That is, although the tools discussed before are useful to defer work to any time but now, you use timers to defer work until at least a specific time has elapsed.
**Therefore, timers have also other uses that Bottom Halves.**

## Softirqs

**Softirqs are rarely used directly; tasklets, which are built on softirqs are a much more common form of bottom half.**

### Implementing Softirqs

**Softirqs are statically allocated at compile time. Unlike tasklets, you cannot dynamically register and destroy softirqs.**
A 32-entry array is used to store softirqs, registered softirq consumes one entry in the array. Consequently, there are predefined number of registered softirqs that is statically determined at compile time and cannot be changed dynamically. **The kernel enforces a limit of 32 registered softirqs.** In the current kernel, only nine exist.

**A softirq never preempts another softirq.** The only event that can preempt a softirq is an interrupt handler. Another softirq (even the same one) can run on another processor, however.

### Executing Softirqs

**A registered softirq must be marked before it will execute. Usually, an interrupt handler marks its softirq for execution before returning.** This is called `raising the softirq`. Then, at a suitable time, the softirq runs.

Pending softirqs are checked for and executed in the following places:
* In the return from hardware interrupt code path.
* In the `ksoftirqd` kernel thread.
* In any code that explicitly checks for and executes pending softirqs, such as the networking subsystem.

### Using Softirqs

**Softirqs are reserved for the most timing-critical and important bottom-half processing on the system.**

Currently, only two subsystems directly use softirqs:
* Networking devices
* Block devices

**Additionally, kernel timers and tasklets are built on top of softirqs.**

## Tasklets

**Tasklets are a bottom-half mechanism built on top of softirqs.** As mentioned, they have nothing to do with tasks. Tasklets are similar in nature and behavior to softirqs, but have a simpler interface and relaxed locking rules.

### Implementing Tasklets

Because tasklets are implemented on top of softirqs, they are softirqs. Tasklets are represented by two of the nine softirqs:
* `HI_SOFTIRQ`.
* `TASKLET_SOFTIRQ`.

**Since softirqs are sorted by priority, the `HI_SOFTIRQ`-based tasklets run prior to the `TASKLET_SOFTIRQ`-based tasklets.**

The implementation of tasklets is simple, but rather clever:
* All tasklets are multiplexed on top of two softirqs, `HI_SOFTIRQ` and `TASKLET_SOFTIRQ`.
* When a tasklet is scheduled, the kernel raises one of these softirqs.
* These softirqs, in turn, are handled by special functions that then run any scheduled tasklets.
* The special functions ensure that only one tasklet of a given type runs at the same time. However, other tasklets can run simultaneously.

**Tasklets are dynamically created and, as with softirqs, cannot sleep.** You cannot use semaphores or other blocking functions in a tasklet.
**Tasklets also run with all interrupts enabled**, so you must take precautions (for example, disable interrupts and obtain a lock) if your tasklet shares data with an interrupt handler.
**Unlike softirqs, two of the same tasklets never run concurrently, though two different tasklets can run at the same time on two different processors.** If a tasklet shares data with another tasklet or softirq, proper locking need to be used.

**After a tasklet is scheduled, it runs once at some time in the near future.** If the same tasklet is scheduled again, before it has had a chance to run, it still runs only once. If it is already running, for example on another processor, the tasklet is rescheduled and runs again. As an optimization, a tasklet always runs on the processor that scheduled it, making better use of the processor's cache.

### ksoftirqd

**Softirq processing is aided by a set of per-processor kernel threads.** These kernel threads help in the processing of softirqs when the system is overwhelmed with softirqs. Because tasklets are implemented using softirqs, the following discussion applies equally to softirqs and tasklets.

As described, the kernel processes softirqs in a number of places, most commonly on return from handling an interrupt. There are two characteristics with softirqs:
* Softirqs might be raised at high rates, such as during heavy network traffic.
* Softirq functions can reactivate themselves. That is, while running, a softirq can raise itself so that it runs again. For example, the networking subsystem's softirq raises itself.

The issue is that in an high load environments, in which many softirqs continually reactivate themselves:
* If the Kernel keep handling softirqs, it might not accomplish much else. Resulting in user-space programs being starved of processor time.
* If the Kernel stops handling softirqs, it prevents starving user-space, but it does starve the softirqs and does not take good advantage of an idle system.

**The solution ultimately implemented in the kernel is to not immediately process reactivated softirqs. Instead, if the number of softirqs grows excessive, the kernel wakes up a family of kernel threads to handle the load. The kernel threads run with the lowest possible priority (nice value of 19), which ensures they do not run in lieu of anything important.**

The advantage it brings are:
* The concession prevents heavy softirq activity from completely starving user-space of processor time.
* It also ensures that excessive softirqs do run eventually.
* On an idle system the softirqs are handled rather quickly because the kernel threads will schedule immediately.

**There is one thread per processor.** Having a thread on each processor ensures an idle processor, if available, can always service softirqs.

## Work Queues

Work queues are a different form of deferring work. **Work queues defer work into a kernel thread; this bottom half always runs in process context.**
Code deferred to a work queue has all the usual benefits of process context. Most importantly, work queues are schedulable and can therefore sleep.

Normally, it is easy to decide between using work queues and softirqs/tasklets:
* If the deferred work needs to sleep, work queues are used.
* If the deferred work need not sleep, softirqs or tasklets are used.

If you need a schedulable entity to perform your bottom-half processing, you need work queues. **They are the only bottom-half mechanisms that run in process context, and thus the only ones that can sleep.**
This means they are useful for situations in which you need to allocate a lot of memory, obtain a semaphore, or perform block I/O.
If you do not need a kernel thread to handle your deferred work, consider a tasklet instead.

### Implementing Work Queues

In its most basic form, the work queue subsystem is an interface for creating kernel threads to handle work queued from elsewhere. **These kernel threads are called worker threads.**
Work queues enables your driver to create a special worker thread to handle deferred work. The work queue subsystem, however, implements and provides a default worker thread for handling work. **Therefore, in its most common form, a work queue is a simple interface for deferring work to a generic kernel thread.**

**The default worker threads are called `events/n` where `n` is the processor number; there is one per processor.**

The default worker thread handles deferred work from multiple locations. Many drivers in the kernel defer their bottom-half work to the default thread.
Unless a driver or subsystem has a strong requirement for creating its own thread, the default thread is preferred.

Using a dedicated worker thread might be advantageous if the driver performs large amounts of processing in the worker thread. Processor-intense and performance-critical work might benefit from its own thread.
This also lightens the load on the default threads, which prevents starving the rest of the queued work.

Tasks for work threads are strung into a linked list, one for each type of queue on each processor. For example, there is one list of deferred work for the generic thread, per processor.
* When a worker thread wakes up (the thread's state is set to `TASK_RUNNING`), it runs any work in its list.
* **A worker thread executes the work in process context. By default, interrupts are enabled and no locks are held. If needed, it can sleep.**
* As it completes work, it removes the corresponding task entries from the linked list.
* When the list is empty, it goes back to sleep (the thread's state is set to `TASK_INTERRUPTIBLE`).

Despite running in process context, **the work handlers cannot access user-space memory because there is no associated user-space memory map for kernel threads.** The kernel can access user memory only when running on behalf of a user-space process, such as when executing a system call. Only then is user memory mapped in.

## Which Bottom Half Should I Use?

### Softirqs: least serialization, for highly threaded code

Softirqs, by design, provide the least serialization. This requires softirq handlers to go through extra steps to ensure that shared data is safe because two or more softirqs of the same type may run concurrently on different processors.
If the code in question is already highly threaded, such as in a networking subsystem that is chest-deep in per-processor variables, softirqs make a good choice.
**They are certainly the fastest alternative for timing-critical and high-frequency uses.**

### Tasklets: simple interface, for less threaded code

Tasklets make more sense if the code is not finely threaded. They have a simpler interface and, because two tasklets of the same type might not run concurrently, they are easier to implement. **Tasklets are effectively softirqs that do not run concurrently.**
A driver developer should always choose tasklets over softirqs, unless prepared to utilize per-processor variables or similar magic to ensure that the softirq can safely run concurrently on multiple processors.

### Work queues: process context

**If the deferred work needs to run in process context, the only choice of the three is work queues.** If process context is not a requirements (specifically, if you have no need to sleep), softirqs or tasklets are perhaps better suited. Work queues involve the highest overhead because they involve kernel threads and, therefore, context switching. This doesn't mean they are inefficient, but in light of thousands of interrupts hitting per second (as the networking subsystem might experience), other methods make more sense. However, work queues are sufficient for most situations.

### Softirqs vs. tasklets vs. work queues

In terms of ease of use, work queues wins. Using the default events queue is easy. Next come tasklets, which also have a simple interface. Coming in last are softirqs, which need to be statically created and require careful thinking with their implementation.

If the driver need a schedulable entity to perform the deferred work, and if fundamentally, it need to sleep for any reason, then work queues are your only option. Otherwise, tasklets are preferred.
Only if scalability becomes a concern the driver could use softirqs.

The following table is a comparison between the three bottom-half interfaces.
| Bottom Half | Context   | Inherent Serialization              |
|-------------|-----------|-------------------------------------|
| Softirq     | Interrupt | None                                |
| Tasklets    | Interrupt | Against the same tasklet            |
| Work Queues | Process   | None (scheduled as process context) |

## Locking Between the Bottom Halves

It is crucial to protect shared data from concurrent access while using bottom halves, even on a single processor machine. **A bottom half can run at virtually any moment.**

One benefit of tasklets is that they are serialized with respect to themselves. **The same tasklet will not run concurrently, even on two different processors.** This means you do not have to worry about intra-tasklet concurrency issues. Inter-tasklet concurrency (when two different tasklets share the same data) requires proper locking.

On the other hand, because **softirqs provide no serialization, (even two instances of the same softirq might run simultaneously), all shared data needs an appropriate lock.**

If process context code and a bottom half share data, you need to do both of the following before accessing the data:
* Disable bottom-half processing.
* Obtain a lock.

If interrupt context code and a bottom half share data, you need to do both of the following before accessing the data:
* Disable interrupts.
* Obtain a lock.

In both cases, this ensures local and SMP protection and prevents a deadlock.

Because work queues run in process context, there are no issues with asynchronous execution, and thus, there is no need to disable them. On the other hand, protecting shared data is the same as in any process context and requires locking.
However, because softirqs and tasklets can occur asynchronously (for example, on return from handling an interrupt), kernel code may need to disable them. 

**The locking is no different from normal kernel code because work queues run in process context.**
