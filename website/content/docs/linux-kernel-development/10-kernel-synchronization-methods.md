+++
title = "10. Kernel Synchronization Methods"
description = " "
weight = 10
+++

# Kernel Synchronization Methods

The previous chapter discussed the sources of and solutions to race conditions. The Linux kernel provides a family of synchronization methods, which enable developers to write efficient and race-free code. This chapter discusses these methods and their interfaces, behavior, and use.

## Atomic Operations

As the foundation on which other synchronization methods are built, atomic operations provide instructions that execute atomically, without interruption. **Atomic operators are indivisible instructions.**
For example, an atomic increment can read and increment a variable by one in a single indivisible and uninterruptible step.

**The kernel provides two sets of interfaces for atomic operations: one that operates on integers and another that operates on individual bits.**
These interfaces are implemented on every architecture that Linux supports. Most architectures contain instructions that provide atomic versions of simple arithmetic operations.
Other architectures, lacking direct atomic operations, provide an operation to lock the memory bus for a single operation, thus guaranteeing that another memory-affecting operation cannot occur simultaneously.

### Atomicity Versus Ordering

**Atomicity and Ordering are not the same.** As discussed, an atomic read (supported by most architectures) always occurs atomically. It never interleaves with a write to the same word.
The read always returns the word in a consistent state: perhaps before the write completes, perhaps after, but never during. For example, if an integer is initially 42 and then set to 365, a read on the integer always returns 42 or 365 and never some commingling of the two values. **We call this atomicity.**

However, your code might have more stringent requirements than this. Perhaps you require that the read always occurs before the pending write. **This type of requirement is not atomicity, but ordering.**

* Atomicity ensures that instructions occur without interruption and that they complete either in their entirety or not at all.
* Ordering, on the other hand, ensures that the desired, relative ordering of two or more instructions (even if they are to occur in separate threads of execution or even separate processors) is preserved.

**The atomic operations discussed in this section guarantee only atomicity. Ordering is enforced via barrier operations, which is discussed later in this chapter.**

**It is usually preferred to choose atomic operations over more complicated locking mechanisms. On most architectures, one or two atomic operations incur less overhead and less cache-line thrashing than a more complicated synchronization method.**

### Atomic Integer Operations

The atomic integer methods operate on a special data type, `atomic_t` for 32-bit architectures and `atomic64_t` for 64-bit architectures. Usage is exactly the same, except that the usable range of the integer is 32 bits for one and 64 bits for the other.
This special type is used, as opposed to having the functions work directly on the C `int` type, for several reasons:
* Having the atomic functions accept only the `atomic_t` type ensures that the atomic operations are used only with these special types. Likewise, it also ensures that the data types are not passed to any non-atomic functions.
* The use of `atomic_t` ensures the compiler does not (erroneously but cleverly) optimize access to the value—it is important the atomic operations receive the correct memory address and not an alias.
* Use of `atomic_t` can hide any architecture-specific differences in its implementation.

The `atomic_t` data type has several mechanisms to help developers:
* `atomic_read()` to convert from `atomic_t` to `int`.
* `atomic_inc()` and `atomic_dec()` to implement simple counters without having to use locking scheme.

### Atomic Bitwise Operations

**In addition to atomic integer operations, the kernel also provides a family of functions that operate at the bit level, which are architecture-specific.**

**The bitwise functions operates on generic memory addresses. The arguments are a pointer and a bit number.**
Bit zero is the least significant bit of the given address. On 32-bit machines, bit 31 is the most significant bit, and bit 32 is the least significant bit of the following word. There are no limitations on the bit number supplied; although, most uses of the functions provide a word and, consequently, a bit number between 0 and 31 on 32-bit machines and 0 and 63 on 64-bit machines.

Because the functions operate on a generic pointer, there is no equivalent of the atomic integer's `atomic_t` type. Instead, the functions work with a pointer to whatever data in memory.

Conveniently, nonatomic versions of all the bitwise functions are also provided. They behave identically to their atomic siblings, except they do not guarantee atomicity. These variants of the bitwise functions might be faster.

If issuing two atomic bit operations, setting and then unsetting a bit, atomicity requires that either instructions succeed in their entirety, uninterrupted, or instructions fail to execute at all.
Moreover, however, at some point in time prior to the final operation, the bit needs to hold the value as specified by the first operation. Real atomicity requires that all intermediate states be correctly realized.

Without atomic operations, the bit might end up cleared, but it might never have been set. The set operation could occur simultaneously with the clear operation and fail. The clear operation would succeed, and the bit would emerge cleared as intended.
With atomic operations, however, the set would actually occur: there would be a moment in time when a read would show the bit as set, and then the clear would execute and the bit would be zero.

**This behavior can be important, especially when ordering comes into play or when dealing with hardware registers.**

## Spin Locks

Critical regions can span multiple functions. For example, it is often the case that data must be removed from one structure, formatted and parsed, and added to another structure. This entire operation must occur atomically; it must not be possible for other code to read from or write to either structure before the update is completed.

**Because simple atomic operations are clearly incapable of providing the needed protection in such a complex scenario, a more general method of synchronization is needed: `locks`.**

**The most common lock in the Linux kernel is the `spin lock`. A spin lock is a lock that can be held by at most one thread of execution.**
If a thread of execution attempts to acquire a spin lock while it is already held, which is called `contended`, the thread busy loops (spins) waiting for the lock to become available.
If the lock is not `contended`, the thread can immediately acquire the lock and continue. The spinning prevents more than one thread of execution from entering the critical region at any one time. The same lock can be used in multiple locations, so all access to a given data structure, for example, can be protected and synchronized.

| Thread 1                 | Thread 2                 |
|--------------------------|--------------------------|
| try to acquire spin lock | —                        |
| succeeded: acquired lock | —                        |
| working...               | try to acquire spin lock |
| working...               | waiting for lock...      |
| working...               | waiting for lock...      |
| release spin lock        | succeeded: acquired lock |
| —                        | working...               |
| —                        | release spin lock        |

Since a spin lock causes threads to spin (essentially wasting processor time) while waiting for the lock to become available, it is not wise to hold a spin lock for a long time.
This is the nature of the spin lock: a lightweight single-holder lock that should be held for short durations.

An alternative behavior when the lock is contended is to put the current thread to sleep and wake it up when it becomes available. This incurs a bit of overhead, most notably the two context switches required to switch out of and back into the blocking thread.

**`Semaphores` do provide a lock that makes the waiting thread sleep, rather than spin, when contended.**

{{< hint warning >}}
If a thread attempt to acquire a spin lock it already hold, it will spin, waiting for itself to release the spin lock, effectively causing a deadlock.
{{< /hint >}}

Spin locks can be used in interrupt handlers, whereas semaphores cannot be used because they sleep.
If a lock is used in an interrupt handler, local interrupts (interrupt requests on the current processor) must also be disabled before obtaining the lock.
Otherwise, it is possible for an interrupt handler to interrupt kernel code while the lock is held and attempt to reacquire the lock. The interrupt handler spins, waiting for the lock to become available.
The lock holder, however, does not run until the interrupt handler completes.

### Spin Locks and Bottom Halves

**Certain locking precautions must be taken when working with bottom halves.**

* Because a bottom half might preempt process context code, if data is shared between a bottom-half process context, data in process context must be protected with both a lock and the disabling of bottom halves.
* Because an interrupt handler might preempt a bottom half, if data is shared between an interrupt handler and a bottom half, it must be protected with both a lock and the disabling of interrupts.

## Reader-Writer Spin Locks

**Sometimes, lock usage can be clearly divided into reader and writer paths.**

For example, considering a list that is both updated and searched.
* When the list is updated (written to), it is important that no other threads of execution concurrently write to or read from the list. Writing demands mutual exclusion.
* When the list is searched (read from), it is only important that nothing else writes to the list. Multiple concurrent readers are safe so long as there are no writers.

The task list’s access patterns (discussed in Chapter 3,“Process Management”) fit this description. Not surprisingly, a `reader-writer spin lock` protects the task list.

When a data structure is neatly split into reader/writer or consumer/producer usage patterns, it makes sense to use a locking mechanism that provides similar semantics.
**To satisfy this use, the Linux kernel provides reader-writer spin locks. Reader-writer spin locks provide separate reader and writer variants of the lock.**
* One or more readers can concurrently hold the reader lock.
* The writer lock, conversely, can be held by at most one writer with no concurrent readers.

Reader/writer locks are sometimes called `shared/exclusive` or `concurrent/exclusive` locks because the lock is available in a shared (for readers) and an exclusive (for writers) form. Usage is similar to spin locks.

**An important consideration in using the Linux reader-writer spin locks is that they favor readers over writers.**
If the read lock is held and a writer is waiting for exclusive access, readers that attempt to acquire the lock continue to succeed. **The spinning writer does not acquire the lock until all readers release the lock.**
Therefore, a sufficient number of readers can starve pending writers. Sometimes this behavior is beneficial, sometimes it is catastrophic.

**Spin locks provide a quick and simple lock.** The spinning behavior is optimal for short hold times and code that cannot sleep (interrupt handlers, for example).
**In cases where the sleep time might be long or you potentially need to sleep while holding the lock, the semaphore is a solution.**

## Semaphores

**Semaphores in Linux are sleeping locks. When a task attempts to acquire a semaphore that is unavailable, the semaphore places the task onto a wait queue and puts the task to sleep.**
The processor is then free to execute other code. When the semaphore becomes available, one of the tasks on the wait queue is awakened so that it can then acquire the semaphore.

* Because the contending tasks sleep while waiting for the lock to become available, semaphores are well suited to locks that are held for a long time.
* Conversely, semaphores are not optimal for locks that are held for short periods because the overhead of sleeping, maintaining the wait queue, and waking back up can easily outweigh the total lock hold time.
* Because a thread of execution sleeps on lock contention, semaphores must be obtained only in process context because interrupt context is not schedulable.
* A thread can sleep while holding a semaphore because it will not deadlock when another process acquires the same semaphore. It will just go to sleep and eventually let the first thread continue.
* A thread cannot hold a spin lock while it acquire a semaphore, because it might have to sleep while waiting for the semaphore, and it cannot sleep while holding a spin lock.

These facts highlight the uses of semaphores versus spin locks. In most uses of semaphores, there is little choice as to what lock to use.

**If the code needs to sleep, which is often the case when synchronizing with user-space, semaphores are the sole solution.** It is often easier, if not necessary, to use semaphores because they allow the flexibility of sleeping.

**When the code does not need to sleep, the decision between semaphore and spin lock should be based on lock hold time.** Ideally, all your locks should be held as briefly as possible.
With semaphores, however, longer lock hold times are more acceptable. Additionally, unlike spin locks, semaphores do not disable kernel preemption and, consequently, code holding a semaphore can be preempted.
**This means semaphores do not adversely affect scheduling latency.**

### Counting and Binary Semaphores

**A final useful feature of semaphores is that they can allow for an arbitrary number of simultaneous lock holders.**
Whereas spin locks permit at most one task to hold the lock at a time, the number of permissible simultaneous holders of semaphores can be set at declaration time.
This value is called the `usage count` or simply the `count`.

The most common value is to allow, like spin locks, only one lock holder at a time.
* **In this case, the count is equal to one, and the semaphore is called either a `binary semaphore` (because it is either held by one task or not held at all) or a `mutex` (because it enforces mutual exclusion).**

Alternatively, the count can be initialized to a nonzero value greater than one.
* **In this case, the semaphore is called a counting semaphore, and it enables at most count holders of the lock at a time.**

Counting semaphores are not used to enforce mutual exclusion because they enable multiple threads of execution in the critical region at once. Instead, they are used to enforce limits in certain code.
They are not used much in the kernel. When using a semaphore, it is almost assuredly wanted to use a `mutex` (a semaphore with a count of one).

Semaphores were formalized by Edsger Wybe Dijkstra in 1968 as a generalized locking mechanism.
**A semaphore supports two `atomic` operations**, `P()` and `V()`, named after the Dutch word `Proberen`, to test (literally, to probe), and the Dutch word `Verhogen`, to increment.

Later systems called these methods `down()` and `up()`, respectively, and so does Linux.
* The `down()` method is used to acquire a semaphore by decrementing the count by one. You `down` a semaphore to acquire it.
* * If the new count is zero or greater, the lock is acquired and the task can enter the critical region. 
* * If the count is negative, the task is placed on a wait queue, and the processor moves on to something else.
* The `up()` method is used to release a semaphore upon completion of a critical region, the method increments the count value. You `up` a semaphore to release it.
* * If the semaphore’s wait queue is not empty, one of the waiting tasks is awakened and allowed to acquire the semaphore.

### Using Semaphores

* The function `down_interruptible()`, which if the semaphore is unavailable, places the calling process to sleep in the `TASK_INTERRUPTIBLE` state. If the task receives a signal while waiting for the semaphore, it is awakened and `down_interruptible()` returns `-EINTR`.
* The function `down()`, which if the semaphore is unavailable, places the calling process to sleep in the `TASK_UNINTERRUPTIBLE` state. The process will not respond to signals, which can be an issue.

**When in `TASK_INTERRUPTIBLE`, if the task receives a signal while waiting for the semaphore, it is awakened and `down_interruptible()` returns `-EINTR`.**

**It is also possible to use `down_trylock()` to try to acquire the given semaphore without blocking.**
If the semaphore is already held, the function immediately returns nonzero. Otherwise, it returns zero and the process successfully hold the lock.

**Finally, to release a given semaphore, the process must call `up()`.**

## Reader-Writer Semaphores

Semaphores, like spin locks, also come in a reader-writer flavor. The situations where reader-writer semaphores are preferred over standard semaphores are the same as with reader-writer spin locks versus standard spin locks.

**All reader-writer semaphores are mutexes, their usage count is one, although they enforce mutual exclusion only for writers, not readers.**
Any number of readers can concurrently hold the read lock, so long as there are no writers.
Conversely, only a sole writer (with no readers) can acquire the write variant of the lock. All reader-writer locks use uninterruptible sleep.

As with normal semaphores, it is also possible to try to acquire the given semaphore without blocking, either as a reader or as a writer. In both cases, the semaphore `down()` function return nonzero if the lock is successfully acquired and zero if it is currently contended. For admittedly no good reason, this is the opposite of normal semaphore behavior!

## Mutexes

Until recently, the only sleeping lock in the kernel was the semaphore. Most users of semaphores instantiated a semaphore with a count of one and treated them as a mutual exclusion lock, a sleeping version of the spin lock.
Unfortunately, semaphores are rather generic and do not impose many usage constraints.
* This makes them useful for managing exclusive access in complicated situations.
* But it also means that simpler locking is harder to do, and the lack of enforced rules makes any sort of automated debugging or constraint enforcement impossible.

**Seeking a simpler sleeping lock, the kernel developers introduced the `mutex`.**

{{< hint info >}}
The term “mutex” is a generic name to refer to any sleeping lock that enforces mutual exclusion, such as a semaphore with a usage count of one. In recent Linux kernels, the proper noun “mutex” is now also a specific type of sleeping lock that implements mutual exclusion.That is, a mutex is a mutex.
{{< /hint >}}

**The mutex behaves similar to a semaphore with a count of one, but it has a simpler interface, more efficient performance, and additional constraints on its use.**

The simplicity and efficiency of the mutex comes from the additional constraints it imposes on its users over and above what the semaphore requires.

Unlike a semaphore, which implements the most basic of behavior in accordance with Dijkstra’s original design, the mutex has a stricter, narrower use case:
* **Only one task can hold the mutex at a time.** That is, the usage count on a mutex is always one.
* **Whoever locked a mutex must unlock it.** That is, you cannot lock a mutex in one context and then unlock it in another. This means that the mutex isn’t suitable for more complicated synchronizations between kernel and user-space. Most use cases, however, cleanly lock and unlock from the same context.
* **Recursive locks and unlocks are not allowed.** That is, you cannot recursively acquire the same mutex, and you cannot unlock an unlocked mutex.
* **A process cannot exit while holding a mutex.**
* **A mutex cannot be acquired by an interrupt handler or bottom half.**
* **A mutex can be managed only via the official API**: It must be initialized via the methods described in this section and cannot be copied, hand initialized, or reinitialized.

Perhaps the most useful aspect of the mutex is that, via a special debugging mode, the kernel can programmatically check for and warn about violations of these constraints.

## Semaphores Versus Mutexes

Mutexes and semaphores are similar. Having both in the kernel is confusing.
Thankfully, the formula dictating which to use is quite simple: Unless one of mutex’s additional constraints prevent you from using them, prefer the new mutex type to semaphores. When writing new code, only specific, often low-level, uses need a semaphore.
Start with a mutex and move to a semaphore only if you run into one of their constraints and have no other alternative.

## Spin Locks Versus Mutexes

Knowing when to use a spin lock versus a mutex (or semaphore) is important to writing optimal code.
In many cases, however, there is little choice. **Only a spin lock can be used in interrupt context, whereas only a mutex can be held while a task sleeps.**

What to Use: Spin Locks Versus Semaphores:
| Requirement                         | Recommended Lock        |
|-------------------------------------|-------------------------|
| Low overhead locking                | Spin lock is preferred. |
| Short lock hold time                | Spin lock is preferred. |
| Long lock hold time                 | Mutex is preferred.     |
| Need to lock from interrupt context | Spin lock is preferred. |
| Need to sleep while holding lock    | Mutex is preferred.     |

## Completion Variables

Using completion variables is an easy way to synchronize between two tasks in the kernel when one task needs to signal to the other that an event has occurred.
* One task waits on the completion variable while another task performs some work.
* When the other task has completed the work, it uses the completion variable to wake up any waiting tasks.

**Completion variables merely provide a simple solution to a problem whose answer is otherwise semaphores.**

## BKL: The Big Kernel Lock

The Big Kernel Lock (BKL) is a global spin lock that was created to ease the transition from Linux’s original SMP implementation to fine-grained locking. **It is not used anymore and has been removed from the Kernel since version 2.6.**

## Sequential Locks

The `sequential lock`, generally shortened to `seq lock`, is a newer type of lock. It provides a simple mechanism for reading and writing shared data.
It works by maintaining a sequence counter. Whenever the data in question is written to, a lock is obtained and a sequence number is incremented.

* Prior to and after reading the data, the sequence number is read.
* * If the values are the same, a write did not begin in the middle of the read.
* * Further, if the values are even, a write is not underway.

Grabbing the write lock makes the value odd, whereas releasing it makes it even because the lock starts at zero.

Seq locks are useful to provide a lightweight and scalable lock for use with many readers and a few writers.
**Seq locks, however, favor writers over readers. An acquisition of the write lock always succeeds as long as there are no other writers.**
Readers do not affect the write lock, as is the case with reader-writer spin locks and semaphores.
Furthermore, pending writers continually cause the read loop to repeat, until there are no longer any writers holding the lock.

Seq locks are ideal when your locking needs meet most or all these requirements:
* Your data has a lot of readers.
* Your data has few writers.
* Although few in number, you want to favor writers over readers and never allow readers to starve writers.
* Your data is simple, such as a simple structure or even a single integer that, for whatever reason, cannot be made atomic.

**A prominent user of the seq lock is `jiffies`, the variable that stores a Linux machine’s uptime.**
Jiffies holds a 64-bit count of the number of clock ticks since the machine booted.
On machines that cannot atomically read the full 64-bit `jiffies_64` variable, jiffies is implemented using seq locks.

## Preemption Disabling

**Because the kernel is preemptive, a process in the kernel can stop running at any instant to enable a process of higher priority to run.**
This means a task can begin running in the same critical region as a task that was preempted. To prevent this, the kernel preemption code uses spin locks as markers of nonpreemptive regions.
**If a spin lock is held, the kernel is not preemptive.** Because the concurrency issues with kernel preemption and SMP are
the same, and the kernel is already SMP-safe; this simple change makes the kernel preempt-safe, too.

In reality, some situations do not require a spin lock, but do need kernel preemption disabled.The most frequent of these situations is per-processor data.
If the data is unique to each processor, there might be no need to protect it with a lock because only that one processor can access the data.
If no spin locks are held, the kernel is preemptive, and it would be possible for a newly scheduled task to access this same variable, as shown here:

| Task A                                                                          | Task B                          |
|---------------------------------------------------------------------------------|---------------------------------|
| task A manipulates per-processor variable foo, which is not protected by a lock | —                               |
| task A is preempted                                                             | —                               |
| —                                                                               | task B is scheduled             |
| —                                                                               | task B manipulates variable foo |
| —                                                                               | task B completes                |
| task A is rescheduled                                                           | —                               |
| task A continues manipulating variable foo                                      | —                               |

Consequently, even if this were a uniprocessor computer, the variable could be accessed pseudo-concurrently by multiple processes.
Normally, this variable would require a spin lock (to prevent true concurrency on multiprocessing machines). If this were a perprocessor variable, however, it might not require a lock.

**To solve this, kernel preemption can be disabled via `preempt_disable()`.**
The call is nestable; it can be called any number of times. For each call, a corresponding call to ``preempt_enable()`` is required. The final corresponding call to `preempt_enable()` reenables preemption.

**The preemption count stores the number of held locks and `preempt_disable()` calls.**
* If the number is zero, the kernel is preemptive.
* If the value is one or greater, the kernel is not preemptive.

## Ordering and Barriers

**When dealing with synchronization between multiple processors or with hardware devices, it is sometimes a requirement that memory-reads (loads) and memory-writes (stores) issue in the order specified in your program code.**

When talking with hardware, you often need to ensure that a given read occurs before another read or write.
Additionally, on symmetrical multiprocessing systems, it might be important for writes to appear in the order that the code issues them (usually to ensure subsequent reads see the data in the same order).
Complicating these issues is the fact that both **the compiler and the processor can reorder `reads` and `writes` for performance reasons.**
Thankfully, all processors that do reorder reads or writes provide machine instructions to enforce ordering requirements.
It is also possible to instruct the compiler not to reorder instructions around a given point.

**These instructions are called `barriers`.**

Essentially, on some processors the following code may allow the processor to store the new value in `b` before it stores the new value in `a`:
```
a = 1;
b = 2;
```

Both the compiler and processor see no relation between a and b.
The compiler would perform this reordering at compile time; the reordering would be static, and the resulting object code would simply set `b` before `a`.
The processor, however, could perform the reordering dynamically during execution by fetching and dispatching seemingly unrelated instructions in whatever order it feels is best.
The vast majority of the time, such reordering is optimal because there is no apparent relation between `a` and `b`.
Sometimes the programmer knows best, though.

Although the previous example might be reordered, the processor would never reorder writes such as the following because there is clearly a data dependency between `a` and `b`:
```
a = 1;
b = a;
```

Neither the compiler nor the processor, however, knows about code in other contexts. Occasionally, it is important that writes are seen by other code and the outside world in the specific order that was intend.
This is often the case with hardware devices but is also common on multiprocessing machines.

* The `rmb()` method provides a read memory barrier. It ensures that no loads are reordered across the `rmb()` call. That is, no loads prior to the call will be reordered to after the call, and no loads after the call will be reordered to before the call.
* The `wmb()` method provides a write barrier. It functions in the same manner as `rmb()`, but with respect to stores instead of loads, it ensures no stores are reordered across the barrier.
* The `mb()` call provides both a read barrier and a write barrier. No loads or stores will be reordered across a call to `mb()`. It is provided because a single instruction (often the same instruction used by `rmb()`) can provide both the load and store barrier.

A variant of `rmb()`, `read_barrier_depends()`, provides a read barrier but only for loads on which subsequent loads depend.
All reads prior to the barrier are guaranteed to complete before any reads after the barrier that depend on the reads prior to the barrier.
Basically, it enforces a read barrier, similar to `rmb()`, but only for certain reads—those that depend on each other.
On some architectures, `read_barrier_depends()` is much quicker than `rmb()` because it is not needed and is, thus, a noop.

| Thread 1 | Thread 2 |
|----------|----------|
| `a = 3;` | —        |
| `mb();`  | —        |
| `b = 4;` | `c = b;` |
| —        | `rmb();` |
| —        | `d = a;` |

Without using the memory barriers, on some processors it is possible for `c` to receive the new value of `b`, whereas `d` receives the old value of `a`.
For example, `c` could equal four (what you’d expect), yet `d` could equal one (not what you’d expect).
Using the `mb()` ensured that `a` and `b` were written in the intended order, whereas the `rmb()` insured `c` and `d` were read in the intended order.

This sort of reordering occurs because modern processors dispatch and commit instructions out of order, to optimize use of their pipelines.
What can end up happening in the previous example is that the instructions associated with the loads of `b` and `a` occur out of order.

**The `rmb()` and `wmb()` functions correspond to instructions that tell the processor to commit any pending load or store instructions, respectively, before continuing.**

The `barrier()` method prevents the compiler from optimizing loads or stores across the call.
The compiler knows not to rearrange stores and loads in ways that would change the effect of the C code and existing data dependencies.
It does not have knowledge, however, of events that can occur outside the current context. For example, the compiler cannot know about interrupts that might read the same data you are writing, you might want to ensure a store is issued before a load.
The previous memory barriers also function as compiler barriers, but a compiler barrier is much lighter in weight than a memory barrier. Indeed, a compiler barrier is practically free, because it simply prevents the compiler from possibly rearranging things.

Note that the actual effects of the barriers vary for each architecture. For example, if a machine does not perform out-of-order stores (for example, Intel x86 processors do not), `wmb()` does nothing.
You can use the appropriate memory barrier for the worst case (that is, the weakest ordering processor) and your code will compile optimally for your architecture.
