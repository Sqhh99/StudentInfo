#!/bin/sh

# 等待MySQL启动
echo "等待MySQL服务启动..."
for i in $(seq 1 30); do
    if nc -z $DJANGO_DB_HOST 3306; then
        echo "MySQL服务已就绪"
        break
    fi
    echo "尝试连接MySQL ($i/30)..."
    sleep 2
done

# 创建必要目录
mkdir -p logs staticfiles media

# 复制Docker环境设置文件
cp StudentInfo/settings_docker.py StudentInfo/settings_local.py

# 执行数据库迁移
echo "正在执行数据库迁移..."
python manage.py migrate --settings=StudentInfo.settings_docker

# 载入初始数据
echo "检查是否需要载入初始数据..."
# 检查数据库中是否已有数据
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentInfo.settings_docker')
django.setup()
from django.db import connection
cursor = connection.cursor()
try:
    cursor.execute('SELECT COUNT(*) FROM users_user')
    count = cursor.fetchone()[0]
    exit(0 if count > 0 else 1)
except:
    exit(1)
"

# 如果没有数据，运行初始化脚本
if [ $? -ne 0 ]; then
    echo "正在载入初始数据..."
    
    # 使用init_all.py进行一体化初始化
    if [ -f init_all.py ]; then
        echo "执行一体化初始化脚本..."
        python init_all.py --settings=StudentInfo.settings_docker
    else
        echo "init_all.py不存在，尝试使用分步初始化..."
        
        # 创建默认头像
        if [ -f create_default_avatar.py ]; then
            echo "创建默认头像..."
            python create_default_avatar.py --settings=StudentInfo.settings_docker
        fi

        # 初始化院系和课程数据
        if [ -f init_departments_courses.py ]; then
            echo "初始化院系和课程数据..."
            python init_departments_courses.py --settings=StudentInfo.settings_docker
        fi

        # 初始化成绩数据
        if [ -f init_scores.py ]; then
            echo "初始化成绩数据..."
            python init_scores.py --settings=StudentInfo.settings_docker
        fi
    fi

    # 创建超级管理员账号
    echo "创建超级管理员账号..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell --settings=StudentInfo.settings_docker
    
    echo "初始数据载入完成"
else
    echo "数据库已有数据，跳过初始化"
fi

# 收集静态文件
echo "正在收集静态文件..."
python manage.py collectstatic --noinput --settings=StudentInfo.settings_docker

# 使用命令行参数执行命令
echo "准备运行应用..."
exec "$@" 
