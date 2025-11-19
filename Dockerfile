# 使用官方 Nginx 镜像
FROM nginx:alpine

# 删除 Nginx 默认的 public 文件夹内容
RUN rm -rf /usr/share/nginx/html/*

# 将本地构建好的静态文件复制到 Nginx 的 web 根目录
COPY build/html /usr/share/nginx/html/py-md

# 暴露 80 端口
EXPOSE 80

# Nginx 镜像会默认启动服务