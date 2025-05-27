from django.urls import path
from . import views

app_name = 'student_portal'

urlpatterns = [
    # 认证相关
    path('', views.student_login, name='login'),
    path('login/', views.student_login, name='login'),
    path('logout/', views.student_logout, name='logout'),
    
    # 主要功能页面
    path('dashboard/', views.dashboard, name='dashboard'),
    path('grades/', views.my_grades, name='my_grades'),
    path('courses/', views.course_selection, name='course_selection'),
    path('schedule/', views.my_schedule, name='my_schedule'),    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('notifications/', views.notifications, name='notifications'),
      # 操作功能
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('drop/<int:enrollment_id>/', views.drop_course, name='drop_course'),
    
    # 通知相关操作
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notification/<int:notification_id>/unread/', views.mark_notification_unread, name='mark_notification_unread'),
    path('notification/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/mark-read/', views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/delete/', views.delete_notifications, name='delete_notifications'),
]
