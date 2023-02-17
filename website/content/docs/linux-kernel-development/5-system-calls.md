+++
title = "5. System Calls"
description = " "
+++

### System Calls

In any modern operating system, **the kernel provides a set of interfaces by which processes running in user-space can interact with the system.** These interfaces give applications controlled access to hardware, a mechanism with which to create new processes and communicate with existing ones, and the capability to request other operating system resources. The existence of these interfaces, and the fact that applications are not free to directly do whatever they want, is key to providing a stable system.

### Communicating with the Kernel

System calls provide a layer between the hardware and user-space processes, which serves three primary purposes:

* **Providing an abstracted hardware interface for userspace.**
* * For example, when reading or writing from a file, applications are not concerned with the type of disk, media, or even the type of filesystem on which the file resides.
* **Ensuring system security and stability.**
* * The kernel acts as a middleman between system resources and user-space, so it can arbitrate access based on permissions, users, and other criteria. For example, this arbitration prevents applications from incorrectly using hardware, stealing other processes’ resources, or otherwise doing harm to the system.
* **A single common layer between user-space and the rest of the system allows for the virtualized system provided to processes.**
* * It would be impossible to implement multitasking and virtual memory if applications were free to access access system resources without the kernel’s knowledge.

**In Linux, system calls are the only means user-space has of interfacing with the kernel** and the only legal entry point into the kernel other than exceptions and traps. Other interfaces, such as device files or /proc, are ultimately accessed via system calls. Interestingly, Linux implements far fewer system calls than most systems.

### APIs, POSIX, and the C Library

**Applications are typically programmed against an Application Programming Interface (API) implemented in user-space, not directly to system calls**, because no direct correlation is needed between the interfaces used by applications and the actual interface provided by the kernel.
An API defines a set of programming interfaces used by applications. Those interfaces can be implemented as a system call, implemented through multiple system calls, or implemented without the use of system calls at all.
The same API can exist on multiple systems and provide the same interface to applications while the implementation of the API itself can differ greatly from system to system.

![Relationship between a POSIX API, the C library, and system calls.](https://raw.githubusercontent.com/wdhif/grimoire/master/website/static/linux-kernel-development/figure_5.1.png)

The most common APIs in the Unix world is based on POSIX. Technically, POSIX is composed of a series of standards from the IEEE that aim to provide a portable operating system standard roughly based on Unix. Linux strives to be POSIX- and SUSv3-compliant where applicable.

On most Unix systems, the POSIX-defined API calls have a strong correlation to the system calls. Some systems that are rather un-Unix, such as Microsoft Windows, offer POSIX-compatible libraries.

**The system call interface in Linux, as with most Unix systems, is provided in part by the C library.**

The C library implements the main API on Unix systems, including the standard C library and the system call interface.
The C library is used by all C programs and, because of C’s nature, is easily wrapped by other programming languages for use in their programs. The C library additionally provides the majority of the POSIX API.

From the application programmer’s point of view, system calls are irrelevant; all the programmer is concerned with is the API.
Conversely, the kernel is concerned only with the system calls; what library calls and applications make use of the system calls is not of the kernel’s concern. Nonetheless, it is important for the kernel to keep track of the potential uses of a system call and keep the system call as general and flexible as possible.

### Syscalls

**System calls (often called syscalls in Linux) are typically accessed via function calls defined in the C library.**
