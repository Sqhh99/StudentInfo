FROM python:3.11-alpine

WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple \
    DJANGO_SETTINGS_MODULE=StudentInfo.settings_docker

# 安装依赖（使用国内镜像）
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && \
    apk add --no-cache \
    mariadb-dev \
    build-base \
    netcat-openbsd \
    linux-headers \
    pcre-dev

# 复制并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建日志目录
RUN mkdir -p logs

# 确保脚本有执行权限
RUN echo '#!/bin/sh' > docker-entrypoint.tmp && \
    cat docker-entrypoint.sh >> docker-entrypoint.tmp && \
    mv docker-entrypoint.tmp docker-entrypoint.sh && \
    chmod +x docker-entrypoint.sh && \
    ls -la docker-entrypoint.sh

# 收集静态文件
RUN python manage.py collectstatic --noinput

# 使用启动脚本
ENTRYPOINT ["/bin/sh", "./docker-entrypoint.sh"] 