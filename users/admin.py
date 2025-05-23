from django.contrib import admin
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import User
import json
from django.urls import path
from django.template.response import TemplateResponse
from django.core.cache import cache
import redis
from django.conf import settings
from django.contrib import messages

# Register your models here.

# 注册User模型
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'last_login')
    list_filter = ('is_active', 'is_staff', 'date_joined', 'last_login')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login', 'last_login_ip', 'registration_ip')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('first_name', 'last_name', 'email')}),
        ('权限', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('重要日期', {'fields': ('date_joined', 'last_login')}),
        ('安全信息', {'fields': ('registration_ip', 'last_login_ip', 'failed_login_attempts', 'account_locked_until')}),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('session-health/', self.admin_site.admin_view(self.session_health_view), name='session-health'),
        ]
        return custom_urls + urls
    
    def session_health_view(self, request):
        """会话健康检查视图"""
        context = {
            'title': '会话健康状态',
            'has_permission': True,
            'site_title': self.admin_site.site_title,
            'site_header': self.admin_site.site_header,
        }
        
        # 获取会话配置
        session_engine = settings.SESSION_ENGINE
        session_cookie_age = getattr(settings, 'SESSION_COOKIE_AGE', 1209600)
        session_cookie_name = getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')
        
        # 会话基本信息
        session_info = {
            'session_engine': session_engine,
            'session_cookie_age': session_cookie_age,
            'session_cookie_name': session_cookie_name,
            'save_every_request': getattr(settings, 'SESSION_SAVE_EVERY_REQUEST', False),
            'expire_at_browser_close': getattr(settings, 'SESSION_EXPIRE_AT_BROWSER_CLOSE', False),
        }
        
        # 获取数据库中的会话数
        db_sessions = Session.objects.filter(expire_date__gt=timezone.now())
        db_session_count = db_sessions.count()
        
        # 分析最近活跃的会话
        recent_sessions = db_sessions.order_by('-expire_date')[:10]
        recent_sessions_data = []
        for session in recent_sessions:
            try:
                session_data = session.get_decoded()
                user_id = session_data.get('_auth_user_id')
                user = User.objects.get(pk=user_id) if user_id else None
                
                recent_sessions_data.append({
                    'session_key': session.session_key,
                    'user': user.username if user else '匿名用户',
                    'expire_date': session.expire_date,
                    'ip_address': session_data.get('_ip_address', '未知'),
                    'last_activity': session_data.get('_last_activity', 0),
                })
            except Exception as e:
                recent_sessions_data.append({
                    'session_key': session.session_key,
                    'user': '解析错误',
                    'expire_date': session.expire_date,
                    'ip_address': '未知',
                    'last_activity': 0,
                    'error': str(e)
                })
        
        # Redis会话状态检查
        redis_info = None
        if session_engine == 'django.contrib.sessions.backends.cache':
            try:
                # 获取Redis连接信息
                location = settings.CACHES['default'].get('LOCATION', '')
                if location.startswith('redis://'):
                    parts = location[8:].split(':')
                    host = parts[0]
                    port = int(parts[1].split('/')[0]) if len(parts) > 1 else 6379
                    
                    # 连接Redis并获取信息
                    redis_client = redis.Redis(host=host, port=port, socket_timeout=2)
                    redis_info = redis_client.info()
                    
                    # 获取会话相关的键数量
                    key_prefix = settings.CACHES['default'].get('KEY_PREFIX', '')
                    session_pattern = f"{key_prefix}:*{session_cookie_name}*"
                    session_keys = redis_client.keys(session_pattern)
                    
                    redis_info.update({
                        'session_keys_count': len(session_keys),
                        'redis_connection': 'OK',
                        'used_memory_human': redis_info.get('used_memory_human', '未知'),
                        'connected_clients': redis_info.get('connected_clients', 0),
                    })
            except Exception as e:
                redis_info = {'error': str(e), 'redis_connection': 'ERROR'}
                messages.error(request, f'Redis连接错误: {str(e)}')
        
        # 更新上下文
        context.update({
            'session_info': session_info,
            'db_session_count': db_session_count,
            'recent_sessions': recent_sessions_data,
            'redis_info': redis_info,
        })
        
        return TemplateResponse(request, 'admin/users/session_health.html', context)
