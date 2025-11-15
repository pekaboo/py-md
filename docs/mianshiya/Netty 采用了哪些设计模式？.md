# Netty 采用了哪些设计模式？

**难度**：中等

**创建时间**：2025-10-06 15:48:55

## 答案
Netty 作为高性能网络通信框架，广泛采用了多种经典设计模式来优化其架构和功能实现，以下是其核心设计模式及具体应用：

### **1. 工厂模式（Factory Pattern）**
- **作用**：封装对象创建过程，提供灵活的实例化方式。
- **应用场景**：
  - **ChannelFactory**：根据配置创建不同类型的 `Channel`（如 NIO、Epoll），用户无需直接调用构造方法。
  - **EventLoopGroup**：通过抽象工厂创建事件循环组（如 `NioEventLoopGroup`、`EpollEventLoopGroup`），支持多 I/O 模型切换。
- **示例**：
  ```java
  EventLoopGroup group = new NioEventLoopGroup(); // 创建 NIO 事件循环组
  ServerBootstrap bootstrap = new ServerBootstrap();
  bootstrap.group(group).channel(NioServerSocketChannel.class); // 通过工厂创建 Channel
  ```

### **2. 责任链模式（Chain of Responsibility）**
- **作用**：将请求沿处理链传递，每个处理器决定是否处理或继续传递。
- **应用场景**：
  - **ChannelPipeline**：管理 `ChannelHandler` 链，事件按顺序通过入站（Inbound）和出站（Outbound）处理器。
  - **Handler 链**：如解码、业务逻辑处理、编码等任务由不同 `ChannelHandler` 依次完成。
- **示例**：
  ```java
  ChannelPipeline pipeline = ch.pipeline();
  pipeline.addLast(new DecoderHandler());  // 解码
  pipeline.addLast(new BusinessLogicHandler()); // 业务处理
  pipeline.addLast(new EncoderHandler());  // 编码
  ```

### **3. 观察者模式（Observer Pattern）**
- **作用**：定义一对多依赖关系，被观察者状态变化时通知观察者。
- **应用场景**：
  - **ChannelFuture**：异步操作返回 `ChannelFuture`，通过 `ChannelFutureListener` 监听操作结果。
  - **事件通知**：如 I/O 操作完成时触发回调。
- **示例**：
  ```java
  ChannelFuture future = channel.writeAndFlush(message);
  future.addListener(new ChannelFutureListener() {
      @Override
      public void operationComplete(ChannelFuture future) {
          if (future.isSuccess()) {
              System.out.println("发送成功");
          } else {
              System.err.println("发送失败: " + future.cause());
          }
      }
  });
  ```

### **4. 适配器模式（Adapter Pattern）**
- **作用**：将接口转换为客户端期望的形式，实现接口兼容。
- **应用场景**：
  - **ChannelHandlerAdapter**：简化 `ChannelHandler` 实现，开发者只需覆盖必要方法。
  - **ChannelInboundHandlerAdapter**：适配入站处理器接口。
- **示例**：
  ```java
  public class MyHandler extends ChannelInboundHandlerAdapter {
      @Override
      public void channelRead(ChannelHandlerContext ctx, Object msg) {
          System.out.println("收到消息: " + msg);
          ctx.fireChannelRead(msg); // 传递到下一个处理器
      }
  }
  ```

### **5. 单例模式（Singleton Pattern）**
- **作用**：确保全局唯一实例，提供全局访问点。
- **应用场景**：
  - **EventLoopGroup**：通常以单例形式使用，避免重复创建。
  - **资源管理器**：如 `ResourceLeakDetector` 通过静态内部类实现线程安全单例。
- **示例**：
  ```java
  public class ResourceLeakDetector {
      private static class Holder {
          static final ResourceLeakDetector INSTANCE = new ResourceLeakDetector();
      }
      public static ResourceLeakDetector getInstance() {
          return Holder.INSTANCE;
      }
  }
  ```

### **6. 策略模式（Strategy Pattern）**
- **作用**：封装可互换的算法，支持动态策略选择。
- **应用场景**：
  - **I/O 多路复用**：`EventLoopGroup` 根据运行环境选择策略（如 Linux 下优先用 Epoll）。
  - **编解码器**：支持多种序列化方式（如 Protobuf、JSON）动态切换。
- **示例**：
  ```java
  EventLoopGroup group = new EpollEventLoopGroup(); // Linux 高性能实现
  Bootstrap bootstrap = new Bootstrap();
  bootstrap.group(group).channel(EpollSocketChannel.class); // 使用 Epoll 策略
  ```

### **7. 装饰器模式（Decorator Pattern）**
- **作用**：动态为对象添加功能，无需修改结构。
- **应用场景**：
  - **LoggingHandler**：通过 `ChannelDuplexHandler` 添加日志功能。
  - **TrafficShapingHandler**：实现流量控制。
- **示例**：
  ```java
  public class LoggingHandler extends ChannelDuplexHandler {
      @Override
      public void channelRead(ChannelHandlerContext ctx, Object msg) {
          System.out.println("收到: " + msg);
          super.channelRead(ctx, msg);
      }
  }
  ```

### **8. 建造者模式（Builder Pattern）**
- **作用**：逐步构建复杂对象，支持链式调用。
- **应用场景**：
  - **ServerBootstrap**：通过链式调用配置服务端参数。
- **示例**：
  ```java
  ServerBootstrap bootstrap = new ServerBootstrap();
  bootstrap.group(group)
           .channel(NioServerSocketChannel.class)
           .childHandler(new ChannelInitializer<SocketChannel>() {
               @Override
               protected void initChannel(SocketChannel ch) {
                   ch.pipeline().addLast(new EchoServerHandler());
               }
           });
  ```

### **9. 原型模式（Prototype Pattern）**
- **作用**：通过克隆创建对象，减少重复初始化开销。
- **应用场景**：
  - **ByteBuf 克隆**：通过 `ByteBuf.copy()` 创建缓冲区副本。
- **示例**：
  ```java
  ByteBuf buf = Unpooled.buffer(1024);
  buf.writeBytes("Hello, Netty".getBytes());
  ByteBuf clonedBuf = buf.copy(); // 创建副本
  ```

### **10. 桥接模式（Bridge Pattern）**
- **作用**：解耦抽象与实现，支持独立变化。
- **应用场景**：
  - **Channel 实现**：桥接不同传输实现（如 NIO、Epoll）。
- **示例**：
  ```java
  Channel channel = new NioSocketChannel(); // NIO 实现
  // Channel channel = new EpollSocketChannel(); // Epoll 实现
  ```

### **11. 享元模式（Flyweight Pattern）**
- **作用**：共享对象以减少内存占用。
- **应用场景**：
  - **ByteBufAllocator**：通过对象池复用 `ByteBuf` 对象。
- **示例**：
  ```java
  ByteBufAllocator allocator = ch.alloc();
  ByteBuf buf1 = allocator.buffer(1024);
  ByteBuf buf2 = allocator.buffer(1024); // 复用缓冲区
  ```

### **12. 模板方法模式（Template Method Pattern）**
- **作用**：定义算法骨架，延迟部分步骤到子类实现。
- **应用场景**：
  - **SimpleChannelInboundHandler**：提供模板方法，子类重写特定逻辑。
- **示例**：
  ```java
  public abstract class SimpleChannelInboundHandler<I> extends ChannelInboundHandlerAdapter {
      @Override
      public void channelRead(ChannelHandlerContext ctx, Object msg) {
          if (msg instanceof I) {
              channelRead0(ctx, (I) msg); // 子类实现具体逻辑
          }
      }
      protected abstract void channelRead0(ChannelHandlerContext ctx, I msg);
  }
  ```
