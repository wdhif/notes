+++
title = "Process Management"
+++

### The Process

A **process, or task in the Kernel, is a program (object code) that is currently running**, but a program is not a process, **two or more processes can actually run the same program at the same time.**

They are more than juste code (text section), they also include a set of resources such as:
* Open files.
* Pending signals.
* Internal Kernel data.
* Processor state.
* A memory address space with one or more mappings.
* One or more threads of execution.
* A data section containing global variables.

**Threads of execution**, or **threads**, are the objects of activity within the process.
Each thread includes:
* A unique program counter.
* A Process stack.
* A set of processor registers.

**The kernel schedules individual threads, not processes.**

Process that runs more than one thread are call **multithreaded**.

On modern operating systems, processes provide two virtualizations:
* **A virtualized processor**: The virtual processor gives the process the illusion that it alone monopolizes the system, despite possibly sharing the processor among hundreds of other processes.
* **A virtual memory**:Virtual memory lets the process allocate and manage memory as if it alone owned all the memory in the system.

**Note that threads share the virtual memory abstraction, but they each receives their own virtualized processor.**

## Process lifecycle

The process lifecycle goes as follow:
* **fork()**: A **parent process** will run the **fork()** system call, effectively cloning himself (**fork()** is implemented using **clone()**) into a **child process**. The parent process will then resume execution and the child process will start execution at the same place, **where the fork() system call returns**. **fork()** will in fact return twice, once in the parent process, and once in the child process. At some point however, the parent process **will have to run a wait() type system call** to **reap** its exited child process.
* **exec()**: After its creation, the child process will run one of the **exec()** system calls that will create a new address space and load a new program into it.
* **exit()**: Finally, when a process exits, it run the **exit()** system call.  This will terminate the process and free all its ressources. The process will then be placed in a **zombie state** and until its parent process run the **wait4()** system call.

### Process Descriptor and the Task Structure

The kernel stores the list of processes in a circular doubly linked list called the **task list**. Each element of this list is called a **process descriptor** that will contain all informations about a given process.

The system identifies processes by a unique process identification value or **PID**, stored in the **process descriptor**. The PID is typically an integer going up to 32,768.
**This maximum value is important because it is essentially the maximum number of processes that may exist concurrently on the system.**

**The Kernel will affect PID to each process in an ascending order**, this creates the notion that the **higher the PID, the later the process started**. But if the maximum number of PID is reached, then it will wrap back and try to affect freed PID to new process, detroying this useful notion.

You can also increase this value up to four millons, by modifying /proc/sys/kernel/pid_max. Take note that this might break compatibility with older programs.

### Process State

The **state** field of the **process descriptor** describes the current condition of the process.
**Each process on the system is in exactly one of the five following states:**
* **TASK_RUNNING**: The process is runnable, it is either currently running or on a runqueue waiting to run. This is the only possible state for a process executing in user-space. It can also apply to a process in kernel-space that is actively running.
* **TASK_INTERRUPTIBLE**: The process is sleeping, or blocked, waiting for some condition to exist. When this condition exists, the kernel sets the process’s state to **TASK_RUNNING**. The process also **awakes prematurely and becomes runnable if it receives a signal**.
* **TASK_UNINTERRUPTIBLE**: This state is identical to **TASK_INTERRUPTIBLE** except that it does not wake up and become runnable if it receives a signal. This is used in situations where the process must wait without interruption or when the event is expected to occur quite quickly. Because the task does not respond to signals in this state, **TASK_UNINTERRUPTIBLE** is less often used than **TASK_INTERRUPTIBLE**.
* **__TASK_TRACED**: The process is being traced by another process, such as a debugger (like strace), using the **ptrace()** system call.
* **__TASK_STOPPED**: Process execution has stopped. The task is not running nor is it eligible to run. This occurs if the task receives the **SIGSTOP**, **SIGTSTP**, **SIGTTIN**, or **SIGTTOU** signal or if it receives any signal while it is being debugged.

Take note that a process in the **TASK_UNINTERRUPTIBLE** state will not even respond to **SIGKILL**. This state is represented by the famous **D** state in the **ps** command.

![Flow chart of process states.](https://user-images.githubusercontent.com/5231539/93128748-42a59600-f6d0-11ea-95d9-be06909f7d8c.png)
