+++
title = "Introduction to the Linux Kernel"
+++

### Introduction to Unix

Unix is a family of operating systems featuring a similar API and design, including Unix, BSD, Solaris and Linux.

Some Unix characteristics that are at the core of its strength:

* Unix is simple: only hundreds of system calls and have a straightforward, even basic, design.
* In Unix, everything is a file: simplifies the manipulation of data and devices into a set of core system calls: open(),read(), write(), lseek(), and close().
* Unix has robust IPC (Interprocess communication) systems.

### Overview of Operating Systems and Kernels
The operating system is the parts of the system responsible for basic use and administration.
The kernel is the innermost portion of the operating system. It is the core internals: the software that provides basic services for all other parts of the system, manages hardware, and distributes system resource.

An OS contains:

* Kernel:
  * Interrupt handlers to service interrupt requests.
  * A scheduler to share processor time among multiple processes.
  * A memory management system to manage process address spaces.
  * System services such as networking and interprocess communication.
* Device drivers
* Boot loader
* Command shell
* User interfaces
* Basic utilities

#### Kernel-space and User-space
**Kernel-space**: on modern systems with protected memory management units, the kernel typically resides in an elevated system state, which includes a protected memory space and full access to the hardware. This system state and memory space is collectively referred to as kernel-space.

**User-space**: applications execute in user-space, where they can access a subset of the machine’s available resources and can perform certain system functions, directly access hardware, access memory outside of that allotted them by the kernel, or otherwise misbehave.

When executing kernel code, the system is in kernel-space executing in kernel mode. When running a regular process, the system is in user-space executing in user mode.

Applications running on the system comminicate with the kernel using **system calls** ([Figure 1.1](https://raw.githubusercontent.com/wdhif/grimoire/master/website/static/linux-kernel-development/figure_1.1.png))

Basically, an application will use a C library to use the system call interface. The system calls will allow the Kernel to do operation on behalf of the application.
Furthermore, the application is said to be executing a system call in **kernel-space**, and the kernel is running in **process context**.

Some function of this C library provide many feature not found in system calls, E.G. the `printf()` function will not only wall the `write()` system call but will also do formating, etc...

On the other hand, the `open()` function simply use the `open()` system call. Other functions of this C library does not use system calls at all, E.G. `strcpy()`


![Relationship between applications, the kernel, and hardware.](https://raw.githubusercontent.com/wdhif/grimoire/master/website/static/linux-kernel-development/figure_1.1.png)

