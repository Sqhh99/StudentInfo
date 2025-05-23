#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
学生信息系统一体化初始化脚本
此脚本集成所有初始化步骤，包括:
1. 创建必要目录
2. 创建默认头像和其他静态资源
3. 初始化院系、专业、课程和班级数据（更真实的数据）
4. 初始化学生数据（生成更合理的姓名和信息）
5. 初始化成绩数据（包含GPA计算和成绩分布）
6. 创建管理员和演示用户账号
"""
import os
import sys
import django
import random
import datetime
import json
import csv
import hashlib
import logging
from pathlib import Path
from faker import Faker
import numpy as np

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'init_data.log'), mode='w')
    ]
)
logger = logging.getLogger(__name__)

# 确保logs目录存在
os.makedirs('logs', exist_ok=True)

# 创建中文和英文的faker实例
fake_zh = Faker('zh_CN')
fake_en = Faker('en_US')

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentInfo.settings_docker')

# 初始化Django
logger.info("正在初始化Django...")
django.setup()

# 确保使用Docker环境中的数据库设置
from django.conf import settings
settings.DATABASES['default'].update({
    'HOST': os.environ.get('DJANGO_DB_HOST', 'db'),
    'PORT': os.environ.get('DJANGO_DB_PORT', '3306'),
    'NAME': os.environ.get('DJANGO_DB_NAME', 'studentinfo'),
    'USER': os.environ.get('DJANGO_DB_USER', 'root'),
    'PASSWORD': os.environ.get('DJANGO_DB_PASSWORD', 'password'),
})

logger.info("===== 学生信息系统数据初始化 =====")

# 导入模型
from students.models import Department, Course, Major, Class, Student, Score
# 导入用户模型
from django.contrib.auth import get_user_model
User = get_user_model()

# ---- 0. 清除已有数据 ----
logger.info("[0/6] 清除已有数据...")
try:
    # 先清除关联数据
    logger.info("  清除成绩数据...")
    Score.objects.all().delete()
    
    logger.info("  清除学生数据...")
    Student.objects.all().delete()
    
    logger.info("  清除班级数据...")
    Class.objects.all().delete()
    
    logger.info("  清除专业数据...")
    Major.objects.all().delete()
    
    logger.info("  清除课程数据...")
    Course.objects.all().delete()
    
    logger.info("  清除院系数据...")
    Department.objects.all().delete()
    
    logger.info("  清除非管理员用户...")
    # 保留管理员用户，删除其他用户
    User.objects.filter(is_superuser=False).delete()
    
    logger.info("✓ 数据清除完成")
except Exception as e:
    logger.error(f"✗ 清除数据失败: {str(e)}")

# ---- 1. 创建必要目录 ----
logger.info("[1/6] 创建必要目录...")
try:
    media_root = settings.MEDIA_ROOT
    avatars_dir = os.path.join(media_root, 'student_profiles')
    documents_dir = os.path.join(media_root, 'documents')
    course_materials_dir = os.path.join(media_root, 'course_materials')
    
    os.makedirs(media_root, exist_ok=True)
    os.makedirs(avatars_dir, exist_ok=True)
    os.makedirs(documents_dir, exist_ok=True)
    os.makedirs(course_materials_dir, exist_ok=True)
    
    logger.info("✓ 目录创建完成")
except Exception as e:
    logger.error(f"✗ 目录创建失败: {str(e)}")

# ---- 2. 创建默认头像 ----
logger.info("\n[2/6] 创建默认头像和静态资源...")
try:
    # 引入模型
    from django.core.files import File
    
    default_avatar_path = os.path.join(settings.MEDIA_ROOT, 'student_profiles', 'default.png')
    
    # 创建学生默认头像
    if os.path.exists(default_avatar_path):
        logger.info("✓ 学生默认头像文件已存在")
    else:
        # 创建一个漂亮的默认头像
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建200x200的浅蓝色头像
            img = Image.new('RGB', (200, 200), color=(240, 248, 255))
            draw = ImageDraw.Draw(img)
            
            # 绘制圆形背景
            draw.ellipse((20, 20, 180, 180), fill=(135, 206, 250))
            
            # 绘制简单人形轮廓
            draw.ellipse((60, 60, 140, 120), fill=(240, 248, 255))  # 头部
            draw.rectangle((85, 120, 115, 170), fill=(240, 248, 255))  # 身体
            
            # 保存图像
            img.save(default_avatar_path)
            logger.info(f"✓ 创建学生默认头像: {default_avatar_path}")
            
            # 为测试创建几个随机颜色的头像供测试使用
            colors = [
                (255, 182, 193),  # 浅粉色
                (173, 216, 230),  # 浅蓝色
                (152, 251, 152),  # 浅绿色
                (255, 222, 173),  # 浅橙色
                (221, 160, 221),  # 浅紫色
            ]
            
            for i, color in enumerate(colors, 1):
                test_avatar_path = os.path.join(settings.MEDIA_ROOT, 'student_profiles', f'test_avatar_{i}.png')
                img = Image.new('RGB', (200, 200), color=(245, 245, 245))
                draw = ImageDraw.Draw(img)
                
                # 绘制圆形背景
                draw.ellipse((20, 20, 180, 180), fill=color)
                
                # 绘制更真实的人物轮廓
                draw.ellipse((70, 50, 130, 110), fill=(245, 245, 245))  # 头部
                
                # 随机添加不同的身体形状
                if i % 3 == 0:
                    # 绘制一个梯形身体
                    draw.polygon([(85, 110), (115, 110), (125, 170), (75, 170)], fill=(245, 245, 245))
                else:
                    draw.rectangle((85, 110, 115, 170), fill=(245, 245, 245))  # 普通身体
                
                img.save(test_avatar_path)
                logger.info(f"✓ 创建测试头像 {i}: {test_avatar_path}")
                
        except ImportError as e:
            logger.warning(f"PIL库不可用: {str(e)}，将创建空头像文件")
            # 如果没有PIL，创建空文件
            with open(default_avatar_path, 'w') as f:
                f.write('')
            logger.info("✓ 创建了空的默认头像文件")
except Exception as e:
    logger.error(f"✗ 创建默认头像失败: {str(e)}")

# ---- 3. 初始化院系和课程数据 ----
logger.info("\n[3/6] 初始化院系和课程数据...")
try:
    # 初始化院系数据
    logger.info("  创建院系...")
    departments_data = [
        {'name': '计算机科学与技术学院', 'code': 'CS', 'description': '计算机科学与技术、软件工程、人工智能、网络空间安全等专业'},
        {'name': '电子信息工程学院', 'code': 'EE', 'description': '电子工程、通信工程、微电子科学与工程、光电信息科学与工程等专业'},
        {'name': '经济管理学院', 'code': 'EM', 'description': '经济学、工商管理、市场营销、财务管理、会计学等专业'},
        {'name': '外国语学院', 'code': 'FL', 'description': '英语、日语、法语、德语、西班牙语、翻译等专业'},
        {'name': '数学与统计学院', 'code': 'MATH', 'description': '数学与应用数学、信息与计算科学、统计学、数据科学与大数据技术等专业'},
        {'name': '物理与材料科学学院', 'code': 'PHY', 'description': '物理学、应用物理学、材料科学与工程、新能源材料与器件等专业'},
        {'name': '生命科学学院', 'code': 'BIO', 'description': '生物科学、生物技术、生态学、生物信息学等专业'},
        {'name': '人文学院', 'code': 'LIB', 'description': '汉语言文学、历史学、哲学、文化产业管理等专业'},
    ]
    
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults={
                'name': dept_data['name'],
                'description': dept_data['description'],
            }
        )
        if created:
            logger.info(f"    + 创建院系: {dept.name}")
        else:
            logger.info(f"    · 院系已存在: {dept.name}")
    
    # 创建专业数据
    logger.info("\n  创建专业...")
    majors_data = [
        # 计算机学院
        {'name': '计算机科学与技术', 'code': 'CS', 'description': '培养具备计算机系统基础理论和专门知识，能从事计算机系统设计、开发及应用的高级技术人才。'},
        {'name': '软件工程', 'code': 'SE', 'description': '培养具备软件开发方法和技术，能从事大型软件系统分析、设计、实现和维护的专业人才。'},
        {'name': '网络工程', 'code': 'NE', 'description': '培养具备计算机网络理论和工程技术，能从事网络系统建设与管理的专业人才。'},
        {'name': '人工智能', 'code': 'AI', 'description': '培养具备人工智能理论和算法，能从事智能系统开发和应用的创新型人才。'},
        {'name': '数据科学与大数据技术', 'code': 'DS', 'description': '培养具备数据分析和处理能力，能从事大数据系统开发和应用的复合型人才。'},
        
        # 电子学院
        {'name': '电子信息工程', 'code': 'EIE', 'description': '培养具备电子技术和信息系统知识，能从事电子设备和信息系统设计的专业人才。'},
        {'name': '通信工程', 'code': 'CE', 'description': '培养具备现代通信理论和技术，能从事通信系统设计和开发的专业人才。'},
        {'name': '微电子科学与工程', 'code': 'MESE', 'description': '培养具备微电子器件和集成电路知识，能从事芯片设计和制造的专业人才。'},
        
        # 经管学院
        {'name': '经济学', 'code': 'ECON', 'description': '培养具备经济学理论和政策分析能力，能从事经济分析和决策的专业人才。'},
        {'name': '工商管理', 'code': 'BM', 'description': '培养具备现代管理理论和方法，能从事企业管理和决策的专业人才。'},
        {'name': '会计学', 'code': 'ACCT', 'description': '培养具备会计理论和实务，能从事财务会计和审计工作的专业人才。'},
        
        # 外语学院
        {'name': '英语', 'code': 'ENG', 'description': '培养具备扎实的英语语言基础和广泛的文化知识，能从事翻译、教育等工作的专业人才。'},
        {'name': '日语', 'code': 'JAP', 'description': '培养具备扎实的日语语言基础和日本文化知识，能从事翻译、贸易等工作的专业人才。'},
        
        # 数学院
        {'name': '数学与应用数学', 'code': 'MATH', 'description': '培养具备扎实的数学基础和应用能力，能从事科学研究和技术应用的专业人才。'},
        {'name': '统计学', 'code': 'STAT', 'description': '培养具备统计理论和方法，能从事数据分析和统计工作的专业人才。'},
    ]
    
    # 创建专业
    for major_data in majors_data:
        major, created = Major.objects.get_or_create(
            code=major_data['code'],
            defaults={
                'name': major_data['name'],
                'description': major_data['description'],
            }
        )
        
        if created:
            logger.info(f"    + 创建专业: {major.name}")
        else:
            logger.info(f"    · 专业已存在: {major.name}")
    
    # 创建班级数据
    logger.info("\n  创建班级...")
    classes_data = [
        # 计算机科学与技术专业班级
        {'name': '计科2021级1班', 'code': 'CS2021-1', 'major': 'CS', 'admission_year': 2021},
        {'name': '计科2021级2班', 'code': 'CS2021-2', 'major': 'CS', 'admission_year': 2021},
        {'name': '计科2022级1班', 'code': 'CS2022-1', 'major': 'CS', 'admission_year': 2022},
        {'name': '计科2022级2班', 'code': 'CS2022-2', 'major': 'CS', 'admission_year': 2022},
        {'name': '计科2023级1班', 'code': 'CS2023-1', 'major': 'CS', 'admission_year': 2023},
        
        # 软件工程专业班级
        {'name': '软工2021级1班', 'code': 'SE2021-1', 'major': 'SE', 'admission_year': 2021},
        {'name': '软工2022级1班', 'code': 'SE2022-1', 'major': 'SE', 'admission_year': 2022},
        {'name': '软工2023级1班', 'code': 'SE2023-1', 'major': 'SE', 'admission_year': 2023},
        
        # 人工智能专业班级
        {'name': '人工智能2022级1班', 'code': 'AI2022-1', 'major': 'AI', 'admission_year': 2022},
        {'name': '人工智能2023级1班', 'code': 'AI2023-1', 'major': 'AI', 'admission_year': 2023},
        
        # 电子信息工程专业班级
        {'name': '电信2021级1班', 'code': 'EIE2021-1', 'major': 'EIE', 'admission_year': 2021},
        {'name': '电信2022级1班', 'code': 'EIE2022-1', 'major': 'EIE', 'admission_year': 2022},
        
        # 经济学专业班级
        {'name': '经济2021级1班', 'code': 'ECON2021-1', 'major': 'ECON', 'admission_year': 2021},
        {'name': '经济2022级1班', 'code': 'ECON2022-1', 'major': 'ECON', 'admission_year': 2022},
        
        # 英语专业班级
        {'name': '英语2021级1班', 'code': 'ENG2021-1', 'major': 'ENG', 'admission_year': 2021},
        {'name': '英语2022级1班', 'code': 'ENG2022-1', 'major': 'ENG', 'admission_year': 2022},
    ]
    
    # 创建专业代码到对象的映射
    major_map = {major.code: major for major in Major.objects.all()}
    
    # 创建班级
    for class_data in classes_data:
        # 获取对应的专业对象
        major_code = class_data.pop('major')
        major = major_map.get(major_code)
        
        if not major:
            logger.warning(f"找不到专业代码 {major_code}，跳过创建班级 {class_data['name']}")
            continue
        
        class_obj, created = Class.objects.get_or_create(
            code=class_data['code'],
            defaults={
                **class_data,
                'major': major
            }
        )
        
        if created:
            logger.info(f"    + 创建班级: {class_obj.name} (专业: {major.name})")
        else:
            logger.info(f"    · 班级已存在: {class_obj.name}")
    
    # 初始化课程数据
    logger.info("\n  创建课程...")
    
    # 重新创建院系代码到对象的映射
    dept_map = {dept.code: dept for dept in Department.objects.all()}
    
    # 定义学期数据
    current_year = datetime.datetime.now().year
    semesters = [
        f"{current_year-1}-{current_year}-1",  # 上一学年第一学期
        f"{current_year-1}-{current_year}-2",  # 上一学年第二学期
        f"{current_year}-{current_year+1}-1",  # 当前学年第一学期
    ]
    
    courses_data = [
        # 公共基础课
        {
            'code': 'PUB101', 
            'name': '高等数学(上)', 
            'credit': 5.0,
            'teacher': '李数学',
            'description': '微积分、极限、导数、定积分等基础数学知识，为各专业学生打下扎实的数学基础。',
            'department': 'MATH',
            'class_time': '周一 1-2节, 周三 3-4节',
            'location': '教学楼A-101',
            'capacity': 120,
            'semester': semesters[0],
            'status': 'completed'
        },
        {
            'code': 'PUB102', 
            'name': '高等数学(下)', 
            'credit': 4.0,
            'teacher': '李数学',
            'description': '多元函数微积分、级数、常微分方程等高等数学知识，为专业课学习提供数学工具。',
            'department': 'MATH',
            'class_time': '周二 1-2节, 周四 3-4节',
            'location': '教学楼A-102',
            'capacity': 120,
            'semester': semesters[1],
            'status': 'completed'
        },
        {
            'code': 'PUB103', 
            'name': '线性代数', 
            'credit': 3.0,
            'teacher': '王矩阵',
            'description': '线性空间、线性变换、矩阵理论等内容，培养学生的抽象思维和逻辑推理能力。',
            'department': 'MATH',
            'class_time': '周二 5-7节',
            'location': '教学楼B-201',
            'capacity': 100,
            'semester': semesters[0],
            'status': 'completed'
        },
        {
            'code': 'PUB104', 
            'name': '大学物理(上)', 
            'credit': 4.0,
            'teacher': '张物理',
            'description': '力学、热学等物理基础知识，通过理论教学和实验相结合的方式进行。',
            'department': 'PHY',
            'class_time': '周三 1-2节, 周五 3-4节',
            'location': '物理楼A-301',
            'capacity': 100,
            'semester': semesters[0],
            'status': 'completed'
        },
        {
            'code': 'PUB105', 
            'name': '大学物理(下)', 
            'credit': 4.0,
            'teacher': '张物理',
            'description': '电磁学、光学和近代物理等内容，培养学生的科学思维和实验能力。',
            'department': 'PHY',
            'class_time': '周一 5-6节, 周四 7-8节',
            'location': '物理楼A-302',
            'capacity': 100,
            'semester': semesters[1],
            'status': 'completed'
        },
        {
            'code': 'PUB106', 
            'name': '大学英语(1)', 
            'credit': 3.0,
            'teacher': '刘英语',
            'description': '基础英语听说读写训练，提高学生的英语综合应用能力。',
            'department': 'FL',
            'class_time': '周一 3-4节, 周三 5-6节',
            'location': '外语楼102',
            'capacity': 60,
            'semester': semesters[0],
            'status': 'completed'
        },
        
        # 计算机专业课程
        {
            'code': 'CS101', 
            'name': '计算机程序设计基础(C语言)', 
            'credit': 4.0,
            'teacher': '周程序',
            'description': '介绍C语言基础知识和程序设计方法，培养学生的编程思维和解决问题的能力。',
            'department': 'CS',
            'class_time': '周一 7-8节, 周四 5-6节',
            'location': '计算机楼A-101',
            'capacity': 80,
            'semester': semesters[0],
            'status': 'completed'
        },
        {
            'code': 'CS201', 
            'name': '数据结构与算法', 
            'credit': 4.0,
            'teacher': '李数据',
            'description': '学习基本数据结构（如数组、链表、栈、队列、树、图等）和算法设计与分析方法。',
            'department': 'CS',
            'class_time': '周二 3-5节',
            'location': '计算机楼B-202',
            'capacity': 70,
            'semester': semesters[1],
            'status': 'completed'
        },
        {
            'code': 'CS301', 
            'name': '操作系统原理', 
            'credit': 3.5,
            'teacher': '王操作',
            'description': '操作系统的基本概念、原理和实现技术，包括进程管理、内存管理、文件系统和I/O管理等。',
            'department': 'CS',
            'class_time': '周三 6-8节',
            'location': '计算机楼C-303',
            'capacity': 60,
            'semester': semesters[2],
            'status': 'active'
        },
        {
            'code': 'CS302', 
            'name': '计算机组成原理', 
            'credit': 4.0,
            'teacher': '黄硬件',
            'description': '计算机硬件系统的组成、结构和工作原理，包括CPU、存储器、I/O系统等。',
            'department': 'CS',
            'class_time': '周二 1-3节',
            'location': '计算机楼B-201',
            'capacity': 65,
            'semester': semesters[2],
            'status': 'active'
        },
        {
            'code': 'CS401', 
            'name': '数据库系统', 
            'credit': 3.0,
            'teacher': '刘数据',
            'description': '数据库系统原理、关系数据库设计理论和SQL语言，以及数据库管理系统的实现技术。',
            'department': 'CS',
            'class_time': '周四 3-5节',
            'location': '计算机楼B-203',
            'capacity': 70,
            'semester': semesters[2],
            'status': 'active'
        },
        {
            'code': 'CS501', 
            'name': '计算机网络', 
            'credit': 3.0,
            'teacher': '陈网络',
            'description': '计算机网络的基本概念、体系结构和协议，包括物理层、数据链路层、网络层、传输层和应用层等。',
            'department': 'CS',
            'class_time': '周五 1-3节',
            'location': '计算机楼C-304',
            'capacity': 65,
            'semester': semesters[2],
            'status': 'active'
        },
        {
            'code': 'CS601', 
            'name': '人工智能导论', 
            'credit': 3.0,
            'teacher': '钱智能',
            'description': '人工智能的基本概念、方法和应用，包括搜索、知识表示、机器学习、神经网络等内容。',
            'department': 'CS',
            'class_time': '周一 5-7节',
            'location': '计算机楼A-201',
            'capacity': 50,
            'semester': semesters[2],
            'status': 'active'
        },
        {
            'code': 'CS602', 
            'name': '编译原理', 
            'credit': 3.5,
            'teacher': '马编译',
            'description': '程序语言编译器的设计与实现，包括词法分析、语法分析、语义分析、中间代码生成和优化等。',
            'department': 'CS',
            'class_time': '周三 1-3节',
            'location': '计算机楼A-202',
            'capacity': 45,
            'semester': semesters[2],
            'status': 'active'
        },
        
        # 软件工程专业课程
        {
            'code': 'SE301', 
            'name': '软件工程导论', 
            'credit': 3.0,
            'teacher': '张软件',
            'description': '软件工程的基本概念、方法和技术，包括软件过程、需求分析、设计、测试和维护等。',
            'department': 'CS',
            'class_time': '周二 6-8节',
            'location': '计算机楼C-301',
            'capacity': 60,
            'semester': semesters[1],
            'status': 'completed'
        },
        {
            'code': 'SE401', 
            'name': '软件设计与架构', 
            'credit': 3.0,
            'teacher': '李架构',
            'description': '软件设计原则、模式和架构风格，培养学生的软件系统设计能力。',
            'department': 'CS',
            'class_time': '周四 1-3节',
            'location': '计算机楼C-302',
            'capacity': 55,
            'semester': semesters[2],
            'status': 'active'
        },
        
        # 电子信息工程专业课程
        {
            'code': 'EE101', 
            'name': '电路分析基础', 
            'credit': 4.0,
            'teacher': '赵电路',
            'description': '电路的基本理论和分析方法，包括直流电路、交流电路、暂态分析等内容。',
            'department': 'EE',
            'class_time': '周一 6-8节',
            'location': '电子楼201',
            'capacity': 90,
            'semester': semesters[0],
            'status': 'completed'
        },
        {
            'code': 'EE201', 
            'name': '模拟电子技术', 
            'credit': 3.5,
            'teacher': '钱电子',
            'description': '模拟电子线路的基本原理和设计方法，包括半导体器件、放大器、运算放大器等。',
            'department': 'EE',
            'class_time': '周二 1-3节',
            'location': '电子楼302',
            'capacity': 85,
            'semester': semesters[1],
            'status': 'completed'
        },
        {
            'code': 'EE301', 
            'name': '数字电路与逻辑设计', 
            'credit': 3.5,
            'teacher': '孙数字',
            'description': '数字电路的基本原理和设计方法，包括逻辑门、组合逻辑电路、时序逻辑电路等。',
            'department': 'EE',
            'class_time': '周三 3-5节',
            'location': '电子楼103',
            'capacity': 75,
            'semester': semesters[2],
            'status': 'active'
        },
    ]
    
    # 创建课程
    for course_data in courses_data:
        # 获取对应的院系对象
        dept_code = course_data.pop('department')
        department = dept_map.get(dept_code)
        
        if not department:
            logger.warning(f"找不到院系代码 {dept_code}，跳过创建课程 {course_data['name']}")
            continue
        
        course, created = Course.objects.get_or_create(
            code=course_data['code'],
            defaults={
                **course_data,
                'department': department
            }
        )
        
        if created:
            logger.info(f"    + 创建课程: {course.name} (院系: {department.name})")
        else:
            logger.info(f"    · 课程已存在: {course.name}")
    
    logger.info("✓ 院系和课程数据初始化完成")    
except Exception as e:
    logger.error(f"✗ 初始化院系和课程数据失败: {str(e)}")

# ---- 4. 初始化学生数据 ----
logger.info("\n[4/6] 初始化学生数据...")
try:
    # 创建学生数据
    logger.info("  创建学生...")
    
    # 获取班级信息用于分配学生
    class_map = {class_obj.code: class_obj for class_obj in Class.objects.all()}
    major_map = {major.code: major for major in Major.objects.all()}
    
    # 确保至少有一个班级可用
    if not class_map:
        logger.warning("没有可用的班级，无法创建学生数据")
    else:
        # 为不同班级创建学生
        for class_code, class_obj in class_map.items():
            # 从班级代码中获取专业代码(如CS2021-1中的CS)
            major_code = class_obj.major.code
            major = major_map.get(major_code)
            
            # 确定该班级需要创建的学生数量(模拟班级规模不一)
            student_count = random.randint(30, 40)  # 每个班级30-40名学生
            
            for i in range(1, student_count + 1):
                # 生成唯一学号 (年份+专业代码+序号)
                # 例如: 202101001 表示2021级CS专业第1班第001号学生
                student_id_prefix = f"{class_obj.admission_year}{i:03d}"
                student_id = f"{student_id_prefix}{i:03d}"
                
                # 随机生成学生姓名
                name = fake_zh.name()
                
                # 随机性别
                gender = random.choice(['male', 'female'])
                
                # 入学日期(根据班级入学年份)
                admission_year = class_obj.admission_year
                admission_date = f"{admission_year}-09-01"  # 9月1日入学
                
                # 创建学生
                student, created = Student.objects.get_or_create(
                    student_id=student_id,
                    defaults={
                        'name': name,
                        'gender': gender,
                        'class_obj': class_obj,
                        'major': major,
                        'admission_date': admission_date,
                        'phone': fake_zh.phone_number(),
                        'email': fake_en.email(),
                        'status': 'active',
                    }
                )
                
                if created:
                    logger.info(f"    + 创建学生: {student.name} (学号: {student.student_id}, 班级: {class_obj.name})")
                else:
                    logger.info(f"    · 学生已存在: {student.name}")
        
        logger.info(f"✓ 成功创建学生数据，共 {Student.objects.count()} 名学生")
except Exception as e:
    logger.error(f"✗ 初始化学生数据失败: {str(e)}")

# ---- 5. 初始化成绩数据 ----
logger.info("\n[5/6] 初始化成绩数据...")
try:
    # 获取所有学生和课程
    students = Student.objects.all()
    courses = Course.objects.all()
    
    # 检查是否有学生和课程数据
    if not students:
        logger.warning("没有学生数据，无法创建成绩")
    elif not courses:
        logger.warning("没有课程数据，无法创建成绩")
    else:
        logger.info("  创建成绩...")
        # 学期列表
        semesters = [
            f"{datetime.datetime.now().year-1}-{datetime.datetime.now().year}-1",  # 上一学年第一学期
            f"{datetime.datetime.now().year-1}-{datetime.datetime.now().year}-2",  # 上一学年第二学期
        ]
        
        # 为每个学生创建成绩
        count = 0
        for student in students:
            # 只为已结课的课程生成成绩
            completed_courses = Course.objects.filter(status='completed')
            
            # 确保有已结课的课程
            if not completed_courses:
                logger.warning(f"没有已结课的课程，学生 {student.name} 无法创建成绩")
                continue
                
            # 为每个学生随机选择3-6门已完成的课程
            num_courses = min(random.randint(3, 6), completed_courses.count())
            selected_courses = random.sample(list(completed_courses), num_courses)
            
            for course in selected_courses:
                # 随机选择学期
                semester = random.choice(semesters)
                
                # 生成随机分数 (正态分布，平均75分，标准差10)
                score_value = round(max(0, min(100, np.random.normal(75, 10))), 1)
                
                # 创建成绩记录
                score, created = Score.objects.get_or_create(
                    student=student,
                    course=course,
                    semester=semester,
                    defaults={
                        'score': score_value,
                    }
                )
                
                if created:
                    count += 1
                    # 只打印部分日志，避免过多输出
                    if count <= 10 or count % 50 == 0:
                        logger.info(f"    + 创建成绩: {student.name} - {course.name}: {score.score} ({semester})")
        
        logger.info(f"✓ 成功创建成绩数据，共 {count} 条成绩记录")
except Exception as e:
    logger.error(f"✗ 初始化成绩数据失败: {str(e)}")

# ---- 6. 创建管理员和演示用户账号 ----
logger.info("\n[6/6] 创建管理员和演示用户账号...")
try:
    # 创建管理员账号
    logger.info("  创建管理员账号...")
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_superuser': True,
            'password': 'admin',
        }
    )
    if created:
        logger.info(f"    + 创建管理员账号: {admin_user.username}")
    else:
        logger.info(f"    · 管理员账号已存在: {admin_user.username}")
    
    # 创建演示用户账号
    logger.info("\n  创建演示用户账号...")
    demo_user, created = User.objects.get_or_create(
        username='demo',
        defaults={
            'is_superuser': False,
            'password': 'demo',
        }
    )
    if created:
        logger.info(f"    + 创建演示用户账号: {demo_user.username}")
    else:
        logger.info(f"    · 演示用户账号已存在: {demo_user.username}")
except Exception as e:
    logger.error(f"✗ 创建管理员和演示用户账号失败: {str(e)}")

logger.info("✓ 所有数据初始化完成") 