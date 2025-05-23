# students/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    
    # 会话管理URL
    path('sessions/', views.session_management, name='session_management'),
    path('sessions/terminate-all/', views.terminate_all_sessions, name='terminate_all_sessions'),
    path('sessions/refresh/', views.refresh_current_session, name='refresh_current_session'),
    path('sessions/activity-log/', views.session_activity_log, name='session_activity_log'),
    path('sessions/clear-data/', views.clear_session_data, name='clear_session_data'),
]