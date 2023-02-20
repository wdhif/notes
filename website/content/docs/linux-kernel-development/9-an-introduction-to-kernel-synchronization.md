+++
title = "9. An Introduction to Kernel Synchronization"
description = " "
+++

# An Introduction to Kernel Synchronization

In a shared memory application, developers must ensure that shared resources are protected from concurrent access. The kernel is no exception.
**Symmetrical multiprocessing is supported in Linux. Multiprocessing support implies that kernel code can simultaneously run on two or more processors.**

Shared resources require protection from concurrent access because if multiple threads of execution access and manipulate the data at the same time, the threads may overwrite each other's changes or access data while it is in an inconsistent state.
Consequently, without protection, code in the kernel, running on two different processors, can simultaneously access shared data at exactly the same time.

The term threads of execution implies any instance of executing code. For example, this includes any of the following:
* A task in the kernel
* An interrupt handler
* A bottom half
* A kernel thread

Concurrent access of shared data often results in instability is hard to track down and debug.

The Linux kernel is preemptive. This implies that (in the absence of protection) the scheduler can preempt kernel code at virtually any point and reschedule another task.
A number of scenarios enable for concurrency inside the kernel, and they all require protection.

## Critical Regions and Race Conditions

**Code paths that access and manipulate shared data are called `critical regions` (also called `critical sections`).** It is usually unsafe for multiple threads of execution to access the same resource simultaneously.
To prevent concurrent access during critical regions, the programmer must ensure that code executes **atomically**, which means that operations complete without interruption as if the entire critical region were one indivisible instruction.

**If two threads of execution simultaneously execute within the same critical region, it is called a `race condition`, so-named because the threads raced to get there first.** Debugging race conditions is often difficult because they are not easily reproducible.
**Ensuring that unsafe concurrency is prevented and that race conditions do not occur is called `synchronization`.**

### Why Do We Need Protection?

To best understand the need for synchronization, look at the ubiquity of race conditions.
The first example is a real-world case: an ATM (Automated Teller Machine, called a cash machine).

The ATM works as follows:
* Check whether the deduction is possible.
* Compute the new total funds.
* Finally execute the physical deduction.

Assuming a user, with a $100 in the bank, and user's spouse are initiating withdrawal of $75.
* Both the user and user's spouse initiate withdrawal at the same time.
* Both transactions verify that sufficient funds exist, in both cases, the user has $100 in the bank for the withdrawal of $75.
* In both transactions, the new computed total fund would be $25.
* In both cases, the users would be getting $75, for a total of $150, while still having in the bank $25.
* This means that the user funds would increase from $100 to $175.

Clearly, financial institutions must ensure that this can never happen. They must lock the account during certain operations, making each transaction atomic with respect to any other transaction.
Such transactions must occur in their entirety, without interruption, or not occur at all.

### The Single Variable

Consider a simple shared resource, a single global integer, and a simple critical region, the operation of merely incrementing it: `i++`.

This might translate into machine instructions to the computer's processor that resemble the following:
* Get the current value of `i` and copy it into a register.
* Add one to the value stored in the register.
* Write back to memory the new value of `i`.

Assume that there are two threads of execution, both enter this critical region, and the initial value of `i` is 7. The desired outcome is then similar to the following (with each row representing a unit of time):

| Thread 1               | Thread 2               |
|------------------------|------------------------|
| get `i` (7)            | —                      |
| increment `i` (7 -> 8) | —                      |
| write back `i` (8)     | —                      |
| —                      | get `i` (8)            |
| —                      | increment `i` (8 -> 9) |
| —                      | write back `i` (9)     |

As expected, 7 incremented twice is 9.

However, another possible outcome is the following:

| Thread 1               | Thread 2               |
|------------------------|------------------------|
| get `i` (7)            | get `i` (7)            |
| increment `i` (7 -> 8) | —                      |
| —                      | increment `i` (7 -> 8) |
| write back `i` (8)     | —                      |
| —                      | write back `i` (9)     |

If both threads of execution read the initial value of `i` before it is incremented, both threads increment and save the same value. As a result, the variable `i` contains the value 8 when, in fact, it should now contain 9.
This is one of the simplest examples of a critical region. The solution is simple. We merely need a way to perform these operations in one indivisible step.
Most processors provide an instruction to atomically read, increment, and write back a single variable.

Using this atomic instruction, the only possible outcome is:

| Thread 1                       | Thread 2                       |
|--------------------------------|--------------------------------|
| increment & store `i` (7 -> 8) | —                              |
| —                              | increment & store `i` (8 -> 9) |

Thread 2 could also be incrementing `i` first, but the result would be the same.

**It would never be possible for the two atomic operations to interleave. The processor would physically ensure that it was impossible.** Using such an instruction would alleviate the problem. The kernel provides a set of interfaces that implement these atomic instructions, which are discussed in the next chapter.

## Locking

Assuming a queue of requests that needs to be serviced and the implementation is a linked list, in which each node represents a request. Two functions manipulate the queue:

* One function adds a new request to the tail of the queue.
* One function removes a request from the head of the queue and service request.

Requests are continually being added, removed, and serviced, since various parts of the kernel invoke these two functions.
Manipulating the request queues certainly requires multiple instructions. If one thread attempts to read from the queue while another is in the middle of manipulating it, the reading thread will find the queue in an inconsistent state.
It should be apparent the sort of damage that could occur if access to the queue could occur concurrently. **Often, when the shared resource is a complex data structure, the result of a race condition is corruption of the data structure.**

Although it is feasible for a particular architecture to implement simple instructions, such as arithmetic and comparison, atomically it is ludicrous for architectures to provide instructions to support the indefinitely sized critical regions that would exist in the example.

What is needed is a way of making sure that only one thread manipulates the data structure at a time, a mechanism for preventing access to a resource while another thread of execution is in the marked region.
**A lock provides such a mechanism. Threads hold locks; locks protect data.**

* Whenever there was a new request to add to the queue, the thread would first obtain the lock. Then it could safely add the request to the queue and ultimately release the lock.
* When a thread wanted to remove a request from the queue, it would also obtain the lock. Then it could read the request and remove it from the queue. Finally, it would release the lock.

Any other access to the queue would similarly need to obtain the lock. Because the lock can be held by only one thread at a time, only a single thread can manipulate the queue at a time.
If a thread comes along while another thread is already updating it, the second thread has to wait for the first to release the lock before it can continue. **The lock prevents concurrency and protects the queue from race conditions.**

| Thread 1                 | Thread 2                 |
|--------------------------|--------------------------|
| try to lock the queue    | try to lock the queue    |
| succeeded: acquired lock | failed: waiting...       |
| access queue...          | waiting...               |
| unlock the queue         | waiting...               |
| —                        | succeeded: acquired lock |
| —                        | access queue...          |
| —                        | unlock the queue         |

**Notice that locks are advisory and voluntary.** Locks are entirely a programming construct that the programmer must take advantage of.
Nothing prevents you from writing code that manipulates the fictional queue without the appropriate lock, but such a practice would eventually result in a race condition and corruption.

**Locks come in various shapes and sizes. Linux alone implements a handful of different locking mechanisms.** The most significant difference between the various mechanisms is the behavior when the lock is unavailable because another thread already holds it:
* Some lock variants busy wait (spin in a tight loop, checking the status of the lock over and over, waiting for the lock to become available).
* Other locks put the current task to sleep until the lock becomes available.

**The itself lock does not solve the problem; it simply shrinks the critical region down to just the lock and unlock code: probably much smaller, but still a potential race. What if a lock is aquired by two threads at the exact same time?** 

**Fortunately, locks are implemented using atomic operations that ensure no race exists.** A single instruction can verify whether the key is taken and, if not, seize it.
How this is done is architecture-specific, but almost all processors implement an atomic test and set instruction that tests the value of an integer and sets it to a new value only if it is zero. A value of zero means unlocked.

### Causes of Concurrency

In user-space, programs are scheduled preemptively at the will of the scheduler. Because a process can be preempted at any time and another process can be scheduled onto the processor, a process can be involuntarily preempted in the middle of accessing a critical region.
If the newly scheduled process then enters the same critical region (for example, if the two processes manipulate the same shared memory or write to the same file descriptor), a race can occur.
The same problem can occur with multiple single-threaded processes sharing files, or within a single program with signals, because signals can occur asynchronously.
**This type of concurrency in which two things do not actually happen at the same time but interleave with each other is called pseudo-concurrency.**

With a symmetrical multiprocessing machine (multiple processors or cores), two processes can actually be executed in a critical region at the exact same time. **That is called true concurrency**. Although the causes and semantics of true versus pseudo concurrency are different, they both result in the same race conditions and require the same sort of protection.

The kernel has similar causes of concurrency:
* **Interrupts:** An interrupt can occur asynchronously at almost any time, interrupting the currently executing code.
* **Softirqs and tasklets:** The kernel can raise or schedule a softirq or tasklet at almost any time, interrupting the currently executing code.
* **Kernel preemption:** Because the kernel is preemptive, one task in the kernel can preempt another.
* **Sleeping and synchronization with user-space:** A task in the kernel can sleep and thus invoke the scheduler, resulting in the running of a new process.
* **Symmetrical multiprocessing:** Two or more processors can execute kernel code at exactly the same time.

**This is the reason locking and synchronization mechanisms are needed.**

## Deadlocks

**A deadlock is a condition involving one or more threads of execution and one or more resources, such that each thread waits for one of the resources, but all the resources are already held.**

**The threads all wait for each other, but they never make any progress toward releasing the resources that they already hold. Therefore, none of the threads can continue, which results in a deadlock.**

A good analogy is a four-way traffic stop. If each car at the stop decides to wait for the other cars before going, no car will ever proceed, and we have a traffic deadlock.

**The most common example is with two threads and two locks, which is often called the deadly embrace or the ABBA deadlock:**
| Thread 1              | Thread 2              |
|-----------------------|-----------------------|
| acquire lock A        | acquire lock B        |
| try to acquire lock B | try to acquire lock A |
| wait for lock B       | wait for lock A       |

Each thread is waiting for the other, and neither thread will ever release its original lock; therefore, neither lock will become available.

Prevention of deadlock scenarios is important. Although it is difficult to prove that code is free of deadlocks, the following rules can help in writing a deadlock-free code:

* **Implement lock ordering.** Nested locks must always be obtained in the same order. This prevents the deadly embrace deadlock.
* Prevent starvation.
* * Does this code always finish?
* * If foo does not occur, will bar wait forever?
* Do not double acquire the same lock.
* Design for simplicity. Complexity locking schemes invites deadlocks.

The first point is most important and worth stressing. **If two or more locks are acquired at the same time, they must always be acquired in the same order.**
The order of unlock does not matter with respect to deadlock, although it is common practice to release the locks in an order inverse to that in which they were acquired.

Preventing deadlocks is important. The Linux kernel has some basic debugging facilities for detecting deadlock scenarios in a running kernel, which are discussed in the next chapter.

## Contention and Scalability

**The term lock contention, or simply contention, describes a lock currently in use but that another thread is trying to acquire.**
A lock that is highly contended often has threads waiting to acquire it. High contention can occur because a lock is frequently obtained, held for a long time after it is obtained, or both.
Because a lock's job is to serialize access to a resource, they can slow down a system's performance. A highly contended lock can become a bottleneck in the system, quickly limiting its performance.
However, a solution to high contention must continue to provide the necessary concurrency protection, because locks are also required to prevent the system from tearing itself to shreds.

**Scalability is a measurement of how well a system can be expanded.** In operating systems, we talk of the scalability with a large number of processes, a large number of processors, or large amounts of memory.
We can discuss scalability in relation to virtually any component of a computer to which we can attach a quantity. Ideally, doubling the number of processors should result in a doubling of the system's processor performance, which, of course, is never the case.

**The granularity of locking is a description of the size or amount of data that a lock protects:**
* A very coarse lock protects a large amount of data, e.g. an entire subsystem’s set of data structures.
* On the other hand, a very fine-grained lock protects a small amount of data, e.g. only a single element in a larger structure.

Scalability improvement is generally a good thing because it improves Linux's performance on larger and more powerful systems.
However, rampant scalability "improvements" can lead to a decrease in performance on smaller SMP and UP machines, because smaller machines may not need such fine-grained locking but will nonetheless need to put up with the increased complexity and overhead.
