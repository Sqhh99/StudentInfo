import os
import sys
import django
import datetime

# 将当前目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentInfo.settings')
django.setup()

from students.models import Department, Course, Class, Major

def init_departments():
    """初始化院系数据"""
    departments_data = [
        {'name': '计算机科学与技术学院', 'code': 'CS', 'description': '计算机科学与技术、软件工程、网络工程等专业'},
        {'name': '数学与统计学院', 'code': 'MATH', 'description': '数学、统计学、应用数学等专业'},
        {'name': '物理与电子工程学院', 'code': 'PHY', 'description': '物理学、电子工程、光电子技术等专业'},
        {'name': '外国语学院', 'code': 'LANG', 'description': '英语、日语、法语等语言专业'},
        {'name': '经济管理学院', 'code': 'ECON', 'description': '经济学、工商管理、市场营销等专业'},
    ]
    
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults={
                'name': dept_data['name'],
                'description': dept_data['description']
            }
        )
        if created:
            print(f"创建院系: {dept.name}")
        else:
            print(f"院系已存在: {dept.name}")
    
    return Department.objects.all()

def init_courses(departments):
    """初始化课程数据"""
    courses_data = [
        {
            'code': 'CS101', 
            'name': '计算机导论', 
            'credit': 3.0,
            'teacher': '张教授',
            'description': '本课程是计算机科学的入门课程，介绍计算机的基本概念、原理和应用，培养学生的计算思维和解决问题的能力。',
            'department': 'CS',
            'class_time': '周一 1-2节',
            'location': '教学楼A-101',
            'capacity': 120,
            'semester': '2025-1',
            'status': 'active'
        },
        {
            'code': 'CS201', 
            'name': '数据结构与算法', 
            'credit': 4.0,
            'teacher': '李教授',
            'description': '学习常见数据结构和算法，包括数组、链表、栈、队列、树、图等数据结构，以及排序、搜索等算法。',
            'department': 'CS',
            'class_time': '周二 3-5节',
            'location': '教学楼B-202',
            'capacity': 80,
            'semester': '2025-1',
            'status': 'active'
        },
        {
            'code': 'MATH201', 
            'name': '高等数学', 
            'credit': 5.0,
            'teacher': '王教授',
            'description': '微积分、级数、微分方程等数学基础知识，为学生后续专业课程打下坚实数学基础。',
            'department': 'MATH',
            'class_time': '周三 1-4节',
            'location': '教学楼C-301',
            'capacity': 150,
            'semester': '2025-1',
            'status': 'active'
        },
        {
            'code': 'PHY102', 
            'name': '大学物理', 
            'credit': 4.0,
            'teacher': '赵教授',
            'description': '力学、热学、电磁学、光学和近代物理等基础知识，通过实验和理论教学相结合的方式进行。',
            'department': 'PHY',
            'class_time': '周四 6-8节',
            'location': '物理实验楼A-102',
            'capacity': 100,
            'semester': '2025-1',
            'status': 'active'
        },
        {
            'code': 'LANG101', 
            'name': '大学英语', 
            'credit': 3.0,
            'teacher': '陈教授',
            'description': '培养学生的英语听说读写能力，提高英语综合应用能力和跨文化交际能力。',
            'department': 'LANG',
            'class_time': '周五 1-2节',
            'location': '外语楼102',
            'capacity': 60,
            'semester': '2025-1',
            'status': 'active'
        },
        {
            'code': 'ECON202', 
            'name': '微观经济学', 
            'credit': 3.0,
            'teacher': '钱教授',
            'description': '研究个体经济单位的经济行为和决策，包括消费者行为、生产者行为、市场结构等内容。',
            'department': 'ECON',
            'class_time': '周二 6-8节',
            'location': '经管楼305',
            'capacity': 90,
            'semester': '2025-1',
            'status': 'pending'
        },
        {
            'code': 'CS301', 
            'name': '数据库系统', 
            'credit': 3.5,
            'teacher': '刘教授',
            'description': '学习数据库设计原理、关系模型、SQL语言、事务处理等数据库核心技术。',
            'department': 'CS',
            'class_time': '周三 6-8节',
            'location': '计算机楼202',
            'capacity': 75,
            'semester': '2024-2',
            'status': 'completed'
        },
        {
            'code': 'CS401', 
            'name': '人工智能', 
            'credit': 4.0,
            'teacher': '孙教授',
            'description': '介绍人工智能的基本概念、方法和应用，包括搜索算法、知识表示、机器学习、深度学习等内容。',
            'department': 'CS',
            'class_time': '周四 3-5节',
            'location': '计算机楼304',
            'capacity': 60,
            'semester': '2025-2',
            'status': 'pending'
        },
    ]
    
    # 创建院系代码到对象的映射
    dept_map = {dept.code: dept for dept in departments}
    
    created_courses = []
    for course_data in courses_data:
        # 获取对应的院系对象
        dept_code = course_data.pop('department')
        department = dept_map.get(dept_code)
        
        if not department:
            print(f"错误: 找不到院系代码 {dept_code}")
            continue
        
        course, created = Course.objects.get_or_create(
            code=course_data['code'],
            defaults={
                **course_data,
                'department': department
            }
        )
        
        if created:
            created_courses.append(course)
            print(f"创建课程: {course.name}")
        else:
            print(f"课程已存在: {course.name}")
    
    return created_courses

def init_classes():
    """初始化班级数据"""
    # 获取所有专业
    majors = Major.objects.all()
    if not majors.exists():
        print("没有找到专业数据，请先初始化专业数据")
        return []
    
    classes_data = [
        {
            'name': '计算机科学2023级1班',
            'code': 'CS2023-1',
            'major': 'CS',
            'admission_year': 2023
        },
        {
            'name': '计算机科学2023级2班',
            'code': 'CS2023-2',
            'major': 'CS',
            'admission_year': 2023
        },
        {
            'name': '电子工程2023级1班',
            'code': 'EE2023-1',
            'major': 'PHY',
            'admission_year': 2023
        },
        {
            'name': '经济管理2023级1班',
            'code': 'EM2023-1',
            'major': 'ECON',
            'admission_year': 2023
        },
        {
            'name': '外语2023级1班',
            'code': 'FL2023-1',
            'major': 'LANG',
            'admission_year': 2023
        }
    ]
    
    # 创建专业代码到对象的映射
    major_map = {major.code: major for major in majors}
    
    created_classes = []
    for class_data in classes_data:
        # 获取对应的专业对象
        major_code = class_data.pop('major')
        major = major_map.get(major_code)
        
        if not major:
            print(f"错误: 找不到专业代码 {major_code}")
            continue
        
        class_obj, created = Class.objects.get_or_create(
            code=class_data['code'],
            defaults={
                **class_data,
                'major': major
            }
        )
        
        if created:
            created_classes.append(class_obj)
            print(f"创建班级: {class_obj.name}")
        else:
            print(f"班级已存在: {class_obj.name}")
    
    return created_classes

if __name__ == '__main__':
    print("开始初始化院系数据...")
    departments = init_departments()
    print(f"院系数据初始化完成，共 {departments.count()} 个院系")
    
    print("\n开始初始化课程数据...")
    courses = init_courses(departments)
    print(f"课程数据初始化完成，共 {len(courses)} 门课程")
    
    print("\n开始初始化班级数据...")
    classes = init_classes()
    print(f"班级数据初始化完成，共 {len(classes)} 个班级") 