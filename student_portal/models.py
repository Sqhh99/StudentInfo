from django.db import models
from students.models import Student, Course, Score

# 学生选课模型
class Enrollment(models.Model):
    """学生选课模型"""
    STATUS_CHOICES = (
        ('enrolled', '已选课'),
        ('dropped', '已退课'),
        ('completed', '已完成'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments', verbose_name='学生')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name='课程')
    enrollment_date = models.DateTimeField(auto_now_add=True, verbose_name='选课时间')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled', verbose_name='状态')
    semester = models.CharField(max_length=20, verbose_name='学期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '选课记录'
        verbose_name_plural = '选课记录'
        unique_together = ('student', 'course', 'semester')

    def __str__(self):
        return f"{self.student.name} - {self.course.name}"


class StudentNotification(models.Model):
    """学生通知模型"""
    TYPE_CHOICES = (
        ('course', '课程通知'),
        ('exam', '考试通知'),
        ('grade', '成绩通知'),
        ('system', '系统通知'),
        ('academic', '学术通知'),
    )
    
    PRIORITY_CHOICES = (
        ('low', '低'),
        ('medium', '中'),
        ('high', '高'),
    )
    
    title = models.CharField(max_length=200, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system', verbose_name='类型')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='优先级')
    sender = models.CharField(max_length=100, verbose_name='发送者', null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notifications', verbose_name='学生', null=True, blank=True)
    is_read = models.BooleanField(default=False, verbose_name='已读')
    action_url = models.URLField(verbose_name='操作链接', null=True, blank=True)
    attachment = models.FileField(upload_to='notifications/', verbose_name='附件', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '学生通知'
        verbose_name_plural = '学生通知'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.student.name if self.student else '全局通知'}"
    
    def get_type_display_zh(self):
        """获取中文类型显示"""
        type_map = {
            'course': '课程',
            'exam': '考试', 
            'grade': '成绩',
            'system': '系统',
            'academic': '学术',
        }
        return type_map.get(self.type, self.type)
