from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import datetime


class UserManager(BaseUserManager):
    def create_user(self, username, email, first_name, last_name, password=None):
        if not email:
            raise ValueError('用户必须有邮箱地址')
        if not username:
            raise ValueError('用户必须有用户名')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, first_name, last_name, password=None):
        user = self.create_user(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    first_name = models.CharField(max_length=30, verbose_name='名')
    last_name = models.CharField(max_length=30, verbose_name='姓')
    username = models.CharField(max_length=30, unique=True, verbose_name='用户名')
    email = models.EmailField(max_length=100, unique=True, verbose_name='电子邮箱')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='注册日期')
    last_login = models.DateTimeField(auto_now=True, verbose_name='最后登录')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # 安全与授权字段
    registration_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='注册IP')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='最后登录IP')
    last_password_change = models.DateTimeField(null=True, blank=True, verbose_name='最后密码修改')
    failed_login_attempts = models.PositiveIntegerField(default=0, verbose_name='失败登录尝试')
    last_failed_login = models.DateTimeField(null=True, blank=True, verbose_name='最后失败登录')
    account_locked_until = models.DateTimeField(null=True, blank=True, verbose_name='账户锁定至')
    
    # 隐私与授权设置
    email_verified = models.BooleanField(default=False, verbose_name='邮箱已验证')
    newsletter_subscription = models.BooleanField(default=False, verbose_name='订阅通讯')
    data_processing_consent = models.BooleanField(default=True, verbose_name='数据处理同意')
    cookie_consent = models.CharField(max_length=20, choices=[
        ('none', '无同意'),
        ('necessary', '仅必要Cookie'),
        ('all', '所有Cookie'),
    ], default='necessary', verbose_name='Cookie同意')

    # 添加字段: 会话管理相关
    active_sessions_count = models.PositiveIntegerField(default=0, verbose_name="活跃会话数")
    last_active_device = models.CharField(max_length=255, blank=True, null=True, verbose_name="最后活跃设备")
    login_days_count = models.PositiveIntegerField(default=0, verbose_name="累计登录天数")
    last_session_refresh = models.DateTimeField(null=True, blank=True, verbose_name="上次会话刷新时间")

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def __str__(self):
        return self.username

    def record_failed_login(self, ip_address=None):
        """记录失败登录尝试"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        if ip_address:
            self.last_login_ip = ip_address
            
        # 账户锁定逻辑 - 5次失败尝试锁定30分钟
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
            
        self.save(update_fields=['failed_login_attempts', 'last_failed_login', 
                                'last_login_ip', 'account_locked_until'])
                                
    def reset_failed_login(self):
        """重置失败登录尝试计数"""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
        
    def is_account_locked(self):
        """检查账户是否被锁定"""
        if self.account_locked_until and self.account_locked_until > timezone.now():
            return True
        # 如果锁定时间已过，自动重置
        elif self.account_locked_until:
            self.reset_failed_login()
        return False
        
    def record_password_change(self):
        """记录密码修改时间"""
        self.last_password_change = timezone.now()
        self.save(update_fields=['last_password_change'])

    def record_login(self, ip_address=None, user_agent=None):
        """记录成功登录并更新统计数据"""
        today = timezone.now().date()
        last_login_date = self.last_login.date() if self.last_login else None
        
        # 如果是新的一天登录，增加登录天数计数
        if not last_login_date or last_login_date < today:
            self.login_days_count += 1
            
        # 更新活跃会话数(简单增加，实际应该结合会话存储)
        self.active_sessions_count += 1
        
        # 保存设备信息
        if user_agent:
            self.last_active_device = self._get_device_info(user_agent)
            
        self.save(update_fields=['login_days_count', 'active_sessions_count', 'last_active_device'])
        
    def _get_device_info(self, user_agent):
        """从User-Agent解析设备信息"""
        # 简单实现，实际应使用更复杂的UA解析库如user_agents
        device = "未知设备"
        if "Windows" in user_agent:
            device = "Windows电脑"
        elif "Macintosh" in user_agent:
            device = "Mac电脑"
        elif "iPhone" in user_agent:
            device = "iPhone"
        elif "iPad" in user_agent:
            device = "iPad"
        elif "Android" in user_agent:
            if "Mobile" in user_agent:
                device = "Android手机"
            else:
                device = "Android平板"
        return device

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

# 记录用户不同设备的会话信息
class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions", verbose_name="用户")
    session_key = models.CharField(max_length=40, verbose_name="会话密钥")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    user_agent = models.TextField(blank=True, verbose_name="用户代理")
    device_type = models.CharField(max_length=50, blank=True, verbose_name="设备类型")
    browser = models.CharField(max_length=50, blank=True, verbose_name="浏览器")
    location = models.CharField(max_length=100, blank=True, verbose_name="地理位置")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="最后活动")
    is_active = models.BooleanField(default=True, verbose_name="是否活跃")
    
    class Meta:
        verbose_name = "用户会话"
        verbose_name_plural = "用户会话"
        
    def __str__(self):
        return f"{self.user.username} - {self.device_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
        
    def get_device_icon(self):
        """返回设备对应的Bootstrap图标类名"""
        if "Windows" in self.device_type or "Mac" in self.device_type:
            return "bi-laptop"
        elif "iPhone" in self.device_type:
            return "bi-phone"
        elif "iPad" in self.device_type or "平板" in self.device_type:
            return "bi-tablet"
        elif "Android" in self.device_type:
            if "手机" in self.device_type:
                return "bi-phone"
            else:
                return "bi-tablet"
        return "bi-device-unknown"
        
    def terminate(self):
        """终止此会话"""
        self.is_active = False
        self.save(update_fields=['is_active'])
        
# 用户登录活动统计
class UserLoginStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="login_stats", verbose_name="用户")
    total_logins = models.PositiveIntegerField(default=0, verbose_name="总登录次数")
    weekly_logins = models.JSONField(default=dict, verbose_name="每周登录统计")
    monthly_logins = models.JSONField(default=dict, verbose_name="每月登录统计")
    login_times = models.JSONField(default=dict, verbose_name="登录时间分布")
    device_stats = models.JSONField(default=dict, verbose_name="设备统计")
    browser_stats = models.JSONField(default=dict, verbose_name="浏览器统计")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="最后更新")
    
    class Meta:
        verbose_name = "登录统计"
        verbose_name_plural = "登录统计"
        
    def __str__(self):
        return f"{self.user.username} 的登录统计"
        
    def record_login(self, device_type="", browser=""):
        """记录一次登录并更新统计数据"""
        self.total_logins += 1
        
        # 更新当前星期几的登录计数
        weekday = timezone.now().strftime('%A')
        weekly_data = self.weekly_logins or {}
        weekly_data[weekday] = weekly_data.get(weekday, 0) + 1
        self.weekly_logins = weekly_data
        
        # 更新当前月份的登录计数 
        month = timezone.now().strftime('%B')
        monthly_data = self.monthly_logins or {}
        monthly_data[month] = monthly_data.get(month, 0) + 1
        self.monthly_logins = monthly_data
        
        # 更新登录时间分布
        hour = timezone.now().hour
        hour_range = f"{hour:02d}:00-{hour:02d}:59"
        login_times = self.login_times or {}
        login_times[hour_range] = login_times.get(hour_range, 0) + 1
        self.login_times = login_times
        
        # 更新设备统计
        if device_type:
            device_stats = self.device_stats or {}
            device_stats[device_type] = device_stats.get(device_type, 0) + 1
            self.device_stats = device_stats
            
        # 更新浏览器统计
        if browser:
            browser_stats = self.browser_stats or {}
            browser_stats[browser] = browser_stats.get(browser, 0) + 1
            self.browser_stats = browser_stats
            
        self.save()
