#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentInfo.settings')
django.setup()

from students.models import Student

# 检查学生数据
print("检查学生数据...")
students = Student.objects.all()
print(f"总共有 {students.count()} 个学生")

# 检查学号为20200001的学生
try:
    student = Student.objects.get(student_id='20200001')
    print(f"\n找到学生: {student.name} (学号: {student.student_id})")
    print(f"密码字段内容: {student.password}")
    print(f"密码是否为空: {not student.password}")
    
    # 尝试验证密码
    if student.password:
        print(f"验证密码 '20200001': {student.check_password('20200001')}")
    else:
        print("密码为空，设置默认密码...")
        student.set_password('20200001')
        student.save()
        print("密码已设置为学号")
        print(f"重新验证密码 '20200001': {student.check_password('20200001')}")
        
except Student.DoesNotExist:
    print("学号 20200001 的学生不存在")

# 列出前5个学生
print("\n前5个学生:")
for student in students[:5]:
    print(f"- {student.name} (学号: {student.student_id}), 密码: {'已设置' if student.password else '未设置'}")