# 说说你知道的几种 I/O 模型

**难度**：中等

**创建时间**：2025-10-06 15:36:58

## 答案
I/O（输入/输出）模型是操作系统处理数据读写的核心机制，直接影响程序的并发性能和资源利用率。不同模型在阻塞行为、线程/进程管理、系统调用方式等方面有显著差异。以下是常见的几种 I/O 模型及其特点：

---

### **1. 阻塞 I/O（Blocking I/O）**
**原理**：  
当进程发起 I/O 操作（如 `read`、`write`）时，若数据未就绪，内核会将进程挂起（阻塞），直到操作完成才返回。  
**特点**：  
- **简单直观**：代码逻辑清晰，易于实现。  
- **效率低**：单个线程/进程在同一时间只能处理一个 I/O 操作，其他操作需等待。  
- **适用场景**：单线程简单程序或对并发要求不高的场景。  

**示例**：  
```c
int fd = open("file.txt", O_RDONLY);
char buf[1024];
ssize_t n = read(fd, buf, sizeof(buf)); // 阻塞直到数据就绪
```

---

### **2. 非阻塞 I/O（Non-blocking I/O）**
**原理**：  
进程发起 I/O 操作时，若数据未就绪，内核立即返回错误（如 `EWOULDBLOCK` 或 `EAGAIN`），进程需不断轮询检查数据状态。  
**特点**：  
- **高并发潜力**：单个线程可管理多个 I/O 操作（通过轮询）。  
- **CPU 浪费**：频繁轮询导致 CPU 空转。  
- **适用场景**：需要低延迟但能容忍轮询开销的场景（如嵌入式系统）。  

**示例**：  
```c
int fd = open("file.txt", O_RDONLY | O_NONBLOCK); // 设置为非阻塞
char buf[1024];
ssize_t n;
while ((n = read(fd, buf, sizeof(buf))) == -1 && errno == EAGAIN) {
    // 轮询或执行其他任务
}
```

---

### **3. I/O 多路复用（I/O Multiplexing）**
**原理**：  
通过一个系统调用（如 `select`、`poll`、`epoll`）同时监听多个文件描述符（fd）的 I/O 事件（可读、可写、错误等），当某个 fd 就绪时，内核通知进程处理。  
**特点**：  
- **高效管理多连接**：单线程可处理数千个并发连接（如 Nginx）。  
- **减少线程开销**：避免为每个连接创建线程。  
- **复杂度较高**：需手动处理事件分发和回调。  

**常见实现**：  
- **`select`/`poll`**：  
  - 跨平台但性能有限（`select` 有 fd 数量限制，`poll` 无限制但需遍历所有 fd）。  
- **`epoll`（Linux）**：  
  - 基于事件驱动，仅返回就绪的 fd，性能最优（适合高并发）。  
- **`kqueue`（BSD）**：  
  - 类似 `epoll`，但支持更多事件类型（如文件修改通知）。  

**示例（epoll）**：  
```c
int epoll_fd = epoll_create1(0);
struct epoll_event event, events[10];
event.events = EPOLLIN;
event.data.fd = sockfd;
epoll_ctl(epoll_fd, EPOLL_CTL_ADD, sockfd, &event);

while (1) {
    int n = epoll_wait(epoll_fd, events, 10, -1); // 阻塞等待事件
    for (int i = 0; i < n; i++) {
        if (events[i].data.fd == sockfd) {
            // 处理就绪的 fd
        }
    }
}
```

---

### **4. 信号驱动 I/O（Signal-Driven I/O）**
**原理**：  
进程通过 `fcntl` 或 `signal` 注册信号处理函数，当 fd 就绪时，内核发送信号（如 `SIGIO`）通知进程，进程在信号处理函数中执行 I/O 操作。  
**特点**：  
- **异步通知**：避免轮询，但信号处理可能中断主流程。  
- **适用场景**：对实时性要求高且能处理信号的场景（如 Unix 工具）。  

**示例**：  
```c
void sigio_handler(int sig) {
    // 处理 I/O 就绪事件
}

int fd = open("file.txt", O_RDONLY);
fcntl(fd, F_SETOWN, getpid()); // 设置进程为 fd 的所有者
fcntl(fd, F_SETFL, FASYNC);    // 启用异步通知
signal(SIGIO, sigio_handler);  // 注册信号处理函数
```

---

### **5. 异步 I/O（Asynchronous I/O, AIO）**
**原理**：  
进程发起 I/O 操作后立即返回，内核在后台完成操作，并通过回调、信号或未来对象（如 Linux 的 `io_uring`）通知进程结果。  
**特点**：  
- **完全非阻塞**：进程无需等待或轮询，可继续执行其他任务。  
- **实现复杂**：依赖操作系统支持（如 Linux 的 `libaio`、Windows 的 IOCP）。  
- **适用场景**：高并发、低延迟需求（如数据库、实时系统）。  

**示例（Linux AIO）**：  
```c
#include <libaio.h>
struct iocb cb = {0};
struct iocb *cbs[] = {&cb};
char buf[1024];
io_prep_pread(&cb, fd, buf, sizeof(buf), 0); // 准备异步读

io_submit(aio_context, 1, cbs); // 提交异步请求
struct io_event events[1];
io_getevents(aio_context, 1, 1, events, NULL); // 等待完成
```

**现代替代方案（io_uring）**：  
Linux 5.1+ 引入的 `io_uring` 提供更高效的异步 I/O 接口，支持提交和完成队列分离，减少系统调用开销。

---

### **模型对比总结**
| 模型          | 阻塞行为       | 并发能力       | 系统调用次数 | 复杂度 | 典型应用               |
|---------------|----------------|----------------|--------------|--------|------------------------|
| 阻塞 I/O      | 阻塞           | 低             | 高           | 低     | 简单命令行工具         |
| 非阻塞 I/O    | 不阻塞（轮询） | 中             | 高           | 中     | 嵌入式系统             |
| I/O 多路复用  | 阻塞（等事件） | 高             | 低           | 高     | Nginx、Redis           |
| 信号驱动 I/O  | 不阻塞（信号） | 中             | 低           | 高     | Unix 实时工具          |
| 异步 I/O      | 不阻塞         | 最高           | 最低         | 最高   | 数据库、高性能服务器   |

---

### **选择建议**
- **低并发、简单逻辑**：阻塞 I/O。  
- **高并发连接管理**：I/O 多路复用（`epoll`/`kqueue`）。  
- **极致性能需求**：异步 I/O（`io_uring` 或 Windows IOCP）。  
- **避免非阻塞 I/O 的轮询开销**：优先使用多路复用或异步模型。  

理解这些模型有助于根据业务场景（如响应时间、吞吐量、资源限制）选择最优方案。
