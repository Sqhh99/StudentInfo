#!/usr/bin/env python
"""
创建示例通知数据
"""
import os
import django
import sys
from django.utils import timezone
from datetime import datetime, timedelta

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentInfo.settings')
django.setup()

from students.models import Student
from student_portal.models import StudentNotification

def create_sample_notifications():
    """创建示例通知数据"""
    
    # 获取一些学生
    students = Student.objects.all()[:10]
    
    # 系统公告（面向所有学生）
    system_notifications = [
        {
            'title': '重要通知：期末考试安排已发布',
            'content': '各位同学请注意，2025年春季学期期末考试安排已经发布。请登录教务系统查看具体考试时间和地点。考试时间为6月15日-6月25日，请同学们合理安排复习时间。',
            'type': 'announcement',
            'priority': 'high',
            'sender': '教务处',
            'action_url': '/student/schedule/',
        },
        {
            'title': '学费缴费提醒',
            'content': '2025年秋季学期学费缴费工作已开始，请同学们在7月31日前完成缴费。可通过网上银行、支付宝、微信等方式缴费。逾期未缴费将影响选课和注册。',
            'type': 'warning',
            'priority': 'high',
            'sender': '财务处',
        },
        {
            'title': '图书馆暑期开放时间调整',
            'content': '图书馆暑期（7月1日-8月31日）开放时间调整为：周一至周五 8:00-17:00，周六 9:00-16:00，周日闭馆。请同学们合理安排学习时间。',
            'type': 'info',
            'priority': 'medium',
            'sender': '图书馆',
        },
        {
            'title': '奖学金评选开始',
            'content': '2024-2025学年优秀学生奖学金评选工作开始，申请时间为6月1日-6月15日。符合条件的同学请准备相关材料并在规定时间内提交申请。',
            'type': 'success',
            'priority': 'medium',
            'sender': '学工处',
            'action_url': '/student/profile/',
        },
        {
            'title': '网络维护通知',
            'content': '为提升网络服务质量，校园网将于本周六（6月1日）凌晨2:00-6:00进行维护升级，期间可能出现网络不稳定情况，请同学们提前做好准备。',
            'type': 'warning',
            'priority': 'low',
            'sender': '网络中心',
        }
    ]
    
    # 创建系统公告
    for notification_data in system_notifications:
        StudentNotification.objects.create(
            student=None,  # 全体学生
            **notification_data,
            created_at=timezone.now() - timedelta(days=notification_data.get('days_ago', 0))
        )
    
    # 个人通知（面向特定学生）
    personal_notifications = [
        {
            'title': '选课结果通知',
            'content': '您申请的《高等数学》课程选课成功，请按时上课。上课时间：周一、三、五 8:00-9:40，地点：教学楼A301。',
            'type': 'success',
            'priority': 'medium',
            'sender': '教务系统',
            'action_url': '/student/schedule/',
        },
        {
            'title': '成绩发布通知',
            'content': '《程序设计基础》课程成绩已发布，您的成绩为85分。如有疑问请在成绩发布后一周内联系任课教师。',
            'type': 'info',
            'priority': 'medium',
            'sender': '任课教师',
            'action_url': '/student/grades/',
        },
        {
            'title': '补考通知',
            'content': '《高等数学》课程期末考试成绩不及格，需要参加补考。补考时间：7月15日 14:00-16:00，地点：教学楼B201。',
            'type': 'error',
            'priority': 'high',
            'sender': '教务处',
        },
        {
            'title': '实习安排通知',
            'content': '您的专业实习安排已确定，实习单位：ABC科技公司，实习时间：7月1日-8月31日。请及时联系实习指导老师。',
            'type': 'info',
            'priority': 'medium',
            'sender': '实习指导老师',
        }
    ]
    
    # 为部分学生创建个人通知
    for i, student in enumerate(students[:5]):
        for j, notification_data in enumerate(personal_notifications):
            StudentNotification.objects.create(
                student=student,
                **notification_data,
                created_at=timezone.now() - timedelta(days=j, hours=i)
            )
    
    print("示例通知数据创建完成！")
    
    # 显示统计信息
    total_notifications = StudentNotification.objects.count()
    system_count = StudentNotification.objects.filter(student__isnull=True).count()
    personal_count = StudentNotification.objects.filter(student__isnull=False).count()
    
    print(f"总通知数：{total_notifications}")
    print(f"系统公告：{system_count}")
    print(f"个人通知：{personal_count}")

if __name__ == '__main__':
    create_sample_notifications()
