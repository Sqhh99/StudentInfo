from django import forms
from .models import Student, Class, Major, Course, Department, Score


class StudentSearchForm(forms.Form):
    """学生搜索表单"""
    student_id = forms.CharField(required=False, label='学号', 
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入学号'}))
    name = forms.CharField(required=False, label='姓名', 
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入姓名'}))
    class_obj = forms.ModelChoiceField(required=False, label='班级', queryset=Class.objects.all(),
                                     widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.ChoiceField(required=False, label='状态', 
                              choices=[('', '所有状态')] + list(Student.STATUS_CHOICES),
                              widget=forms.Select(attrs={'class': 'form-select'}))


class StudentForm(forms.ModelForm):
    """学生表单"""
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'gender', 'class_obj', 'major', 'admission_date', 
                 'phone', 'email', 'status', 'profile_image']
        widgets = {
            'student_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'class_obj': forms.Select(attrs={'class': 'form-select'}),
            'major': forms.Select(attrs={'class': 'form-select'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 当选择班级时自动选择相应的专业
        if 'class_obj' in self.data:
            try:
                class_id = int(self.data.get('class_obj'))
                class_obj = Class.objects.get(id=class_id)
                self.fields['major'].initial = class_obj.major
            except (ValueError, Class.DoesNotExist):
                pass


class MajorForm(forms.ModelForm):
    """专业表单"""
    class Meta:
        model = Major
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ClassForm(forms.ModelForm):
    """班级表单"""
    class Meta:
        model = Class
        fields = ['name', 'code', 'major', 'admission_year']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'major': forms.Select(attrs={'class': 'form-select'}),
            'admission_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '2000', 'max': '2100'}),
        }


class DepartmentForm(forms.ModelForm):
    """院系表单"""
    class Meta:
        model = Department
        fields = ['name', 'code', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CourseForm(forms.ModelForm):
    """课程表单"""
    class Meta:
        model = Course
        fields = ['code', 'name', 'credit', 'teacher', 'description', 'department', 
                 'class_time', 'location', 'capacity', 'semester', 'status']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'credit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0.5', 'max': '10'}),
            'teacher': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'class_time': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '1000'}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class CourseSearchForm(forms.Form):
    """课程搜索表单"""
    code = forms.CharField(required=False, label='课程编号',
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '输入课程编号'}))
    name = forms.CharField(required=False, label='课程名称',
                          widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '输入课程名称'}))
    teacher = forms.CharField(required=False, label='任课教师',
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '输入教师姓名'}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, label='所属院系',
                                       widget=forms.Select(attrs={'class': 'form-select'}))
    credit = forms.ChoiceField(
        choices=(
            ('', '全部学分'),
            ('1', '1学分'),
            ('2', '2学分'),
            ('3', '3学分'),
            ('4', '4学分'),
            ('5', '5学分及以上'),
        ),
        required=False,
        label='学分',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    semester = forms.CharField(required=False, label='开课学期',
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '如：2025-1'}))
    status = forms.ChoiceField(
        choices=(('', '全部状态'),) + Course.STATUS_CHOICES,
        required=False,
        label='课程状态',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class ScoreForm(forms.ModelForm):
    """成绩表单"""
    class Meta:
        model = Score
        fields = ['student', 'course', 'score', 'semester', 'comment']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'score': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'step': '0.1'}),
            'semester': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '如：2025-1'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'}),
        }


class ScoreSearchForm(forms.Form):
    """成绩搜索表单"""
    student_id = forms.CharField(required=False, label='学号',
                                widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入学号'}))
    student_name = forms.CharField(required=False, label='学生姓名',
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入学生姓名'}))
    course_code = forms.CharField(required=False, label='课程编号',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入课程编号'}))
    course_name = forms.CharField(required=False, label='课程名称',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入课程名称'}))
    semester = forms.CharField(required=False, label='学期',
                              widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '如：2025-1'}))
    score_min = forms.DecimalField(required=False, label='最低分数',
                                   widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}))
    score_max = forms.DecimalField(required=False, label='最高分数',
                                   widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}))
    grade = forms.ChoiceField(required=False, label='等级',
                             choices=[('', '所有等级')] + list(Score.GRADE_CHOICES),
                             widget=forms.Select(attrs={'class': 'form-select'})) 