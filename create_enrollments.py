#!/usr/bin/env python
import os
import sys
import django
import random
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentInfo.settings')
django.setup()

from students.models import Student, Course, Score
from student_portal.models import Enrollment

def create_sample_enrollments():
    """为学生创建示例选课数据"""
    print("开始创建选课数据...")
    
    students = Student.objects.all()
    courses = Course.objects.filter(status='active')
    current_semester = "2025-1"
    
    enrollments_created = 0
    
    for student in students:
        # 为每个学生随机选择3-6门课程
        num_courses = random.randint(3, 6)
        selected_courses = random.sample(list(courses), min(num_courses, len(courses)))
        
        for course in selected_courses:
            # 检查是否已经有选课记录
            existing_enrollment = Enrollment.objects.filter(
                student=student,
                course=course,
                semester=current_semester
            ).first()
            
            if not existing_enrollment:
                Enrollment.objects.create(
                    student=student,
                    course=course,
                    semester=current_semester,
                    status='enrolled'
                )
                enrollments_created += 1
    
    print(f"选课数据创建完成！共创建了 {enrollments_created} 条选课记录")
    
    # 验证创建的数据
    total_enrollments = Enrollment.objects.count()
    print(f"数据库中现有选课记录总数: {total_enrollments}")
    
    # 显示第一个学生的选课情况
    first_student = Student.objects.first()
    if first_student:
        student_enrollments = Enrollment.objects.filter(
            student=first_student,
            status='enrolled'
        )
        print(f"\n学生 {first_student.name} 的选课情况:")
        for enrollment in student_enrollments:
            print(f"  - {enrollment.course.name} ({enrollment.semester})")

if __name__ == '__main__':
    create_sample_enrollments()
