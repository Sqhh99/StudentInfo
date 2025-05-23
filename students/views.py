from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Avg, Max, Min, Count
from django.http import JsonResponse, HttpResponse
import json
import csv

from users.models import User
from .models import Student, Class, Major, Department, Course, Score
from .forms import StudentForm, StudentSearchForm, MajorForm, ClassForm, DepartmentForm, CourseForm, CourseSearchForm, ScoreForm, ScoreSearchForm


def index(request):
    # 获取统计数据
    student_count = Student.objects.count()
    class_count = Class.objects.count()
    course_count = Course.objects.count()
    score_count = Score.objects.count()
    
    # 按专业统计学生数量，而不是按班级，以减少图表杂乱
    majors = Major.objects.all()
    major_student_counts = []
    for major in majors:
        major_student_count = Student.objects.filter(major=major).count()
        if major_student_count > 0:  # 只添加有学生的专业
            major_student_counts.append({
                'name': major.name,
                'value': major_student_count
            })
    
    # 获取最近添加的10名学生
    recent_students = Student.objects.all().order_by('-id')[:10]
    
    # 计算各专业各等级成绩数量
    # 计算机科学专业
    cs_scores = Score.objects.filter(student__major__name='计算机科学与技术')
    excellent_cs = cs_scores.filter(score__gte=90).count()
    good_cs = cs_scores.filter(score__gte=80, score__lt=90).count()
    pass_cs = cs_scores.filter(score__gte=60, score__lt=80).count()
    fail_cs = cs_scores.filter(score__lt=60).count()
    
    # 软件工程专业
    se_scores = Score.objects.filter(student__major__name='软件工程')
    excellent_se = se_scores.filter(score__gte=90).count()
    good_se = se_scores.filter(score__gte=80, score__lt=90).count()
    pass_se = se_scores.filter(score__gte=60, score__lt=80).count()
    fail_se = se_scores.filter(score__lt=60).count()
    
    # 数据科学专业
    ds_scores = Score.objects.filter(student__major__name='数据科学')
    excellent_ds = ds_scores.filter(score__gte=90).count()
    good_ds = ds_scores.filter(score__gte=80, score__lt=90).count()
    pass_ds = ds_scores.filter(score__gte=60, score__lt=80).count()
    fail_ds = ds_scores.filter(score__lt=60).count()
    
    # 人工智能专业
    ai_scores = Score.objects.filter(student__major__name='人工智能')
    excellent_ai = ai_scores.filter(score__gte=90).count()
    good_ai = ai_scores.filter(score__gte=80, score__lt=90).count()
    pass_ai = ai_scores.filter(score__gte=60, score__lt=80).count()
    fail_ai = ai_scores.filter(score__lt=60).count()
    
    # 网络工程专业
    ne_scores = Score.objects.filter(student__major__name='网络工程')
    excellent_ne = ne_scores.filter(score__gte=90).count()
    good_ne = ne_scores.filter(score__gte=80, score__lt=90).count()
    pass_ne = ne_scores.filter(score__gte=60, score__lt=80).count()
    fail_ne = ne_scores.filter(score__lt=60).count()
    
    context = {
        "active_tab": "index",
        "student_count": student_count,
        "class_count": class_count, 
        "course_count": course_count,
        "score_count": score_count,
        "major_student_counts": major_student_counts,  # 使用专业学生数量数据
        "recent_students": recent_students,
        # 各专业成绩等级分布
        "excellent_cs": excellent_cs,
        "good_cs": good_cs,
        "pass_cs": pass_cs,
        "fail_cs": fail_cs,
        "excellent_se": excellent_se,
        "good_se": good_se,
        "pass_se": pass_se,
        "fail_se": fail_se,
        "excellent_ds": excellent_ds,
        "good_ds": good_ds,
        "pass_ds": pass_ds,
        "fail_ds": fail_ds,
        "excellent_ai": excellent_ai,
        "good_ai": good_ai,
        "pass_ai": pass_ai,
        "fail_ai": fail_ai,
        "excellent_ne": excellent_ne,
        "good_ne": good_ne,
        "pass_ne": pass_ne,
        "fail_ne": fail_ne
    }
    return render(request, 'students/by_base_page/index_by_base.html', context)


def about(request):
    return render(request, 'students/by_base_page/about_by_base.html', {"active_tab": "about"})


@login_required
def students(request):
    # 获取所有班级，用于搜索表单
    classes = Class.objects.all()
    
    # 获取所有专业，用于添加学生表单
    majors = Major.objects.all()
    
    # 创建并处理搜索表单
    form = StudentSearchForm(request.GET)
    
    # 获取所有学生数据
    students_list = Student.objects.all()
    
    # 应用搜索过滤
    if form.is_valid():
        student_id = form.cleaned_data.get('student_id')
        name = form.cleaned_data.get('name')
        class_obj = form.cleaned_data.get('class_obj')
        status = form.cleaned_data.get('status')
        
        if student_id:
            students_list = students_list.filter(student_id__icontains=student_id)
        if name:
            students_list = students_list.filter(name__icontains=name)
        if class_obj:
            students_list = students_list.filter(class_obj=class_obj)
        if status:
            students_list = students_list.filter(status=status)
    
    context = {
        "active_tab": "students",
        "students": students_list,
        "classes": classes,
        "majors": majors,
        "form": form
    }
    return render(request, 'students/by_base_page/student_by_base.html', context)


@login_required
def query_results(request):
    """成绩查询视图"""
    # 获取所有成绩数据
    scores = Score.objects.all().select_related('student', 'course', 'course__department')
    
    # 创建搜索表单
    form = ScoreSearchForm(request.GET)
    
    # 应用搜索过滤
    if form.is_valid():
        student_id = form.cleaned_data.get('student_id')
        student_name = form.cleaned_data.get('student_name')
        course_code = form.cleaned_data.get('course_code')
        course_name = form.cleaned_data.get('course_name')
        semester = form.cleaned_data.get('semester')
        score_min = form.cleaned_data.get('score_min')
        score_max = form.cleaned_data.get('score_max')
        grade = form.cleaned_data.get('grade')
        
        if student_id:
            scores = scores.filter(student__student_id__icontains=student_id)
        if student_name:
            scores = scores.filter(student__name__icontains=student_name)
        if course_code:
            scores = scores.filter(course__code__icontains=course_code)
        if course_name:
            scores = scores.filter(course__name__icontains=course_name)
        if semester:
            scores = scores.filter(semester__icontains=semester)
        if score_min is not None:
            scores = scores.filter(score__gte=score_min)
        if score_max is not None:
            scores = scores.filter(score__lte=score_max)
        if grade:
            scores = scores.filter(grade=grade)
    
    # 获取统计信息
    stats = {}
    if scores.exists():
        stats = {
            'avg_score': scores.aggregate(Avg('score'))['score__avg'],
            'max_score': scores.aggregate(Max('score'))['score__max'],
            'min_score': scores.aggregate(Min('score'))['score__min'],
            'count': scores.count(),
            'pass_rate': scores.filter(score__gte=60).count() / scores.count() * 100 if scores.count() > 0 else 0
        }
    
    # 获取成绩分布
    grade_distribution = {}
    for grade, _ in Score.GRADE_CHOICES:
        grade_distribution[grade] = scores.filter(grade=grade).count()
    
    # 计算分数段统计，用于ECharts图表
    fail_score_count = scores.filter(score__lt=60).count()
    pass_score_count = scores.filter(score__gte=60, score__lt=70).count()
    good_score_count = scores.filter(score__gte=70, score__lt=80).count()
    better_score_count = scores.filter(score__gte=80, score__lt=90).count()
    excellent_score_count = scores.filter(score__gte=90).count()
    
    # 计算更详细的分数段分布
    score_range_0_10 = scores.filter(score__lt=10).count()
    score_range_11_20 = scores.filter(score__gte=11, score__lt=20).count()
    score_range_21_30 = scores.filter(score__gte=21, score__lt=30).count()
    score_range_31_40 = scores.filter(score__gte=31, score__lt=40).count()
    score_range_41_50 = scores.filter(score__gte=41, score__lt=50).count()
    score_range_51_60 = scores.filter(score__gte=51, score__lt=60).count()
    score_range_61_70 = scores.filter(score__gte=61, score__lt=70).count()
    score_range_71_80 = scores.filter(score__gte=71, score__lt=80).count()
    score_range_81_90 = scores.filter(score__gte=81, score__lt=90).count()
    score_range_91_100 = scores.filter(score__gte=91).count()
    
    context = {
        "active_tab": "query_results",
        "scores": scores,
        "form": form,
        "stats": stats,
        "grade_distribution": grade_distribution,
        # 添加分数段统计数据
        "fail_score_count": fail_score_count,
        "pass_score_count": pass_score_count,
        "good_score_count": good_score_count,
        "better_score_count": better_score_count,
        "excellent_score_count": excellent_score_count,
        # 详细分数段分布
        "score_range_0_10": score_range_0_10,
        "score_range_11_20": score_range_11_20,
        "score_range_21_30": score_range_21_30,
        "score_range_31_40": score_range_31_40,
        "score_range_41_50": score_range_41_50,
        "score_range_51_60": score_range_51_60,
        "score_range_61_70": score_range_61_70,
        "score_range_71_80": score_range_71_80,
        "score_range_81_90": score_range_81_90,
        "score_range_91_100": score_range_91_100
    }
    
    return render(request, 'students/by_base_page/query_results_by_base.html', context)


@login_required
def course_management(request):
    # 获取所有院系，用于搜索表单
    departments = Department.objects.all()
    
    # 创建并处理搜索表单
    form = CourseSearchForm(request.GET)
    
    # 获取所有课程数据
    courses_list = Course.objects.all()
    
    # 应用搜索过滤
    if form.is_valid():
        code = form.cleaned_data.get('code')
        name = form.cleaned_data.get('name')
        teacher = form.cleaned_data.get('teacher')
        department = form.cleaned_data.get('department')
        credit = form.cleaned_data.get('credit')
        semester = form.cleaned_data.get('semester')
        status = form.cleaned_data.get('status')
        
        if code:
            courses_list = courses_list.filter(code__icontains=code)
        if name:
            courses_list = courses_list.filter(name__icontains=name)
        if teacher:
            courses_list = courses_list.filter(teacher__icontains=teacher)
        if department:
            courses_list = courses_list.filter(department=department)
        if credit:
            if credit == '5':
                courses_list = courses_list.filter(credit__gte=5)
            else:
                courses_list = courses_list.filter(credit=credit)
        if semester:
            courses_list = courses_list.filter(semester__icontains=semester)
        if status:
            courses_list = courses_list.filter(status=status)
    
    context = {
        "active_tab": "course_management",
        "courses": courses_list,
        "departments": departments,
        "form": form,
        "course_count": courses_list.count()
    }
    return render(request, 'students/by_base_page/course_management_by_base.html', context)


@login_required
def profile_view(request):
    # 获取统计数据
    students_count = Student.objects.count()
    courses_count = Course.objects.count()
    scores_count = Score.objects.count()
    
    # 获取用户IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        user_ip = x_forwarded_for.split(',')[0]
    else:
        user_ip = request.META.get('REMOTE_ADDR', '')
    
    # 上下文数据
    context = {
        'active_tab': 'profile',
        'students_count': students_count,
        'courses_count': courses_count,
        'scores_count': scores_count,
        'login_days': 1,  # 示例数据，实际项目中可以根据登录记录计算
        'user_ip': user_ip
    }
    
    return render(request, 'students/profile.html', context)


# 用户资料更新视图
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm


@login_required
def update_profile(request):
    if request.method == 'POST':
        # 获取表单数据
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        # 验证邮箱是否已被其他用户使用
        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, '该邮箱已被其他用户使用')
            return redirect('profile')

        # 更新用户信息
        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, '个人信息已成功更新')
        return redirect('profile')

    return redirect('profile')


@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # 验证当前密码
        if not request.user.check_password(current_password):
            messages.error(request, '当前密码不正确')
            return redirect('profile')

        # 验证新密码与确认密码是否一致
        if new_password != confirm_password:
            messages.error(request, '新密码与确认密码不匹配')
            return redirect('profile')

        # 验证密码复杂性
        try:
            validate_password(new_password)
        except ValidationError as e:
            messages.error(request, e.messages[0])
            return redirect('profile')

        # 更新密码
        user = request.user
        user.set_password(new_password)
        user.save()

        # 更新会话，防止用户被登出
        update_session_auth_hash(request, user)

        messages.success(request, '密码已成功更改')
        return redirect('profile')

    return redirect('profile')


# 学生管理相关视图
@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '学生信息添加成功')
            return redirect('students')
        else:
            # 表单验证失败，将错误信息返回给模态框
            messages.error(request, '表单验证失败，请检查输入')
    else:
        form = StudentForm()
    
    # 无论POST还是GET请求，都重定向回学生列表页面
    # 因为添加学生功能是在模态框中实现的
    return redirect('students')


@login_required
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, '学生信息更新成功')
            return redirect('students')
        else:
            messages.error(request, '表单验证失败，请检查输入')
    else:
        form = StudentForm(instance=student)
    
    context = {
        'form': form,
        'student': student
    }
    return render(request, 'students/student_form.html', context)


@login_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == 'POST':
        student.delete()
        messages.success(request, '学生信息删除成功')
        return redirect('students')
    
    context = {
        'student': student
    }
    return render(request, 'students/student_confirm_delete.html', context)


@login_required
def student_detail(request, pk):
    """
    学生详情页面
    """
    student = get_object_or_404(Student, pk=pk)
    student_scores = Score.objects.filter(student=student).order_by('-semester', 'course__name')
    
    # 学生成绩统计信息
    student_stats = {}
    if student_scores.exists():
        student_stats = {
            'avg_score': student_scores.aggregate(Avg('score'))['score__avg'],
            'max_score': student_scores.aggregate(Max('score'))['score__max'],
            'min_score': student_scores.aggregate(Min('score'))['score__min'],
            'course_count': student_scores.count()
        }
    else:
        student_stats = {
            'avg_score': 0,
            'max_score': 0,
            'min_score': 0,
            'course_count': 0
        }
    
    # 学生成绩等级分布
    excellent_count = student_scores.filter(score__gte=90).count()
    good_count = student_scores.filter(score__gte=80, score__lt=90).count()
    fair_count = student_scores.filter(score__gte=70, score__lt=80).count()
    pass_count = student_scores.filter(score__gte=60, score__lt=70).count()
    fail_count = student_scores.filter(score__lt=60).count()
    
    context = {
        "active_tab": "students",
        "student": student,
        "student_scores": student_scores,
        "student_stats": student_stats,
        "excellent_count": excellent_count,
        "good_count": good_count,
        "fair_count": fair_count,
        "pass_count": pass_count,
        "fail_count": fail_count
    }
    
    return render(request, 'students/by_base_page/student_detail_by_base.html', context)


# 课程管理相关视图
@login_required
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '课程信息添加成功')
            return redirect('course_management')
        else:
            # 表单验证失败，将错误信息返回给模态框
            messages.error(request, '表单验证失败，请检查输入')
    else:
        form = CourseForm()
    
    # 无论POST还是GET请求，都重定向回课程列表页面
    # 因为添加课程功能是在模态框中实现的
    return redirect('course_management')


@login_required
def edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, '课程信息更新成功')
            return redirect('course_management')
        else:
            messages.error(request, '表单验证失败，请检查输入')
    else:
        form = CourseForm(instance=course)
    
    context = {
        'form': form,
        'course': course
    }
    return render(request, 'students/course_form.html', context)


@login_required
def delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, '课程信息删除成功')
        return redirect('course_management')
    
    context = {
        'course': course
    }
    return render(request, 'students/course_confirm_delete.html', context)


@login_required
def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    context = {
        'course': course
    }
    return render(request, 'students/course_detail.html', context)


# AJAX 请求处理视图
@login_required
def get_class_by_major(request):
    major_id = request.GET.get('major_id')
    classes = Class.objects.filter(major_id=major_id).values('id', 'name')
    return JsonResponse(list(classes), safe=False)


@login_required
def export_students_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="students.csv"'
    
    # 创建CSV写入器
    writer = csv.writer(response)
    
    # 写入标题行
    writer.writerow(['学号', '姓名', '性别', '班级', '专业', '入学时间', '联系电话', '电子邮箱', '状态'])
    
    # 获取学生数据，可以应用与学生列表页面相同的筛选
    students = Student.objects.all()
    form = StudentSearchForm(request.GET)
    
    # 应用搜索过滤
    if form.is_valid():
        student_id = form.cleaned_data.get('student_id')
        name = form.cleaned_data.get('name')
        class_obj = form.cleaned_data.get('class_obj')
        status = form.cleaned_data.get('status')
        
        if student_id:
            students = students.filter(student_id__icontains=student_id)
        if name:
            students = students.filter(name__icontains=name)
        if class_obj:
            students = students.filter(class_obj=class_obj)
        if status:
            students = students.filter(status=status)
    
    # 写入每个学生的数据行
    for student in students:
        writer.writerow([
            student.student_id,
            student.name,
            student.get_gender_display(),
            student.class_obj.name,
            student.major.name,
            student.admission_date.strftime('%Y-%m-%d'),
            student.phone or '',
            student.email or '',
            student.get_status_display()
        ])
    
    return response


@login_required
def export_courses_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="courses.csv"'
    
    # 创建CSV写入器
    writer = csv.writer(response)
    
    # 写入标题行
    writer.writerow(['课程编号', '课程名称', '学分', '任课教师', '开课学期', '上课时间', '上课地点', '所属院系', '课程容量', '课程状态'])
    
    # 获取课程数据，可以应用与课程列表页面相同的筛选
    courses = Course.objects.all()
    form = CourseSearchForm(request.GET)
    
    # 应用搜索过滤
    if form.is_valid():
        code = form.cleaned_data.get('code')
        name = form.cleaned_data.get('name')
        teacher = form.cleaned_data.get('teacher')
        department = form.cleaned_data.get('department')
        credit = form.cleaned_data.get('credit')
        semester = form.cleaned_data.get('semester')
        status = form.cleaned_data.get('status')
        
        if code:
            courses = courses.filter(code__icontains=code)
        if name:
            courses = courses.filter(name__icontains=name)
        if teacher:
            courses = courses.filter(teacher__icontains=teacher)
        if department:
            courses = courses.filter(department=department)
        if credit:
            if credit == '5':
                courses = courses.filter(credit__gte=5)
            else:
                courses = courses.filter(credit=credit)
        if semester:
            courses = courses.filter(semester__icontains=semester)
        if status:
            courses = courses.filter(status=status)
    
    # 写入每个课程的数据行
    for course in courses:
        writer.writerow([
            course.code,
            course.name,
            course.credit,
            course.teacher,
            course.semester,
            course.class_time,
            course.location,
            course.department.name,
            course.capacity,
            course.get_status_display()
        ])
    
    return response


@login_required
def add_score(request):
    """添加成绩视图"""
    if request.method == 'POST':
        form = ScoreForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '成绩添加成功')
            return redirect('query_results')
        else:
            messages.error(request, '表单验证失败，请检查输入')
    else:
        form = ScoreForm()
    
    # 无论POST还是GET请求，都重定向回成绩列表页面
    # 因为添加成绩功能是在模态框中实现的
    return redirect('query_results')


@login_required
def edit_score(request, pk):
    """编辑成绩视图"""
    score = get_object_or_404(Score, pk=pk)
    
    if request.method == 'POST':
        form = ScoreForm(request.POST, instance=score)
        if form.is_valid():
            form.save()
            messages.success(request, '成绩更新成功')
            return redirect('query_results')
        else:
            messages.error(request, '表单验证失败，请检查输入')
    else:
        form = ScoreForm(instance=score)
    
    context = {
        'form': form,
        'score': score
    }
    return render(request, 'students/score_form.html', context)


@login_required
def delete_score(request, pk):
    """删除成绩视图"""
    score = get_object_or_404(Score, pk=pk)
    
    if request.method == 'POST':
        score.delete()
        messages.success(request, '成绩删除成功')
        return redirect('query_results')
    
    context = {
        'score': score
    }
    return render(request, 'students/score_confirm_delete.html', context)


@login_required
def export_scores_csv(request):
    """导出成绩CSV文件"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="scores.csv"'
    
    # 创建CSV写入器
    writer = csv.writer(response)
    
    # 写入标题行
    writer.writerow(['学号', '学生姓名', '课程编号', '课程名称', '分数', '等级', '学期', '评语'])
    
    # 获取成绩数据，可以应用与成绩列表页面相同的筛选
    scores = Score.objects.all().select_related('student', 'course')
    form = ScoreSearchForm(request.GET)
    
    # 应用搜索过滤
    if form.is_valid():
        student_id = form.cleaned_data.get('student_id')
        student_name = form.cleaned_data.get('student_name')
        course_code = form.cleaned_data.get('course_code')
        course_name = form.cleaned_data.get('course_name')
        semester = form.cleaned_data.get('semester')
        score_min = form.cleaned_data.get('score_min')
        score_max = form.cleaned_data.get('score_max')
        grade = form.cleaned_data.get('grade')
        
        if student_id:
            scores = scores.filter(student__student_id__icontains=student_id)
        if student_name:
            scores = scores.filter(student__name__icontains=student_name)
        if course_code:
            scores = scores.filter(course__code__icontains=course_code)
        if course_name:
            scores = scores.filter(course__name__icontains=course_name)
        if semester:
            scores = scores.filter(semester__icontains=semester)
        if score_min is not None:
            scores = scores.filter(score__gte=score_min)
        if score_max is not None:
            scores = scores.filter(score__lte=score_max)
        if grade:
            scores = scores.filter(grade=grade)
    
    # 写入每个成绩的数据行
    for score in scores:
        writer.writerow([
            score.student.student_id,
            score.student.name,
            score.course.code,
            score.course.name,
            score.score,
            score.grade,
            score.semester,
            score.comment or ''
        ])
    
    return response


# 添加未授权访问视图
def unauthorized_access(request):
    """
    处理未授权访问的视图，显示一条消息并提供登录链接
    """
    return render(request, 'students/unauthorized.html')