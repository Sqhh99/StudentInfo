from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.urls import resolve, reverse


class AuthRequiredMiddleware:
    """
    中间件检查用户是否有权限访问某些URL，如果没有则重定向到未授权页面
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # 允许访问的公共URL列表
        public_urls = [
            'index',         # 首页
            'about',         # 关于页面
            'login',         # 登录页面
            'register',      # 注册页面
            'logout',        # 登出页面
            'password_reset', # 密码重置
            'captcha-image', # 验证码图片
            'captcha-refresh', # 验证码刷新
            'unauthorized_access'  # 未授权访问页面
        ]
        
        # 先获取当前请求的URL名称
        current_url_name = None
        try:
            current_url_name = resolve(request.path_info).url_name
        except Exception:
            # 如果无法解析URL，则允许访问
            pass
            
        # 始终允许访问验证码相关路径
        if request.path.startswith('/captcha/'):
            return self.get_response(request)
            
        # 如果URL名称不在公共列表中，且用户未登录，则重定向到未授权页面
        if (current_url_name not in public_urls and 
            not request.user.is_authenticated and 
            not request.path.startswith('/admin/')):
            # 如果是AJAX请求，返回401状态码
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                response = self.get_response(request)
                response.status_code = 401
                return response
                
            # 否则重定向到未授权页面
            return redirect(settings.LOGIN_URL_REDIRECT)
            
        response = self.get_response(request)
        return response 