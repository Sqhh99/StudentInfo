#!/usr/bin/env python
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentInfo.settings')
django.setup()

from students.models import Student, Course, Score
from student_portal.models import StudentNotification, Enrollment

def check_data():
    print("=== 数据库数据检查 ===")
    print(f'学生总数: {Student.objects.count()}')
    print(f'课程总数: {Course.objects.count()}')
    print(f'成绩总数: {Score.objects.count()}')
    print(f'通知总数: {StudentNotification.objects.count()}')
    print(f'选课总数: {Enrollment.objects.count()}')
    
    # 检查第一个学生的数据
    student = Student.objects.first()
    if student:
        print(f'\n=== 第一个学生信息 ===')
        print(f'姓名: {student.name}')
        print(f'学号: {student.student_id}')
        print(f'专业: {student.major.name if student.major else "无"}')
        print(f'班级: {student.class_obj.name if student.class_obj else "无"}')
        
        # 检查该学生的成绩
        scores = Score.objects.filter(student=student)
        print(f'成绩数量: {scores.count()}')
        if scores.exists():
            print("前5个成绩:")
            for score in scores[:5]:
                print(f'  - {score.course.name}: {score.score}分')
        
        # 检查该学生的选课
        enrollments = Enrollment.objects.filter(student=student)
        print(f'选课数量: {enrollments.count()}')
        if enrollments.exists():
            print("选课情况:")
            for enrollment in enrollments[:5]:
                print(f'  - {enrollment.course.name} ({enrollment.status})')
                
        # 检查通知
        notifications = StudentNotification.objects.filter(
            student=student
        ) | StudentNotification.objects.filter(student__isnull=True)
        print(f'相关通知数量: {notifications.count()}')
        
    else:
        print('没有学生数据')

if __name__ == '__main__':
    check_data()
