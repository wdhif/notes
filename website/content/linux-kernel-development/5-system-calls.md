+++
title = "5. System Calls"
+++

**In processes any modern operating system, the kernel provides a set of interfaces by which running in user-space can interact with the system.**
These interfaces give applications:
* Controlled access to hardware.
* A mechanism with which to create new processes.
* A mechanism to communicate with existing processes.
* The capability to request other operating system resources.

**The interfaces act as the messengers between applications and the kernel**, with the applications issuing various requests and the kernel fulfilling them (or returning an error). The existence of these interfaces, and the fact that applications are not free to directly do whatever they want, is key to providing a stable system.

### Communicating with the Kernel

**System calls provide a layer between the hardware and user-space processes.**
This layer serves three primary purposes:
* **It provides an abstracted hardware interface for user-space.** When reading or writing from a file, for example, applications are not concerned with the type of disk, media, or even the type of filesystem on which the file resides.
* **System calls ensure system security and stability.** With the kernel acting as a middle-man between system resources and user-space, the kernel can arbitrate access based on permissions, users, and other criteria. For example, this arbitration prevents applications from incorrectly using hardware, stealing other processes’ resources, or otherwise doing harm to the system. 
* **A single common layer between user-space and the rest of the system allows for the virtualized system provided to processes to work**, if applications were free to access system resources without the kernel’s knowledge, it would be nearly impossible to implement multitasking and virtual memory, and certainly impossible to do so with stability and security.

**In Linux, system calls are the only means user-space has of interfacing with the kernel**. They are the only legal entry point into the kernel other than exceptions and traps. Even other interaces like **devices files** or **/proc** are ultimately accessed via system calls

### APIs, POSIX and the C Library

**Typically, applications are programmed against an Application Programming Interface (API) implemented in user-space, not directly to system calls.** This is important because no direct correlation is needed between the interfaces that applications make use of and the actual interface provided by the kernel.
**An API defines a set of programming interfaces used by applications.**
Those interfaces can be implemented as a system call, implemented through multiple system calls, or implemented without the use of system calls at all.
The same API can exist on multiple systems and provide the same interface to applications while the implementation of the API itself can differ greatly from system to system.

![The relationship between applications, the C library, and the kernel with a call to printf().](https://user-images.githubusercontent.com/5231539/94372623-8b614400-00ff-11eb-838d-661788dbbde5.png)

**One of the more common application programming interfaces in the Unix world is based on the POSIX standard.**
Technically, POSIX is composed of a series of standards from the IEEE that aim to provide a portable operating system standard roughly based on Unix. Linux strives to be POSIX- and SUSv3-compliant where applicable.
**POSIX is an excellent example of the relationship between APIs and system calls.** On most Unix systems, the POSIX-defined API calls have a strong correlation to the system calls.

**The system call interface in Linux, as with most Unix systems, is provided in part by the C library.** The C library implements the main API on Unix systems, including the standard C library and the system call interface. **It is used by all C programs and can be wrapped in other programing languages to be used in their programs.**

**For the programmer, system calls are irrelevant, he only uses the API. On the other hand, the Kernel is only concerned by system calls sent by the API.**

{{<mermaid>}}
graph LR;
    A[Programmer] -->|C Library| B[API]
    B[API] -->|System calls| C[Kernel]
{{< /mermaid >}}

**The kernel is concerned only with the system calls. What library calls and applications make use of the system calls is not of the kernel’s concern**, it will “Provide mechanism, not policy.”.

### Syscalls

**System calls**, or **syscalls** are typically **accessed via function calls defined in the C library**.
They can define zero, one, or more arguments (inputs) and might result in one or more side effects, for example writing to a file or copying some data into a provided pointer.
System calls also provide a return value of type long that signifies success or error, usually, although not always:
* **A negative return value denotes an error.**
* **A return value of zero is usually a sign of success.**

Finally, **system calls have a defined behavior**. For example, the system call **getpid()** is defined to **return an integer that is the current process’s PID**.

### System Call Numbers

**Each syscall is assigned a syscall number.** This is a unique number that is used to reference a specific system call. When a user-space process executes a system call, the syscall number identifies which syscall was executed. **The process does not refer to the syscall by name.**

**The syscall number is important, when assigned, it cannot change, or compiled applications will break.** **If a system call is removed, its system call number cannot be recycled**, or previously compiled code would aim to invoke one system call but would in reality invoke another. To avoid that, Linux implement a **"not implemented"** system call which return **-ENOSYS** (Error No Syscall). This function is used to “plug the hole” in the rare event that a syscall is removed or otherwise made unavailable.

### System Call Performance

Linux's system calls are fast, partly because of fast Linux's context switch between kernel-space and user-space.

### System Call Handler

**It is not possible for user-space applications to execute kernel code directly.** They cannot simply make a function call to a method existing in kernel-space because the kernel exists in a protected memory space.
**If applications could directly read and write to the kernel’s address space, system security and stability would be nonexistent.**

Instead, **user-space applications must somehow signal to the kernel that they want to execute a system call** and have the system switch to kernel mode, where **the system call can be executed in kernel-space by the kernel** on behalf of the application.

**The mechanism to signal the kernel is a software interrupt.**
Incur an exception, and the system will switch to kernel mode and execute the exception handler. **The exception handler, in this case, is actually the system call handler.**
The defined software interrupt on x86 is interrupt number 128. It triggers a switch to kernel mode and the execution of exception vector 128, which is the **system call handler**.

**Basically, to call the system call handler, a user-space program must trigger the exception 128.**

### Denoting the Correct System Call

Simply entering kernel-space alone is not sufficient because multiple system calls exist, all of which enter the kernel in the same manner. **Thus, the system call number must be passed into the kernel.**

To do this, the **user-space** program will put in the **eax** register the **system call number** it needs, and then raise **the 128 exception**. Then, in **kernel-space**, the **system call handler** will read the **eax** register to **execute the correct system call**.

![Invoking the system call handler and executing a system call.](https://user-images.githubusercontent.com/5231539/94994947-298b5900-059b-11eb-9de2-204a3935e89d.png)

### Parameter Passing

**In addition to the system call number, most syscalls require that one or more parameters be passed to them.**

Somehow, user-space must relay the parameters to the kernel during the trap. The easiest way to do this is via the same means that the syscall number is passed. **The parameters are stored in registers.**
On x86-32, **the registers ebx , ecx , edx , esi , and edi contain, in order, the first five arguments**. In the unlikely case of six or more arguments, a single register is used to hold a pointer to user-space where all the parameters are stored.

**The return value is sent to user-space also via register. On x86, it is written into the eax register.**

### System Call Implementation
