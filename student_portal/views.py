from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg, Count, Q, Max, Min
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import models
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import make_password, check_password
import json

from students.models import Student, Course, Score, Department
from .models import Enrollment, StudentNotification
from .forms import StudentLoginForm, StudentProfileForm, CourseEnrollmentForm


def student_login(request):
    """学生登录视图"""
    # 如果学生已经登录，重定向到仪表板
    if request.session.get('student_id'):
        return redirect('student_portal:dashboard')
    
    if request.method == 'POST':
        form = StudentLoginForm(data=request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            # 在session中存储学生信息
            request.session['student_id'] = student.id
            request.session['student_name'] = student.name
            request.session['student_student_id'] = student.student_id
            messages.success(request, f'欢迎回来，{student.name}！')
            return redirect('student_portal:dashboard')
    else:
        form = StudentLoginForm()
    
    return render(request, 'student_portal/login.html', {'form': form})


def student_logout(request):
    """学生登出视图"""
    # 清理session中的学生信息
    if 'student_id' in request.session:
        del request.session['student_id']
    if 'student_name' in request.session:
        del request.session['student_name']
    if 'student_student_id' in request.session:
        del request.session['student_student_id']
    messages.success(request, '您已成功退出登录')
    return redirect('student_portal:login')


def dashboard(request):
    """学生仪表板"""
    try:
        student = Student.objects.get(id=request.session.get('student_id'))
    except (Student.DoesNotExist, TypeError):
        messages.error(request, '请重新登录')
        return redirect('student_portal:login')
    
    # 获取学生成绩统计
    scores = Score.objects.filter(student=student)
    avg_score = scores.aggregate(Avg('score'))['score__avg'] or 0
    total_courses = scores.count()
      # 获取最近成绩
    recent_scores = scores.order_by('-created_at')[:5]
    
    # 获取选课信息
    enrollments = Enrollment.objects.filter(student=student, status='enrolled')
    enrolled_courses_count = enrollments.count()
    
    # 获取通知
    notifications = StudentNotification.objects.filter(
        Q(student=student) | Q(student__isnull=True)
    ).order_by('-created_at')[:5]
    
    # 统计未读通知数量
    unread_notifications = StudentNotification.objects.filter(
        Q(student=student) | Q(student__isnull=True),
        is_read=False
    ).count()
    
    # 成绩分布统计
    grade_distribution = {
        'A': scores.filter(score__gte=90).count(),
        'B': scores.filter(score__gte=80, score__lt=90).count(),
        'C': scores.filter(score__gte=70, score__lt=80).count(),
        'D': scores.filter(score__gte=60, score__lt=70).count(),
        'F': scores.filter(score__lt=60).count(),
    }
    
    context = {
        'student': student,
        'avg_score': avg_score,
        'total_courses': total_courses,
        'enrolled_courses_count': enrolled_courses_count,
        'recent_scores': recent_scores,
        'notifications': notifications,
        'unread_notifications': unread_notifications,
        'grade_distribution': grade_distribution,
    }
    
    return render(request, 'student_portal/dashboard.html', context)


def my_grades(request):
    """我的成绩"""
    try:
        student = Student.objects.get(id=request.session.get('student_id'))
    except (Student.DoesNotExist, TypeError):
        messages.error(request, '请重新登录')
        return redirect('student_portal:login')
    
    # 获取成绩列表
    scores = Score.objects.filter(student=student).order_by('-semester', 'course__name')
      # 成绩搜索
    search_course = request.GET.get('course', '')
    search_semester = request.GET.get('semester', '')
    
    if search_course:
        scores = scores.filter(course__name__icontains=search_course)
    if search_semester:
        scores = scores.filter(semester__icontains=search_semester)
    
    # 分页
    paginator = Paginator(scores, 10)
    page_number = request.GET.get('page')
    page_scores = paginator.get_page(page_number)
    
    # 统计信息
    stats = {
        'total_courses': scores.count(),
        'avg_score': scores.aggregate(Avg('score'))['score__avg'] or 0,
        'max_score': scores.aggregate(Max('score'))['score__max'] or 0,
        'min_score': scores.aggregate(Min('score'))['score__min'] or 0,
    }
    
    context = {
        'student': student,
        'scores': page_scores,
        'stats': stats,
        'search_course': search_course,
        'search_semester': search_semester,
    }
    
    return render(request, 'student_portal/my_grades.html', context)


def course_selection(request):
    """选课页面"""
    try:
        student = Student.objects.get(id=request.session.get('student_id'))
    except (Student.DoesNotExist, TypeError):
        messages.error(request, '请重新登录')
        return redirect('student_portal:login')
    
    # 获取当前学期
    current_semester = "2025-1"  # 可以根据实际需求动态获取
    
    # 获取可选课程
    enrolled_courses = Enrollment.objects.filter(
        student=student, 
        status='enrolled',
        semester=current_semester
    ).values_list('course_id', flat=True)
    
    available_courses = Course.objects.filter(
        status='active'
    ).exclude(id__in=enrolled_courses)
    
    # 课程搜索和筛选
    search_name = request.GET.get('name', '')
    search_dept = request.GET.get('department', '')
    search_teacher = request.GET.get('teacher', '')
    
    if search_name:
        available_courses = available_courses.filter(name__icontains=search_name)
    if search_dept:
        available_courses = available_courses.filter(department_id=search_dept)
    if search_teacher:
        available_courses = available_courses.filter(teacher__icontains=search_teacher)
    
    # 分页
    paginator = Paginator(available_courses, 10)
    page_number = request.GET.get('page')
    page_courses = paginator.get_page(page_number)
    
    # 获取院系列表用于筛选
    departments = Department.objects.all()
    
    # 获取已选课程
    my_enrollments = Enrollment.objects.filter(
        student=student, 
        status='enrolled'
    ).select_related('course')
    
    context = {
        'student': student,
        'available_courses': page_courses,
        'my_enrollments': my_enrollments,
        'departments': departments,
        'current_semester': current_semester,
        'search_name': search_name,
        'search_dept': search_dept,
        'search_teacher': search_teacher,
    }
    
    return render(request, 'student_portal/course_selection.html', context)


def enroll_course(request, course_id):
    """选课操作"""
    try:
        student = Student.objects.get(id=request.session.get('student_id'))
        course = get_object_or_404(Course, id=course_id, status='active')
    except (Student.DoesNotExist, TypeError):
        messages.error(request, '请重新登录')
        return redirect('student_portal:login')
    
    current_semester = "2025-1"
    
    # 检查是否已经选过这门课
    existing_enrollment = Enrollment.objects.filter(
        student=student,
        course=course,
        semester=current_semester
    ).first()
    
    if existing_enrollment:
        if existing_enrollment.status == 'enrolled':
            messages.warning(request, '您已经选择了这门课程')
        elif existing_enrollment.status == 'dropped':
            # 重新选课
            existing_enrollment.status = 'enrolled'
            existing_enrollment.enrollment_date = timezone.now()
            existing_enrollment.save()
            messages.success(request, f'成功重新选择课程：{course.name}')
    else:
        # 检查课程容量
        current_enrollment_count = Enrollment.objects.filter(
            course=course,
            semester=current_semester,
            status='enrolled'
        ).count()
        
        if current_enrollment_count >= course.capacity:
            messages.error(request, '课程已满，无法选课')
        else:
            # 创建选课记录
            Enrollment.objects.create(
                student=student,
                course=course,
                semester=current_semester,
                status='enrolled'
            )
            messages.success(request, f'成功选择课程：{course.name}')
    
    return redirect('student_portal:course_selection')


def drop_course(request, enrollment_id):
    """退课操作"""
    try:
        student = Student.objects.get(id=request.session.get('student_id'))
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=student)
    except (Student.DoesNotExist, TypeError):
        messages.error(request, '请重新登录')
        return redirect('student_portal:login')
    
    enrollment.status = 'dropped'
    enrollment.save()
    messages.success(request, f'成功退选课程：{enrollment.course.name}')
    
    return redirect('student_portal:course_selection')


def my_schedule(request):
    """我的课程表"""
    try:
        student = Student.objects.get(id=request.session.get('student_id'))
    except (Student.DoesNotExist, TypeError):
        messages.error(request, '请重新登录')
        return redirect('student_portal:login')
    
    # 获取当前学期的选课记录
    current_semester = "2025-1"
    enrollments = Enrollment.objects.filter(
        student=student,
        semester=current_semester,
        status='enrolled'    ).select_related('course')
      # 整理课程表数据
    schedule_data = []
    for enrollment in enrollments:
        course = enrollment.course
        schedule_data.append({
            'course': course,
            'enrollment': enrollment,
            'time': course.class_time,
            'location': course.location,
            'teacher': course.teacher,
        })
    
    context = {
        'student': student,
        'schedule_data': schedule_data,
        'current_semester': current_semester,
    }
    
    return render(request, 'student_portal/schedule.html', context)


def profile(request):
    """个人信息"""
    try:
        student = Student.objects.get(id=request.session.get('student_id'))
    except (Student.DoesNotExist, TypeError):
        messages.error(request, '请重新登录')
        return redirect('student_portal:login')
    
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息更新成功')
            return redirect('student_portal:profile')
    else:
        form = StudentProfileForm(instance=student)
    
    # 获取学习统计
    scores = Score.objects.filter(student=student)
    enrollments = Enrollment.objects.filter(student=student, status='enrolled')
    
    stats = {
        'total_courses': scores.count(),
        'enrolled_courses': enrollments.count(),
        'avg_score': scores.aggregate(Avg('score'))['score__avg'] or 0,
        'major': student.major.name,
        'class_name': student.class_obj.name,
        'admission_date': student.admission_date,
    }
    
    context = {
        'student': student,
        'form': form,
        'stats': stats,
    }
    
    return render(request, 'student_portal/profile.html', context)


def notifications(request):
    """通知页面"""
    try:
        student = Student.objects.get(id=request.session.get('student_id'))
    except (Student.DoesNotExist, TypeError):
        messages.error(request, '请重新登录')
        return redirect('student_portal:login')
    
    # 获取通知列表
    notifications = StudentNotification.objects.filter(
        Q(student=student) | Q(student__isnull=True)
    ).order_by('-created_at')
    
    # 分页
    paginator = Paginator(notifications, 10)
    page_number = request.GET.get('page')
    page_notifications = paginator.get_page(page_number)
    
    context = {
        'student': student,
        'notifications': page_notifications,
    }
    
    return render(request, 'student_portal/notifications.html', context)


def mark_notification_read(request, notification_id):
    """标记通知为已读"""
    try:
        student = Student.objects.get(id=request.session.get('student_id'))
        notification = StudentNotification.objects.filter(
            Q(student=student) | Q(student__isnull=True),
            id=notification_id
        ).first()
        
        if notification:
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Notification not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def mark_notification_unread(request, notification_id):
    """将通知标记为未读"""
    student_id = request.session.get('student_id')
    if not student_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        notification = StudentNotification.objects.get(
            id=notification_id,
            student_id=student_id
        )
        notification.is_read = False
        notification.save()
        return JsonResponse({'success': True})
    except StudentNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def delete_notification(request, notification_id):
    """删除单个通知"""
    student_id = request.session.get('student_id')
    if not student_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        notification = StudentNotification.objects.get(
            id=notification_id,
            student_id=student_id
        )
        notification.delete()
        return JsonResponse({'success': True})
    except StudentNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """将所有通知标记为已读"""
    student_id = request.session.get('student_id')
    if not student_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        updated_count = StudentNotification.objects.filter(
            student_id=student_id,
            is_read=False
        ).update(is_read=True)
        return JsonResponse({'success': True, 'count': updated_count})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def mark_notifications_read(request):
    """批量将指定通知标记为已读"""
    student_id = request.session.get('student_id')
    if not student_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        notification_ids = json.loads(request.body).get('notification_ids', [])
        if not notification_ids:
            return JsonResponse({'success': False, 'error': 'No notifications specified'})
        
        updated_count = StudentNotification.objects.filter(
            id__in=notification_ids,
            student_id=student_id
        ).update(is_read=True)
        return JsonResponse({'success': True, 'count': updated_count})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def delete_notifications(request):
    """批量删除指定通知"""
    student_id = request.session.get('student_id')
    if not student_id:
        return JsonResponse({'success': False, 'error': 'Not authenticated'})
    
    try:
        notification_ids = json.loads(request.body).get('notification_ids', [])
        if not notification_ids:
            return JsonResponse({'success': False, 'error': 'No notifications specified'})
        
        deleted_count, _ = StudentNotification.objects.filter(
            id__in=notification_ids,
            student_id=student_id
        ).delete()
        return JsonResponse({'success': True, 'count': deleted_count})
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def change_password(request):
    """修改学生密码"""
    student_id = request.session.get('student_id')
    if not student_id:
        messages.error(request, '请先登录')
        return redirect('student_portal:login')
    
    try:
        student = Student.objects.get(id=student_id)
        
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # 验证当前密码
        if not check_password(old_password, student.password):
            messages.error(request, '当前密码不正确')
            return redirect('student_portal:profile')
        
        # 验证新密码
        if new_password1 != new_password2:
            messages.error(request, '两次输入的新密码不一致')
            return redirect('student_portal:profile')
        
        if len(new_password1) < 6:
            messages.error(request, '新密码长度至少6位')
            return redirect('student_portal:profile')
        
        # 更新密码
        student.password = make_password(new_password1)
        student.save()
        
        messages.success(request, '密码修改成功')
        return redirect('student_portal:profile')
        
    except Student.DoesNotExist:
        messages.error(request, '学生信息不存在')
        return redirect('student_portal:login')
    except Exception as e:
        messages.error(request, f'修改密码失败：{str(e)}')
        return redirect('student_portal:profile')
