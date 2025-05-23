# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import re
from users.models import User
from captcha.fields import CaptchaField


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
        max_length=100,
        required=True,
        label='电子邮箱'
    )
    agree_terms = forms.BooleanField(
        required=True,
        label='同意条款',
        error_messages={'required': '必须同意服务条款才能注册'}
    )
    subscribe_newsletter = forms.BooleanField(
        required=False,
        label='订阅新闻邮件'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
        labels = {
            'username': '用户名',
            'first_name': '名',
            'last_name': '姓',
        }
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'username'}),
        }

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("用户名只能包含字母、数字和 @/./+/-/_")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("该用户名已被注册")
        return username.lower()  # 统一转为小写

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("请输入有效的邮箱地址")

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("该邮箱已被注册")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 8:
            raise ValidationError("密码至少需要8个字符")
        if not any(char.isupper() for char in password):
            raise ValidationError("密码至少包含一个大写字母")
        if not any(char.isdigit() for char in password):
            raise ValidationError("密码至少包含一个数字")
        if not any(not char.isalnum() for char in password):
            raise ValidationError("密码至少包含一个特殊字符")
        return password


class LoginForm(forms.Form):
    """登录表单，包含验证码"""
    username = forms.CharField(
        label='用户名',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    password = forms.CharField(
        label='密码',
        max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )
    captcha = CaptchaField(
        label='验证码',
        error_messages={'invalid': '验证码错误'}
    )
    remember_me = forms.BooleanField(
        label='记住我',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    cookie_consent = forms.ChoiceField(
        label='Cookie设置',
        required=False,
        initial='necessary',
        choices=[
            ('none', '无同意'),
            ('necessary', '仅必要Cookie'),
            ('all', '所有Cookie'),
        ],
        widget=forms.HiddenInput()
    )


class RegisterForm(forms.Form):
    """注册表单，包含验证码"""
    username = forms.CharField(
        label='用户名',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名'})
    )
    email = forms.EmailField(
        label='电子邮箱',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入电子邮箱'})
    )
    first_name = forms.CharField(
        label='名',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入名'})
    )
    last_name = forms.CharField(
        label='姓',
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入姓'})
    )
    password = forms.CharField(
        label='密码',
        max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'})
    )
    confirm_password = forms.CharField(
        label='确认密码',
        max_length=128,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请再次输入密码'})
    )
    captcha = CaptchaField(
        label='验证码',
        error_messages={'invalid': '验证码错误'}
    )
    agree_terms = forms.BooleanField(
        label='同意服务条款',
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    subscribe_newsletter = forms.BooleanField(
        label='订阅通讯',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    cookie_consent = forms.ChoiceField(
        label='Cookie设置',
        required=False,
        initial='necessary',
        choices=[
            ('none', '无同意'),
            ('necessary', '仅必要Cookie'),
            ('all', '所有Cookie'),
        ],
        widget=forms.HiddenInput()
    )
