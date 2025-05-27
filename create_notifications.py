"""
创建示例学生通知数据
"""
import os
import sys
import django

# 添加项目根目录到 Python 路径
sys.path.append('d:/a_django_project/StudentInfo')

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'StudentInfo.settings')
django.setup()

from student_portal.models import StudentNotification
from students.models import Student
from django.utils import timezone
from datetime import timedelta

def create_sample_notifications():
    """创建示例通知"""
    
    # 创建全局通知（所有学生可见）
    global_notifications = [
        {
            'title': '系统维护通知',
            'content': '学生门户系统将于本周六凌晨2:00-6:00进行系统维护，期间无法登录，请提前安排学习计划。',
            'type': 'system',
            'priority': 'high',
            'sender': '系统管理员'
        },
        {
            'title': '期末考试安排通知',
            'content': '2025年春季学期期末考试将于6月20日-6月30日举行，请各位同学认真复习，按时参加考试。具体考试时间请查看考试安排表。',
            'type': 'exam',
            'priority': 'high',
            'sender': '教务处'
        },
        {
            'title': '选课提醒',
            'content': '2025年秋季学期选课即将开始，请同学们于4月1日-4月15日期间完成选课。逾期将无法修改选课结果。',
            'type': 'course',
            'priority': 'medium',
            'sender': '教务处'
        },
        {
            'title': '图书馆开放时间调整',
            'content': '自下周一起，图书馆开放时间调整为7:00-22:00，请同学们合理安排学习时间。',
            'type': 'system',
            'priority': 'low',
            'sender': '图书馆'
        },
        {
            'title': '学术讲座通知',
            'content': '著名计算机科学家李教授将于本周五下午2:00在学术报告厅举办"人工智能发展趋势"专题讲座，欢迎广大师生参加。',
            'type': 'academic',
            'priority': 'medium',
            'sender': '学术委员会'
        },
        {
            'title': '奖学金申请通知',
            'content': '2024-2025学年优秀学生奖学金申请现已开始，符合条件的同学请于4月30日前提交申请材料。详情请咨询学生处。',
            'type': 'academic',
            'priority': 'high',
            'sender': '学生处'
        },
        {
            'title': '校园网络升级通知',
            'content': '为提升网络服务质量，校园网将进行全面升级。升级期间可能出现短暂的网络中断，请大家理解。',
            'type': 'system',
            'priority': 'medium',
            'sender': '网络中心'
        },
        {
            'title': '课程评教提醒',
            'content': '本学期课程评教已开始，请同学们认真填写评教问卷，您的意见对提高教学质量非常重要。',
            'type': 'course',
            'priority': 'medium',
            'sender': '教务处'
        }
    ]
    
    print("开始创建示例通知...")
    
    # 创建全局通知
    for i, notification_data in enumerate(global_notifications):
        notification = StudentNotification.objects.create(
            title=notification_data['title'],
            content=notification_data['content'],
            type=notification_data['type'],
            priority=notification_data['priority'],
            sender=notification_data['sender'],
            student=None,  # 全局通知
            created_at=timezone.now() - timedelta(days=i),
            is_read=False
        )
        print(f"创建全局通知: {notification.title}")
    
    # 为特定学生创建个人通知
    try:
        students = Student.objects.all()[:3]  # 取前3个学生
        
        personal_notifications = [
            {
                'title': '成绩查询通知',
                'content': '您的期中考试成绩已发布，请登录系统查看详细成绩信息。',
                'type': 'academic',
                'priority': 'medium',
                'sender': '任课教师'
            },
            {
                'title': '课程冲突提醒',
                'content': '检测到您选择的课程存在时间冲突，请及时调整选课安排。',
                'type': 'course',
                'priority': 'high',
                'sender': '系统'
            },
            {
                'title': '缴费提醒',
                'content': '您的学费缴费截止日期即将到期，请及时完成缴费。',
                'type': 'system',
                'priority': 'high',
                'sender': '财务处'
            }
        ]
        
        for student in students:
            for j, notification_data in enumerate(personal_notifications):
                notification = StudentNotification.objects.create(
                    title=notification_data['title'],
                    content=notification_data['content'],
                    type=notification_data['type'],
                    priority=notification_data['priority'],
                    sender=notification_data['sender'],
                    student=student,
                    created_at=timezone.now() - timedelta(hours=j*6),
                    is_read=False
                )
                print(f"为学生 {student.name} 创建个人通知: {notification.title}")
                
    except Exception as e:
        print(f"创建个人通知时出错: {e}")
    
    print("示例通知创建完成！")

if __name__ == "__main__":
    create_sample_notifications()
