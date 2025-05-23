import os
import sys
import django
import datetime
import random

# 将当前目录添加到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentInfo.settings')
django.setup()

from students.models import Student, Course, Score

def init_scores():
    """初始化成绩数据"""
    # 获取所有学生和课程
    students = Student.objects.all()
    courses = Course.objects.all()
    
    # 定义学期
    semesters = ['2025-1', '2024-2', '2024-1']
    
    # 创建的成绩数
    score_count = 0
    
    # 为每个学生随机分配3-5门课程的成绩
    for student in students:
        # 随机选择3-5门课程
        student_courses = random.sample(list(courses), min(random.randint(3, 5), len(courses)))
        
        for course in student_courses:
            # 随机选择一个学期
            semester = random.choice(semesters)
            
            # 生成一个随机成绩 (60-100)
            score_value = round(random.uniform(60, 100), 1)
            
            # 生成一个随机评语
            comments = [
                f"{student.name}在{course.name}课程中表现优秀，理论知识掌握扎实，实践能力突出。",
                f"{student.name}在{course.name}课程中表现良好，能够灵活运用所学知识解决问题。",
                f"{student.name}在{course.name}课程中掌握了基本概念和方法，但需要进一步提高实践能力。",
                f"{student.name}在{course.name}课程的学习中付出了努力，建议加强基础知识的巩固。",
                f"{student.name}在{course.name}课程中能够完成基本任务，建议多进行课后练习。"
            ]
            comment = random.choice(comments)
            
            # 创建成绩记录
            score, created = Score.objects.get_or_create(
                student=student,
                course=course,
                semester=semester,
                defaults={
                    'score': score_value,
                    'comment': comment
                }
            )
            
            if created:
                score_count += 1
                print(f"创建成绩: {student.name} - {course.name}: {score.score} ({score.grade})")
            else:
                print(f"成绩已存在: {student.name} - {course.name}")
    
    return score_count

if __name__ == '__main__':
    print("开始初始化成绩数据...")
    score_count = init_scores()
    print(f"成绩数据初始化完成，共创建 {score_count} 条成绩记录")
    print(f"成绩总数: {Score.objects.count()}") 