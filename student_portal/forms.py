from django import forms
from django.contrib.auth.forms import AuthenticationForm
from students.models import Student, Course
from .models import Enrollment


class StudentLoginForm(forms.Form):
    """学生登录表单"""
    username = forms.CharField(
        label='学号',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入学号'
        })
    )
    password = forms.CharField(
        label='密码',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
    )

    def clean(self):
        """验证学生登录信息"""
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            try:
                student = Student.objects.get(student_id=username)
                if not student.check_password(password):
                    raise forms.ValidationError('密码错误')
                cleaned_data['student'] = student
            except Student.DoesNotExist:
                raise forms.ValidationError('学号不存在')
        
        return cleaned_data


class StudentProfileForm(forms.ModelForm):
    """学生个人信息表单"""
    class Meta:
        model = Student
        fields = ['name', 'phone', 'email', 'profile_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'readonly': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CourseEnrollmentForm(forms.ModelForm):
    """选课表单"""
    class Meta:
        model = Enrollment
        fields = ['course', 'semester']
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'}),
            'semester': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '如：2025-1'}),
        }

    def __init__(self, *args, **kwargs):
        student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)
        
        if student:
            # 获取可选课程（排除已选课程）
            enrolled_courses = Enrollment.objects.filter(
                student=student, 
                status='enrolled'
            ).values_list('course_id', flat=True)
            
            self.fields['course'].queryset = Course.objects.filter(
                status='active'
            ).exclude(id__in=enrolled_courses)
