from django.contrib import admin
from .models import Major, Class, Student

# Register your models here.

@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('created_at',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'major', 'admission_year', 'created_at')
    search_fields = ('name', 'code')
    list_filter = ('major', 'admission_year', 'created_at')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'gender', 'class_obj', 'major', 'status', 'admission_date')
    search_fields = ('student_id', 'name', 'email', 'phone')
    list_filter = ('gender', 'status', 'class_obj', 'major', 'admission_date')
    date_hierarchy = 'admission_date'
