---
title: Linux+devops
description: Linux+devops
---

```
    ```## 1. linux 常用命令学习

### 1.1.✅  内容查找
(1) 递归搜索当前文件夹下所有 md2html.config.yaml 文件，查找包含 'py-md' 的内容 grep -r 'py-md' . --include="md2html.config.yaml"

### 1.2.✅  目录文件相关
(1)...
    ⚠️注意事项
    ```
按照上述markdown代码格式输出 linux 常用命令。
```

# Linux+devops
## 1. linux 常用命令学习

### 1.1.✅ 内容查找
(1) 递归搜索指定文件含目标字符串：grep -r 'py-md' . --include="md2html.config.yaml"
(2) 查找文件含目标字符串并显示行号：grep -n 'error' test.txt
(3) 忽略大小写搜索指定类型文件：grep -ri 'warning' . --include="*.log"
(4) 正则匹配开头字符串：grep -r '^user-' . --include="*.conf"
(5) 统计目标字符串出现次数：grep -ro 'target' . --include="*.txt" | wc -l
⚠️注意事项：字符串含特殊字符需用引号包裹；大目录搜索用 --include/--exclude 过滤提升效率；Linux 大小写敏感，-i 忽略大小写

### 1.2.✅ 目录文件操作（查看/切换/创建/删除/复制/移动）
#### 查看目录文件（ls）
(1) 列出所有文件（含隐藏）：ls -a
(2) 详细显示文件属性：ls -l
(3) 人类可读格式显示大小：ls -lh
(4) 按修改时间倒序排列：ls -lht
(5) 过滤特定类型文件：ls -lh *.jar
#### 切换目录（cd）
(1) 切换绝对路径：cd /usr/local
(2) 切换相对路径：cd docs
(3) 回退上一级目录：cd ..
(4) 切换用户主目录：cd ~
(5) 回退上一次目录：cd -
#### 创建（mkdir/touch）
(1) 创建单目录：mkdir test
(2) 创建多级目录：mkdir -p parent/child/grandchild
(3) 创建空文件：touch empty.txt
(4) 批量创建空文件：touch file1.txt file2.log
(5) 自定义文件时间：touch -d "2025-11-01 14:30" old_file.txt
#### 删除（rm）
(1) 删除文件：rm test.txt
(2) 强制删除文件：rm -f old.log
(3) 删除空目录：rm -d empty_dir
(4) 递归删除目录及内容：rm -rf dir
(5) 批量删除特定文件：rm -f *.tmp
#### 复制（cp）
(1) 复制文件到目标目录：cp test.txt /home/user
(2) 递归复制目录：cp -r dir /opt
(3) 保留属性复制：cp -p test.txt backup/
(4) 复制并改名：cp test.txt backup/test_backup.txt
(5) 批量复制文件：cp file1.txt file2.log docs/
#### 移动/重命名（mv）
(1) 文件重命名：mv test.txt test_new.txt
(2) 移动目录：mv dir /opt
(3) 批量移动文件：mv *.log logs/
(4) 移动并提示覆盖：mv -i source.txt target.txt
(5) 按日期重命名：mv app.log app_$(date +%Y%m%d).log
⚠️注意事项：删除操作（rm -rf）不可逆，禁用 rm -rf /；复制/移动目录需加 -r 递归；含空格的文件/目录用引号包裹或转义符处理

### 1.3.✅ 统计与时间修改
#### 统计（wc）
(1) 统计文件行数/单词数/字节数：wc test.txt
(2) 只统计行数：wc -l app.log
(3) 只统计单词数：wc -w article.md
(4) 统计字符数（支持中文）：wc -m test.txt
(5) 统计命令输出行数：ls -l *.java | wc -l
#### 时间修改（touch）
(1) 更新文件访问时间：touch -a test.txt
(2) 更新文件修改时间：touch -m test.txt
(3) 同步参考文件时间：touch -r ref.txt target.txt
(4) 批量创建带序号文件：for i in {1..5}; do touch "log_$i.txt"; done
⚠️注意事项：wc 统计中文时 -c 算字节数，-m 算字符数；touch 无法创建目录，仅修改目录时间戳

### 1.4.✅ 压缩与解压
#### tar 格式（支持 .tar/.tar.gz/.tar.bz2）
(1) 打包压缩为 .tar.gz：tar -zcvf archive.tar.gz docs/ src/
(2) 解压 .tar.gz 到当前目录：tar -zxvf archive.tar.gz
(3) 解压到指定目录：tar -zxvf archive.tar.gz -C /opt/extract/
(4) 查看压缩包内容：tar -ztvf archive.tar.gz
(5) 打包排除指定文件：tar -zcvf archive.tar.gz --exclude="*.log" project/
#### zip 格式（跨平台兼容）
(1) 压缩文件/目录：zip package.zip file1.txt dir/
(2) 解压到当前目录：unzip package.zip
(3) 解压到指定目录：unzip package.zip -d /opt/unzip/
(4) 查看压缩包内容：unzip -l package.zip
(5) 加密压缩文件：zip -P 123456 secure.zip secret.txt
⚠️注意事项：tar 不同压缩格式对应不同参数（.tar.gz/-z、.tar.bz2/-j）；zip 压缩目录需加 -r 递归；中文文件名解压乱码用 unzip -O UTF-8 处理

### 1.5.✅ Java 相关命令
(1) 编译 Java 源码：javac HelloWorld.java
(2) 运行 Java 程序：java HelloWorld
(3) 查看 Java 进程：jps
(4) 监控 GC 状态：jstat -gc 12345 1s
(5) 生成堆快照：jmap -dump:format=b,file=heap.hprof 12345
(6) 查看线程堆栈：jstack 12345 > thread_dump.txt
(7) 运行可执行 jar 包：java -jar app.jar --spring.profiles.active=prod
⚠️注意事项：运行程序需指定主类（含 main 方法）；类路径用 : 分隔（Windows 用 ;）；堆快照生成可能耗时，避免高并发场景频繁执行
⚠️其他：
java -Xms512m -Xmx1024m -XX:+UseG1GC -cp ./target/classes com.example.HelloWorld
常用 JVM 参数说明：
-Xms512m：堆初始内存（默认物理内存 1/64）；
-Xmx1024m：堆最大内存（默认物理内存 1/4）；
-XX:+UseG1GC：使用 G1 垃圾收集器；
-XX:+PrintGCDetails：打印 GC 详细日志；
-XX:MetaspaceSize=128m：元空间初始大小。
适用场景：生产环境部署（调整内存、GC 策略）、性能测试（模拟特定 JVM 配置）。

⚠️## 1. linux 常用命令学习

### 1.5.✅ Java 常用命令总结（核心功能+关键用法+适用场景）
#### 一、编译命令（javac）—— 源码→字节码
(1) 基础单文件编译：`javac HelloWorld.java` → 无依赖独立文件编译，生成同名 .class
(2) 指定输出目录：`javac -d ./target/classes src/com/example/HelloWorld.java` → 按包名生成目录，适配 Maven/Gradle 结构
(3) 引入依赖 jar：`javac -cp lib/*:./target/classes src/*.java` → 依赖第三方库或自定义类时使用
(4) 指定编码格式：`javac -encoding UTF-8 src/HelloWorld.java` → 解决跨系统编码不一致问题
(5) 批量编译文件：`javac -cp lib/* src/com/example/*.java` → 同一包下多个关联源码编译

#### 二、运行命令（java）—— 执行字节码/jar 包
(1) 运行单 .class 文件：`java HelloWorld` → 无依赖字节码文件直接运行
(2) 运行带包名 .class：`java -cp ./target/classes com.example.HelloWorld` → 按全包名指定主类，适配包结构
(3) 运行可执行 jar：`java -jar app.jar --spring.profiles.active=prod` → Spring Boot 应用部署常用，支持传递程序参数
(4) 配置 JVM 参数运行：`java -Xms512m -Xmx1024m -XX:+UseG1GC -cp ./target/classes com.example.HelloWorld` → 生产环境调整内存、GC 策略
(5) 多依赖运行：`java -cp ./target/classes:lib/* com.example.Test` → 未打包为可执行 jar 时，指定所有依赖路径

#### 三、进程监控命令（jps/jstat/jinfo）—— 查看进程状态
(1) 查看 Java 进程：`jps`（基础）/ `jps -l`（显示主类全路径）/ `jps -v`（显示 JVM 参数）→ 快速获取目标进程 ID（PID）
(2) 监控 GC 状态：`jstat -gc 12345 1s 10` → 查看新生代/老年代使用、GC 次数/耗时，排查 GC 频繁问题
(3) 查看 JVM 参数：`jinfo 12345`（所有参数）/ `jinfo -flag Xmx 12345`（指定参数）→ 验证 JVM 配置是否生效
(4) 动态修改参数：`jinfo -flag +PrintGCDetails 12345` → 部分参数支持动态调整，无需重启应用

#### 四、内存分析命令（jmap/jhat）—— 排查内存问题
(1) 生成堆快照：`jmap -dump:format=b,file=heap.hprof 12345` → 生成 .hprof 文件，分析内存泄漏、大对象
(2) 查看堆概况：`jmap -heap 12345` → 快速了解堆内存配置、各区域使用占比
(3) 分析堆快照：`jhat -port 8080 heap.hprof` → 启动 Web 服务初步分析快照，生产环境推荐用 MAT 工具

#### 五、线程分析命令（jstack）—— 排查线程问题
(1) 生成线程堆栈：`jstack 12345 > thread_dump.txt` → 保存线程状态、调用链路，分析阻塞、无响应问题
(2) 排查死锁：`jstack -l 12345` → 检测死锁，输出死锁线程及持锁信息
(3) 定位高 CPU 线程：`top -H -p 12345` → 查高 CPU 线程 ID（十进制）→ `printf "%x\n" 线程ID` → `jstack 12345 | grep -A 20 "十六进制ID"`

#### 六、高级/辅助命令（jstatd/jcmd）
(1) 远程监控服务：`jstatd -J-Djava.security.policy=jstatd.policy` → 支持本地工具（JVisualVM）远程连接监控
(2) 多功能命令（JDK7+）：`jcmd`（查进程）/ `jcmd 12345 GC.heap_dump heap.hprof`（生成堆快照）/ `jcmd 12345 Thread.print`（线程堆栈）→ 集成多命令功能，简化操作

⚠️注意事项
1. 环境依赖：需安装 JDK 并配置 `JAVA_HOME`，JRE 仅支持 `java` 命令，不支持编译/监控命令（javac/jmap 等）；
2. 路径分隔符：Linux/Mac 用 `:` 分隔类路径，Windows 用 `;`，避免跨系统执行报错；
3. 生产环境慎用：`jmap`/`jstack` 会导致 JVM 短暂 STW，高并发时段需避开，选择低峰期执行；
4. 权限与兼容性：执行命令需与 Java 进程启动用户一致，避免权限不足；不同 JDK 版本命令参数有差异，需适配版本；
5. 大文件处理：堆快照文件可能达 GB 级，需确保磁盘空间充足，分析优先用 MAT 而非 jhat。


### 1.6.✅ Docker 相关命令
(1) 拉取镜像：docker pull nginx:latest
(2) 运行容器（后台+端口映射）：docker run -d -p 80:80 --name my-nginx nginx
(3) 查看运行中容器：docker ps
(4) 查看容器日志：docker logs -f my-nginx
(5) 构建镜像：docker build -t my-app:v1.0 .
(6) 进入容器终端：docker exec -it my-nginx /bin/bash
(7) 数据卷挂载：docker run -d -v /host/data:/container/data --name my-app my-app:v1.0
⚠️注意事项：端口映射需确保宿主机端口未占用；挂载目录权限不足需调整宿主机权限；多容器建议用 docker-compose 管理

### 1.7.✅ Kubernetes（k8s）相关命令
(1) 查看当前命名空间 Pod：kubectl get pods
(2) 查看所有命名空间 Pod：kubectl get pods -A
(3) 查看 Deployment：kubectl get deployments
(4) 查看 Pod 日志：kubectl logs -f pod-name
(5) 通过 yaml 创建资源：kubectl apply -f deployment.yaml
(6) 进入 Pod 容器：kubectl exec -it pod-name -- /bin/bash
(7) 扩容 Deployment 副本：kubectl scale deployment my-deploy --replicas=3
(8) 本地端口转发：kubectl port-forward pod/pod-name 8080:80
⚠️注意事项：需配置 kubectl 上下文（~/.kube/config）；未指定命名空间默认操作 default；多容器 Pod 查看日志需指定容器名
 
### 1.8.✅ CentOS 服务器维护（系统状态/软件管理/用户权限/日志监控/防火墙）
#### 系统状态监控
(1) 查看系统负载（1/5/15分钟平均负载）：uptime
(2) 查看CPU使用情况：top（实时）/ mpstat（核心详情）
(3) 查看内存使用情况：free -h（人类可读格式）
(4) 查看磁盘空间：df -h
(5) 查看磁盘IO情况：iostat -x 1（1秒刷新一次）
(6) 查看网络连接状态：netstat -tulnp / ss -tulnp
(7) 查看进程资源占用：ps -ef | grep 进程名 / ps aux --sort=-%cpu
#### 软件包管理（yum/dnf）
(1) 搜索软件包：yum search nginx
(2) 安装软件包：yum install -y nginx（-y 自动确认）
(3) 升级软件包：yum update -y nginx
(4) 卸载软件包：yum remove -y nginx
(5) 查看已安装软件：yum list installed | grep nginx
(6) 清理yum缓存：yum clean all
(7) 查看软件包信息：yum info nginx
(8) 安装本地rpm包：rpm -ivh xxx.rpm
(9) 卸载rpm包：rpm -e xxx.rpm
#### 用户与权限管理
(1) 创建用户：useradd testuser
(2) 设置用户密码：passwd testuser
(3) 删除用户：userdel -r testuser（-r 同时删除家目录）
(4) 切换用户：su - testuser
(5) 给用户授权sudo：usermod -aG wheel testuser
(6) 修改文件权限（读/写/执行：r=4/w=2/x=1）：chmod 755 test.sh
(7) 修改文件所有者：chown testuser:testuser test.txt
(8) 修改目录及子文件权限：chmod -R 777 /data
(9) 查看文件权限：ls -l test.txt
#### 日志监控与管理
(1) 实时查看日志：tail -f /var/log/messages
(2) 查看日志最后100行：tail -n 100 /var/log/nginx/access.log
(3) 搜索日志中关键字：grep 'ERROR' /var/log/java/app.log
(4) 按时间筛选日志（结合awk）：grep '2025-11-17' /var/log/syslog
(5) 轮转日志（避免日志过大）：logrotate /etc/logrotate.conf
(6) 查看系统登录日志：last / lastb
#### 防火墙管理（firewalld）
(1) 查看防火墙状态：systemctl status firewalld
(2) 启动防火墙：systemctl start firewalld
(3) 停止防火墙：systemctl stop firewalld
(4) 设置防火墙开机自启：systemctl enable firewalld
(5) 关闭防火墙开机自启：systemctl disable firewalld
(6) 开放端口（永久生效）：firewall-cmd --permanent --add-port=8080/tcp
(7) 关闭端口（永久生效）：firewall-cmd --permanent --remove-port=8080/tcp
(8) 重新加载防火墙规则：firewall-cmd --reload
(9) 查看开放端口：firewall-cmd --permanent --list-ports
#### 服务管理（systemctl）
(1) 查看服务状态：systemctl status nginx
(2) 启动服务：systemctl start nginx
(3) 停止服务：systemctl stop nginx
(4) 重启服务：systemctl restart nginx
(5) 重新加载配置（不重启）：systemctl reload nginx
(6) 设置服务开机自启：systemctl enable nginx
(7) 关闭服务开机自启：systemctl disable nginx
(8) 查看开机自启服务：systemctl list-unit-files --type=service | grep enabled
#### 磁盘管理与挂载
(1) 查看磁盘分区：fdisk -l
(2) 格式化磁盘（ext4格式）：mkfs.ext4 /dev/sdb1
(3) 创建挂载目录：mkdir /data
(4) 临时挂载磁盘：mount /dev/sdb1 /data
(5) 永久挂载（重启生效）：echo '/dev/sdb1 /data ext4 defaults 0 0' >> /etc/fstab
(6) 查看挂载情况：mount / df -h
(7) 卸载磁盘：umount /data
#### 系统配置与优化
(1) 查看系统内核版本：uname -r
(2) 查看系统版本：cat /etc/redhat-release
(3) 关闭SELinux（临时）：setenforce 0
(4) 关闭SELinux（永久，需重启）：sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config
(5) 调整文件描述符限制（临时）：ulimit -n 65535
(6) 调整文件描述符限制（永久）：echo '* soft nofile 65535' >> /etc/security/limits.conf && echo '* hard nofile 65535' >> /etc/security/limits.conf
(7) 查看系统时间：date
(8) 同步系统时间（NTP）：yum install -y ntpdate && ntpdate ntp.aliyun.com
⚠️注意事项：
- 执行系统级操作（如修改/etc/fstab、关闭SELinux）前建议备份配置文件；
- yum安装软件时避免直接用yum update（可能升级系统内核导致兼容问题），需指定软件名；
- 开放防火墙端口后必须重新加载规则才生效；
- 永久挂载磁盘时需确保分区格式正确，错误配置可能导致系统无法启动；
- 调整文件描述符限制后需重新登录用户生效；
- 操作敏感服务（如sshd、firewalld）时，避免远程操作时误关服务导致断开连接；
- 日志文件过大时及时轮转或清理，避免占满磁盘空间。