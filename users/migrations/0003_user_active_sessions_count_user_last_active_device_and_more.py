# Generated by Django 5.2 on 2025-05-07 17:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_account_locked_until_user_cookie_consent_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='active_sessions_count',
            field=models.PositiveIntegerField(default=0, verbose_name='活跃会话数'),
        ),
        migrations.AddField(
            model_name='user',
            name='last_active_device',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='最后活跃设备'),
        ),
        migrations.AddField(
            model_name='user',
            name='last_session_refresh',
            field=models.DateTimeField(blank=True, null=True, verbose_name='上次会话刷新时间'),
        ),
        migrations.AddField(
            model_name='user',
            name='login_days_count',
            field=models.PositiveIntegerField(default=0, verbose_name='累计登录天数'),
        ),
        migrations.CreateModel(
            name='UserLoginStats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_logins', models.PositiveIntegerField(default=0, verbose_name='总登录次数')),
                ('weekly_logins', models.JSONField(default=dict, verbose_name='每周登录统计')),
                ('monthly_logins', models.JSONField(default=dict, verbose_name='每月登录统计')),
                ('login_times', models.JSONField(default=dict, verbose_name='登录时间分布')),
                ('device_stats', models.JSONField(default=dict, verbose_name='设备统计')),
                ('browser_stats', models.JSONField(default=dict, verbose_name='浏览器统计')),
                ('last_updated', models.DateTimeField(auto_now=True, verbose_name='最后更新')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='login_stats', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '登录统计',
                'verbose_name_plural': '登录统计',
            },
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=40, verbose_name='会话密钥')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP地址')),
                ('user_agent', models.TextField(blank=True, verbose_name='用户代理')),
                ('device_type', models.CharField(blank=True, max_length=50, verbose_name='设备类型')),
                ('browser', models.CharField(blank=True, max_length=50, verbose_name='浏览器')),
                ('location', models.CharField(blank=True, max_length=100, verbose_name='地理位置')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('last_activity', models.DateTimeField(auto_now=True, verbose_name='最后活动')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否活跃')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '用户会话',
                'verbose_name_plural': '用户会话',
            },
        ),
    ]
