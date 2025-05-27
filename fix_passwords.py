#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentInfo.settings')
django.setup()

from students.models import Student

print("修复所有学生的密码...")
students = Student.objects.all()

for student in students:
    print(f"为学生 {student.name} (学号: {student.student_id}) 设置密码...")
    student.set_password(student.student_id)
    student.save()

print(f"完成！已为 {students.count()} 个学生设置密码")

# 验证第一个学生的密码
test_student = Student.objects.get(student_id='20200001')
print(f"\n验证学号 20200001 的密码: {test_student.check_password('20200001')}")
print(f"密码哈希: {test_student.password[:50]}...")
