# students/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('students/', views.students, name='students'),
    path('about/', views.about, name='about'),
    path('query_results/', views.query_results, name='query_results'),
    path('course_management/', views.course_management, name='course_management'),
    path('unauthorized/', views.unauthorized_access, name='unauthorized_access'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # 学生管理相关路由
    path('students/add/', views.add_student, name='add_student'),
    path('students/<int:pk>/edit/', views.edit_student, name='edit_student'),
    path('students/<int:pk>/delete/', views.delete_student, name='delete_student'),
    path('students/<int:pk>/detail/', views.student_detail, name='student_detail'),
    
    # 课程管理相关路由
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/<int:pk>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:pk>/delete/', views.delete_course, name='delete_course'),
    path('courses/<int:pk>/detail/', views.course_detail, name='course_detail'),
    
    # 成绩管理相关路由
    path('scores/add/', views.add_score, name='add_score'),
    path('scores/<int:pk>/edit/', views.edit_score, name='edit_score'),
    path('scores/<int:pk>/delete/', views.delete_score, name='delete_score'),
    
    # AJAX 请求处理路由
    path('get-class-by-major/', views.get_class_by_major, name='get_class_by_major'),
    path('export-students-csv/', views.export_students_csv, name='export_students_csv'),
    path('export-courses-csv/', views.export_courses_csv, name='export_courses_csv'),
    path('export-scores-csv/', views.export_scores_csv, name='export_scores_csv'),
]