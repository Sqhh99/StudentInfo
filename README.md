# 学生信息管理系统 (StudentInfo)

基于Django开发的学生信息管理系统，支持学生信息、班级和专业的管理。

## Docker部署指南

### 前置条件

- 安装 [Docker](https://docs.docker.com/get-docker/)
- 安装 [Docker Compose](https://docs.docker.com/compose/install/)

### 部署步骤

1. 克隆仓库到本地：

```bash
git clone <repository-url>
cd StudentInfo
```

2. 使用Docker Compose启动应用：

```bash
docker-compose up -d
```

这将会：
- 构建应用Docker镜像
- 启动MySQL数据库容器
- 启动Django应用容器
- 自动执行数据库迁移
- 收集静态文件

3. 访问应用：

应用将在 http://localhost:8000 上运行

### 初始化数据

如果需要导入初始数据，可以在容器内执行：

```bash
# 进入容器
docker exec -it studentinfo_web_1 bash

# 运行初始化脚本
python init_departments_courses.py
python create_default_avatar.py
```

### 自定义配置

可以在`docker-compose.yml`文件中修改环境变量来定制配置：

```yaml
environment:
  - DJANGO_DB_HOST=db
  - DJANGO_DB_PORT=3306
  - DJANGO_DB_NAME=studentinfo
  - DJANGO_DB_USER=root
  - DJANGO_DB_PASSWORD=password
```

### 停止和重启

停止应用：

```bash
docker-compose down
```

重启应用：

```bash
docker-compose restart
```

完全重建应用：

```bash
docker-compose down
docker-compose up -d --build
```

### 数据持久化

数据库数据存储在Docker卷中，重启容器不会丢失。静态文件和媒体文件通过卷挂载到容器中实现持久化。 