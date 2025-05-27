from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.

class Major(models.Model):
    """专业模型"""
    name = models.CharField(max_length=50, verbose_name='专业名称')
    code = models.CharField(max_length=20, verbose_name='专业代码', unique=True)
    description = models.TextField(verbose_name='专业描述', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '专业'
        verbose_name_plural = '专业'


class Class(models.Model):
    """班级模型"""
    name = models.CharField(max_length=50, verbose_name='班级名称')
    code = models.CharField(max_length=20, verbose_name='班级代码', unique=True)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='classes', verbose_name='所属专业')
    admission_year = models.IntegerField(verbose_name='入学年份')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '班级'
        verbose_name_plural = '班级'


class Student(models.Model):
    """学生模型"""
    GENDER_CHOICES = (
        ('male', '男'),
        ('female', '女'),
    )
    STATUS_CHOICES = (
        ('active', '在读'),
        ('inactive', '休学'),
        ('graduated', '已毕业'),
        ('transferred', '已转学'),
    )
    
    student_id = models.CharField(max_length=20, unique=True, verbose_name='学号')
    name = models.CharField(max_length=50, verbose_name='姓名')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name='性别')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students', verbose_name='班级')
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name='students', verbose_name='专业')
    admission_date = models.DateField(verbose_name='入学时间')
    phone = models.CharField(max_length=20, verbose_name='联系电话', blank=True, null=True)
    email = models.EmailField(max_length=100, verbose_name='电子邮箱', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='状态')
    password = models.CharField(max_length=128, verbose_name='密码', help_text='学生登录密码，默认为学号', default='pbkdf2_sha256$260000$default$default')  # 临时默认值
    profile_image = models.ImageField(upload_to='student_profiles/', verbose_name='头像', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def set_password(self, raw_password):
        """设置密码"""
        self.password = make_password(raw_password)
        
    def check_password(self, raw_password):
        """验证密码"""
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        """重写save方法，如果是新建学生且没有密码，则设置默认密码为学号"""
        if not self.pk and not self.password:
            self.set_password(self.student_id)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.student_id})"

    class Meta:
        verbose_name = '学生'
        verbose_name_plural = '学生'


class Department(models.Model):
    """院系模型"""
    name = models.CharField(max_length=50, verbose_name='院系名称')
    code = models.CharField(max_length=20, verbose_name='院系代码', unique=True)
    description = models.TextField(verbose_name='院系描述', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '院系'
        verbose_name_plural = '院系'


class Course(models.Model):
    """课程模型"""
    STATUS_CHOICES = (
        ('active', '已开课'),
        ('pending', '待开课'),
        ('completed', '已结课'),
        ('cancelled', '已取消'),
    )
    
    code = models.CharField(max_length=20, unique=True, verbose_name='课程编号')
    name = models.CharField(max_length=100, verbose_name='课程名称')
    credit = models.DecimalField(max_digits=3, decimal_places=1, verbose_name='学分')
    teacher = models.CharField(max_length=50, verbose_name='任课教师')
    description = models.TextField(verbose_name='课程描述', blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses', verbose_name='所属院系')
    class_time = models.CharField(max_length=50, verbose_name='上课时间')
    location = models.CharField(max_length=50, verbose_name='上课地点')
    capacity = models.PositiveIntegerField(verbose_name='课程容量')
    semester = models.CharField(max_length=20, verbose_name='开课学期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='课程状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = '课程'


class Score(models.Model):
    """成绩模型"""
    GRADE_CHOICES = (
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('B-', 'B-'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('C-', 'C-'),
        ('D+', 'D+'),
        ('D', 'D'),
        ('F', 'F'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores', verbose_name='学生')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='scores', verbose_name='课程')
    score = models.DecimalField(max_digits=5, decimal_places=1, verbose_name='分数')
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, verbose_name='等级', blank=True, null=True)
    semester = models.CharField(max_length=20, verbose_name='学期')
    comment = models.TextField(verbose_name='评语', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    def save(self, *args, **kwargs):
        # 自动计算等级
        if self.score is not None:
            if self.score >= 95:
                self.grade = 'A+'
            elif self.score >= 90:
                self.grade = 'A'
            elif self.score >= 85:
                self.grade = 'A-'
            elif self.score >= 80:
                self.grade = 'B+'
            elif self.score >= 75:
                self.grade = 'B'
            elif self.score >= 70:
                self.grade = 'B-'
            elif self.score >= 65:
                self.grade = 'C+'
            elif self.score >= 60:
                self.grade = 'C'
            elif self.score >= 55:
                self.grade = 'C-'
            elif self.score >= 50:
                self.grade = 'D+'
            elif self.score >= 45:
                self.grade = 'D'
            else:
                self.grade = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.name} - {self.course.name}: {self.score}"

    class Meta:
        verbose_name = '成绩'
        verbose_name_plural = '成绩'
        unique_together = ('student', 'course', 'semester')
