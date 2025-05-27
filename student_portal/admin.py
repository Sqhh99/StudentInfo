from django.contrib import admin
from .models import Enrollment, StudentNotification

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'semester', 'enrollment_date')
    list_filter = ('status', 'semester', 'enrollment_date')
    search_fields = ('student__name', 'student__student_id', 'course__name', 'course__code')

@admin.register(StudentNotification)
class StudentNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'student', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'content', 'student__name')
