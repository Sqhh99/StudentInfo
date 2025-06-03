import time
import logging
import json
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import resolve, reverse
import redis
from redis.exceptions import RedisError

logger = logging.getLogger('auth')

class SessionManagementMiddleware:
    """
    会话管理中间件，用于增强会话安全性和用户体验：
    1. 会话活动时间跟踪
    2. 会话到期前刷新
    3. 防止会话固定攻击
    4. 基于IP的会话保护
    5. 浏览器指纹会话绑定
    6. 会话活动记录
    7. Redis异常处理和会话回退
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # 记录Redis连接状态
        self.redis_available = True
        # 尝试初始连接Redis
        self._check_redis_connection()
        
    def __call__(self, request):
        # 检查Redis连接状态
        if not self.redis_available and settings.SESSION_ENGINE == 'django.contrib.sessions.backends.cache':
            # 如果Redis不可用且当前使用的是缓存会话，切换到数据库会话
            self._fallback_to_db_session()
            logger.warning("会话引擎已切换到数据库回退模式", extra={
                'ip': '127.0.0.1',
                'user_agent': 'System'
            })
            
        # 跳过静态资源请求和管理后台请求
        if self._should_skip_request(request):
            return self.get_response(request)
            
        try:
            # 处理会话安全性
            self._handle_session_security(request)
            
            # 获取响应
            response = self.get_response(request)
            
            # 保存会话活动
            if hasattr(request, 'user') and request.user.is_authenticated:
                self._update_session_activity(request)
                
            return response
        except (redis.exceptions.RedisError, ConnectionError) as e:
            # 处理Redis连接问题
            logger.error(f"Redis连接错误: {str(e)}", extra={
                'ip': self._get_client_ip(request) if hasattr(request, 'META') else '127.0.0.1',
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown') if hasattr(request, 'META') else 'System'
            })
            self.redis_available = False
            
            # 切换到数据库会话
            self._fallback_to_db_session()
            
            # 继续处理请求
            return self.get_response(request)
        except Exception as e:
            # 其他未预期的错误
            logger.error(f"会话处理错误: {str(e)}", extra={
                'ip': self._get_client_ip(request) if hasattr(request, 'META') else '127.0.0.1',
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown') if hasattr(request, 'META') else 'System'
            })
            return self.get_response(request)
    
    def _check_redis_connection(self):
        """检查Redis连接是否可用"""
        try:
            # 获取Redis配置
            cache_config = settings.CACHES['default']
            location = cache_config.get('LOCATION', '')

            if not location.startswith('redis://'):
                # 不是Redis缓存后端
                return

            # 尝试解析Redis连接地址
            # 处理格式: redis://host:port/db 或 redis://:password@host:port/db
            location_without_schema = location[8:]  # 去掉 'redis://'

            # 处理密码认证格式：:password@host:port
            password = None
            if '@' in location_without_schema:
                auth_part, host_part = location_without_schema.split('@', 1)
                if auth_part.startswith(':'):
                    password = auth_part[1:]  # 去掉开头的冒号
                location_without_schema = host_part

            # 从OPTIONS中获取密码（优先级更高）
            if not password:
                password = cache_config.get('OPTIONS', {}).get('PASSWORD')

            # 处理可能包含数据库号的地址
            if '/' in location_without_schema:
                host_port, db = location_without_schema.split('/', 1)
            else:
                host_port = location_without_schema
                db = '0'

            # 提取主机和端口
            if ':' in host_port:
                host, port_str = host_port.split(':', 1)
                port = int(port_str)
            else:
                host = host_port
                port = 6379

            # 尝试连接（包含密码）
            client = redis.Redis(
                host=host,
                port=port,
                password=password,  # ✅ 添加密码
                db=int(db) if db.isdigit() else 0,
                socket_timeout=1,
                socket_connect_timeout=1
            )
            client.ping()
            self.redis_available = True

        except Exception as e:
            self.redis_available = False
            logger.error(f"Redis连接检查失败: {str(e)}", extra={
                'ip': '127.0.0.1',
                'user_agent': 'System'
            })
            
    def _fallback_to_db_session(self):
        """切换到数据库会话引擎"""
        if hasattr(settings, 'SESSION_FALLBACK_ENGINE'):
            # 临时修改会话引擎设置
            settings.SESSION_ENGINE = settings.SESSION_FALLBACK_ENGINE
        else:
            # 默认使用数据库会话引擎
            settings.SESSION_ENGINE = 'django.contrib.sessions.backends.db'
            
    def _should_skip_request(self, request):
        """确定是否应该跳过对请求的处理"""
        path = request.path_info.lstrip('/')
        return (
            path.startswith(getattr(settings, 'STATIC_URL', 'static').lstrip('/')) or
            path.startswith(getattr(settings, 'MEDIA_URL', 'media').lstrip('/')) or
            path.startswith('admin/')
        )
        
    def _handle_session_security(self, request):
        """处理会话安全性检查"""
        if not request.session.get('_session_init'):
            # 新会话初始化
            self._initialize_session(request)
            return
            
        # 会话IP验证 (如果启用)
        if not self._validate_session_ip(request):
            self._terminate_session(request, "会话IP验证失败")
            return

        # 会话用户代理验证 (如果启用)
        if not self._validate_session_user_agent(request):
            self._terminate_session(request, "会话用户代理验证失败")
            return
            
        # 检查会话是否接近过期并需要刷新
        if self._should_refresh_session(request):
            self._refresh_session(request)
            
    def _initialize_session(self, request):
        """初始化新会话"""
        request.session['_session_init'] = True
        request.session['_session_started'] = int(time.time())
        request.session['_last_activity'] = int(time.time())
        request.session['_ip_address'] = self._get_client_ip(request)
        request.session['_user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        request.session['_activity_log'] = []
        
        # 生成新的会话ID以防止会话固定攻击
        request.session.cycle_key()
        
    def _validate_session_ip(self, request):
        """验证当前IP是否与会话IP匹配"""
        # 可根据需要调整此方法为严格模式或宽松模式
        # 当前为宽松模式：仅记录IP变化但不强制终止会话
        original_ip = request.session.get('_ip_address', '')
        current_ip = self._get_client_ip(request)
        
        if original_ip and original_ip != current_ip:
            # 记录IP变化但不终止会话
            logger.warning(
                f"会话IP变化 - 原IP: {original_ip}, 新IP: {current_ip}, "
                f"用户: {request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'}",
                extra={
                    'ip': current_ip,
                    'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown')
                }
            )
            # 更新会话IP
            request.session['_ip_address'] = current_ip
            # 可以在此添加IP变化警告通知
            
        return True
        
    def _validate_session_user_agent(self, request):
        """验证用户代理是否与会话中记录的一致"""
        # 同样为宽松模式：记录变化但不终止会话
        original_ua = request.session.get('_user_agent', '')
        current_ua = request.META.get('HTTP_USER_AGENT', '')
        
        if original_ua and original_ua != current_ua:
            logger.warning(
                f"会话用户代理变化 - 用户: {request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'}",
                extra={
                    'ip': self._get_client_ip(request),
                    'user_agent': current_ua
                }
            )
            # 更新会话中的用户代理
            request.session['_user_agent'] = current_ua
            
        return True
        
    def _should_refresh_session(self, request):
        """确定是否应该刷新会话以防止过期"""
        # 如果用户已登录且会话接近过期 (80% 会话生命周期)
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return False
            
        last_activity = request.session.get('_last_activity', 0)
        session_age = int(time.time()) - last_activity
        session_lifetime = getattr(settings, 'SESSION_COOKIE_AGE', 1209600)  # 默认2周
        refresh_threshold = int(session_lifetime * 0.8)
        
        return session_age > refresh_threshold
    
    def _refresh_session(self, request):
        """刷新会话以延长其生命周期"""
        request.session.modified = True
        request.session['_last_activity'] = int(time.time())
        # 在适当情况下轮换会话密钥
        if int(time.time()) - request.session.get('_session_started', 0) > 86400:  # 一天
            request.session.cycle_key()
            request.session['_session_started'] = int(time.time())
            
    def _update_session_activity(self, request):
        """更新会话活动记录"""
        request.session['_last_activity'] = int(time.time())
        
        # 仅记录重要活动以避免会话过大
        if self._is_important_activity(request):
            # 获取当前活动日志并添加新活动
            activities = request.session.get('_activity_log', [])
            
            # 限制活动日志大小，保持最近的10条记录
            if len(activities) >= 10:
                activities = activities[-9:]
                
            # 添加新活动
            activities.append({
                'time': timezone.now().isoformat(),
                'path': request.path,
                'ip': self._get_client_ip(request),
                'method': request.method
            })
            
            request.session['_activity_log'] = activities
        
    def _is_important_activity(self, request):
        """确定是否为重要活动需要记录"""
        # 定义需要记录的路径模式或行为
        important_urls = [
            '/login/', '/logout/', '/register/', '/profile/', 
            '/settings/', '/password/change/', '/admin/'
        ]
        
        # 检查当前路径是否匹配任何重要路径
        current_path = request.path
        for url in important_urls:
            if current_path.startswith(url):
                return True
                
        # 所有POST请求都被视为重要活动
        if request.method == 'POST':
            return True
            
        return False
        
    def _terminate_session(self, request, reason):
        """终止会话并记录原因"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            username = request.user.username
            client_ip = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            
            logger.warning(
                f"强制会话终止 - 用户: {username}, 原因: {reason}, IP: {client_ip}",
                extra={
                    'ip': client_ip,
                    'user_agent': user_agent
                }
            )
            logout(request)
            
        # 完全重置会话
        request.session.flush()
        
    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip 