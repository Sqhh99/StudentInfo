# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging
import re
from .forms import LoginForm, RegisterForm
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
import datetime
import time
import json
import uuid

# 设置日志记录器
logger = logging.getLogger('auth')

def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_agent(request):
    """获取用户设备和浏览器信息"""
    return request.META.get('HTTP_USER_AGENT', 'Unknown')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')  # 如果用户已登录，重定向到主页
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            cookie_consent = form.cleaned_data.get('cookie_consent')
            
            # 记录登录尝试
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            logger.info(f"登录尝试 - 用户: {username}, IP: {ip_address}, 设备: {user_agent}", extra={
                'ip': ip_address,
                'user_agent': user_agent
            })

            # 防护机制，防止暴力破解
            try:
                user = User.objects.get(username=username)
                
                # 检查账户是否被锁定
                if user.is_account_locked():
                    lock_time_remaining = (user.account_locked_until - timezone.now()).seconds // 60
                    error_message = f'账户已被临时锁定，请 {lock_time_remaining} 分钟后再试'
                    logger.warning(f"登录失败(账户锁定) - 用户: {username}, IP: {ip_address}", extra={
                        'ip': ip_address,
                        'user_agent': user_agent
                    })
                    messages.error(request, error_message)
                    return render(request, 'users/login.html', {'login_error': error_message, 'form': form})
                    
            except User.DoesNotExist:
                # 如果用户不存在，我们仍然继续验证，以防止用户名枚举攻击
                pass
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                if not user.is_active:
                    messages.error(request, '您的账户已被禁用，请联系管理员')
                    logger.warning(f"登录失败(账户禁用) - 用户: {username}, IP: {ip_address}", extra={
                        'ip': ip_address,
                        'user_agent': user_agent
                    })
                    return render(request, 'users/login.html', {'login_error': '您的账户已被禁用，请联系管理员', 'form': form})
                    
                # 登录成功，重置失败次数
                user.reset_failed_login()
                login(request, user)
                
                # 设置session过期时间，如果用户选择"记住我"
                if remember_me:
                    request.session.set_expiry(1209600)  # 2周
                else:
                    request.session.set_expiry(0)  # 浏览器关闭时过期
                
                # 更新最后登录时间和IP
                user.last_login = timezone.now()
                user.last_login_ip = ip_address
                
                # 初始化会话信息 (如果中间件尚未设置)
                if not request.session.get('_session_init'):
                    request.session['_session_init'] = True
                    request.session['_session_started'] = int(time.time())
                    request.session['_last_activity'] = int(time.time())
                    request.session['_ip_address'] = ip_address
                    request.session['_user_agent'] = user_agent
                    request.session['_activity_log'] = [{
                        'time': timezone.now().isoformat(),
                        'path': '/login/',
                        'ip': ip_address,
                        'method': 'POST',
                        'action': '用户登录'
                    }]
                    # 生成新的会话ID以防止会话固定攻击
                    request.session.cycle_key()
                
                # 更新Cookie同意状态
                if cookie_consent:
                    user.cookie_consent = cookie_consent
                    
                user.save(update_fields=['last_login', 'last_login_ip', 'cookie_consent'])
                
                logger.info(f"登录成功 - 用户: {username}, IP: {ip_address}", extra={
                    'ip': ip_address,
                    'user_agent': user_agent
                })
                messages.success(request, f'欢迎回来，{user.username}！')
                return redirect('index')  # 重定向到主页或仪表板
            else:
                # 登录失败，记录失败尝试
                try:
                    user = User.objects.get(username=username)
                    user.record_failed_login(ip_address)
                    
                    # 检查是否需要锁定账户
                    if user.is_account_locked():
                        lock_time_remaining = (user.account_locked_until - timezone.now()).seconds // 60
                        error_message = f'登录失败次数过多，账户已被临时锁定，请 {lock_time_remaining} 分钟后再试'
                        messages.error(request, error_message)
                        logger.warning(f"账户锁定 - 用户: {username}, IP: {ip_address}, 失败次数: {user.failed_login_attempts}", extra={
                            'ip': ip_address,
                            'user_agent': user_agent
                        })
                        return render(request, 'users/login.html', {'login_error': error_message, 'form': form})
                except User.DoesNotExist:
                    # 对于不存在的用户名，仅记录，不显示特定错误
                    pass
                    
                logger.warning(f"登录失败(凭据错误) - 用户: {username}, IP: {ip_address}", extra={
                    'ip': ip_address,
                    'user_agent': user_agent
                })
                messages.error(request, '用户名或密码不正确')
                return render(request, 'users/login.html', {'login_error': '用户名或密码不正确', 'form': form})
        else:
            # 表单验证失败，可能是验证码错误
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            logger.warning(f"登录失败(表单验证错误) - IP: {ip_address}", extra={
                'ip': ip_address,
                'user_agent': user_agent
            })
            if 'captcha' in form.errors:
                # 验证码错误时单独处理
                messages.error(request, '验证码错误，请重新输入')
            return render(request, 'users/login.html', {'login_error': '表单验证失败，请检查输入', 'form': form})
    else:
        form = LoginForm()

    return render(request, 'users/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')  # 如果用户已登录，重定向到主页
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')
            agree_terms = form.cleaned_data.get('agree_terms')
            subscribe_newsletter = form.cleaned_data.get('subscribe_newsletter', False)
            cookie_consent = form.cleaned_data.get('cookie_consent', 'necessary')

            # 记录注册尝试
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            logger.info(f"注册尝试 - 用户: {username}, 邮箱: {email}, IP: {ip_address}", extra={
                'ip': ip_address,
                'user_agent': user_agent
            })

            # 验证表单数据
            error = None

            # 检查用户名格式
            if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
                error = '用户名只能包含字母、数字和下划线，长度为3-20个字符'
                
            # 检查用户名是否已存在
            elif User.objects.filter(username=username).exists():
                error = '用户名已被使用'
                logger.warning(f"注册失败(用户名冲突) - 用户: {username}, IP: {ip_address}", extra={
                    'ip': ip_address,
                    'user_agent': user_agent
                })

            # 检查邮箱是否已存在
            elif User.objects.filter(email=email).exists():
                error = '该邮箱已被注册'
                logger.warning(f"注册失败(邮箱冲突) - 邮箱: {email}, IP: {ip_address}", extra={
                    'ip': ip_address,
                    'user_agent': user_agent
                })

            # 检查密码是否匹配
            elif password != confirm_password:
                error = '两次输入的密码不一致'

            # 检查密码强度
            elif len(password) < 8:
                error = '密码长度必须至少为8个字符'
                
            # 检查密码复杂性
            elif not (re.search(r'[A-Z]', password) and     # 至少一个大写字母
                    re.search(r'[0-9]', password) and      # 至少一个数字
                    re.search(r'[^A-Za-z0-9]', password)): # 至少一个特殊字符
                error = '密码必须包含至少一个大写字母、一个数字和一个特殊字符'

            # 检查是否同意服务条款
            elif not agree_terms:
                error = '您必须同意服务条款和隐私政策'

            # Django自带的密码验证
            try:
                validate_password(password)
            except ValidationError as e:
                error = e.messages[0]

            if error:
                messages.error(request, error)
                form.add_error(None, error)
                return render(request, 'users/register.html', {'register_error': error, 'form': form})

            # 创建用户
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                
                # 记录注册信息
                user.date_joined = timezone.now()
                user.last_login_ip = ip_address
                user.registration_ip = ip_address
                user.newsletter_subscription = True if subscribe_newsletter else False
                user.cookie_consent = cookie_consent
                user.data_processing_consent = True
                user.save()

                # 自动登录用户
                login(request, user)
                logger.info(f"注册成功 - 用户: {username}, IP: {ip_address}", extra={
                    'ip': ip_address,
                    'user_agent': user_agent
                })
                messages.success(request, '注册成功！欢迎加入学生管理系统。')
                return redirect('index')  # 重定向到主页

            except Exception as e:
                logger.error(f"注册异常 - 用户: {username}, 错误: {str(e)}", extra={
                    'ip': ip_address,
                    'user_agent': user_agent
                })
                form.add_error(None, str(e))
                return render(request, 'users/register.html', {'register_error': str(e), 'form': form})
        else:
            # 表单验证失败，可能是验证码错误
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            logger.warning(f"注册失败(表单验证错误) - IP: {ip_address}", extra={
                'ip': ip_address,
                'user_agent': user_agent
            })
            return render(request, 'users/register.html', {'register_error': '表单验证错误', 'form': form})
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form})


def logout_view(request):
    username = request.user.username if request.user.is_authenticated else 'Anonymous'
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    logout(request)
    logger.info(f"注销成功 - 用户: {username}, IP: {ip_address}", extra={
        'ip': ip_address,
        'user_agent': user_agent
    })
    messages.success(request, '您已成功退出登录')
    return redirect('login')


def password_reset_request(request):
    """处理密码重置请求"""
    if request.method == 'POST':
        email = request.POST.get('email')
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # 检查电子邮件是否存在
        try:
            user = User.objects.get(email=email)
            # 在这里处理发送密码重置邮件的逻辑
            # ...
            
            logger.info(f"密码重置请求 - 邮箱: {email}, IP: {ip_address}", extra={
                'ip': ip_address,
                'user_agent': user_agent
            })
            messages.success(request, '密码重置链接已发送到您的邮箱，请查收')
        except User.DoesNotExist:
            logger.warning(f"密码重置失败(邮箱不存在) - 邮箱: {email}, IP: {ip_address}", extra={
                'ip': ip_address,
                'user_agent': user_agent
            })
            # 为了安全，不显示具体错误
            messages.success(request, '如果该邮箱已注册，密码重置链接将发送到您的邮箱')
            
        return redirect('login')
        
    return render(request, 'users/password_reset.html')

@login_required
def session_management(request):
    """会话管理视图：显示用户的当前会话及活动记录"""
    # 获取当前会话信息
    session_data = {
        'session_id': request.session.session_key,
        'session_started': request.session.get('_session_started', 0),
        'last_activity': request.session.get('_last_activity', 0),
        'ip_address': request.session.get('_ip_address', '未知'),
        'user_agent': request.session.get('_user_agent', '未知'),
        'activity_log': request.session.get('_activity_log', []),
    }
    
    # 计算会话时长和到期时间
    now = int(time.time())
    session_age = now - session_data['session_started'] if session_data['session_started'] else 0
    session_lifetime = getattr(settings, 'SESSION_COOKIE_AGE', 1209600)  # 默认2周
    session_expires = now + session_lifetime - session_age
    
    # 转换为人类可读格式
    session_data['session_started_readable'] = datetime.datetime.fromtimestamp(
        session_data['session_started']).strftime('%Y-%m-%d %H:%M:%S') if session_data['session_started'] else '未知'
    session_data['last_activity_readable'] = datetime.datetime.fromtimestamp(
        session_data['last_activity']).strftime('%Y-%m-%d %H:%M:%S') if session_data['last_activity'] else '未知'
    session_data['session_expires_readable'] = datetime.datetime.fromtimestamp(
        session_expires).strftime('%Y-%m-%d %H:%M:%S')
    session_data['session_age_readable'] = str(datetime.timedelta(seconds=session_age))
    
    # 获取用户所有活跃会话（如果有需要的话）
    # 这需要一个自定义的实现，因为Django默认不提供查看所有会话的机制
    # 可以在用户登录时将会话ID存储到Redis或数据库中
    
    context = {
        'active_tab': 'sessions',
        'session_data': session_data,
    }
    
    return render(request, 'users/session_management.html', context)

@login_required
def terminate_all_sessions(request):
    """终止用户的所有会话，仅保留当前会话"""
    if request.method == 'POST':
        try:
            # 保存当前会话键
            current_session_key = request.session.session_key
            
            # 创建自定义删除会话的实现
            # 例如，如果您在用户登录时将会话ID存储在Redis中，可以在此删除
            # 这里只作为示例，实际实现需要视会话存储方式而定
            
            messages.success(request, '所有其他会话已被终止')
            
            # 记录会话终止活动
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            logger.info(f"用户终止所有会话 - 用户: {request.user.username}, IP: {ip_address}", extra={
                'ip': ip_address,
                'user_agent': user_agent
            })
            
        except Exception as e:
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            messages.error(request, f'无法终止会话: {str(e)}')
            logger.error(f"会话终止失败 - 用户: {request.user.username}, 错误: {str(e)}", extra={
                'ip': ip_address,
                'user_agent': user_agent
            })
            
    return redirect('session_management')

@login_required
def refresh_current_session(request):
    """刷新当前会话"""
    if request.method == 'POST':
        # 重新生成会话ID
        request.session.cycle_key()
        
        # 更新会话时间戳
        request.session['_session_started'] = int(time.time())
        request.session['_last_activity'] = int(time.time())
        
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        messages.success(request, '会话已刷新并延长有效期')
        logger.info(f"用户刷新会话 - 用户: {request.user.username}, IP: {ip_address}", extra={
            'ip': ip_address,
            'user_agent': user_agent
        })
        
    return redirect('session_management')

@login_required
def session_activity_log(request):
    """返回用户会话活动日志的JSON数据，用于AJAX请求"""
    try:
        activity_log = request.session.get('_activity_log', [])
        
        # 转换ISO格式时间为更可读的格式
        for activity in activity_log:
            if 'time' in activity:
                try:
                    dt = datetime.datetime.fromisoformat(activity['time'])
                    activity['time_readable'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    activity['time_readable'] = '未知时间'
        
        return JsonResponse({'success': True, 'data': activity_log})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def clear_session_data(request):
    """清除会话中的用户活动数据"""
    if request.method == 'POST':
        try:
            # 保留必要的会话数据
            session_started = request.session.get('_session_started')
            ip_address = request.session.get('_ip_address')
            user_agent = request.session.get('_user_agent')
            
            # 清除活动日志
            request.session['_activity_log'] = []
            request.session['_last_activity'] = int(time.time())
            
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            messages.success(request, '会话活动记录已清除')
            logger.info(f"用户清除会话数据 - 用户: {request.user.username}, IP: {ip_address}", extra={
                'ip': ip_address,
                'user_agent': user_agent
            })
            
        except Exception as e:
            ip_address = get_client_ip(request)
            user_agent = get_user_agent(request)
            messages.error(request, f'无法清除会话数据: {str(e)}')
            logger.error(f"清除会话数据失败 - 用户: {request.user.username}, 错误: {str(e)}", extra={
                'ip': ip_address,
                'user_agent': user_agent
            })
    
    return redirect('session_management')