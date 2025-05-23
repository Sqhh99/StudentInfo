from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
import logging
import redis
import time

logger = logging.getLogger('auth')

class Command(BaseCommand):
    help = '清理过期的会话数据，包括数据库会话和Redis缓存会话'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force-redis-cleanup',
            action='store_true',
            dest='force_redis_cleanup',
            help='强制清理Redis中所有会话数据',
        )
        
        parser.add_argument(
            '--inactive-days',
            action='store',
            dest='inactive_days',
            default=7,
            type=int,
            help='清理指定天数内未活动的会话（即使尚未过期）',
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            help='只显示将要清理的会话，不实际删除',
        )
    
    def handle(self, *args, **options):
        force_redis_cleanup = options['force_redis_cleanup']
        inactive_days = options['inactive_days']
        dry_run = options['dry_run']
        
        self.stdout.write(f"开始清理会话数据...")
        
        # 清理数据库会话
        self._cleanup_db_sessions(inactive_days, dry_run)
        
        # 如果使用Redis作为缓存后端，尝试清理Redis会话
        if 'django_redis' in settings.CACHES['default'].get('BACKEND', ''):
            self._cleanup_redis_sessions(force_redis_cleanup, inactive_days, dry_run)
        
        self.stdout.write(self.style.SUCCESS("会话清理完成!"))
    
    def _cleanup_db_sessions(self, inactive_days, dry_run):
        """清理数据库中的过期会话"""
        # 删除已过期会话
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        expired_count = expired_sessions.count()
        
        self.stdout.write(f"找到 {expired_count} 个已过期会话")
        
        if not dry_run and expired_count > 0:
            expired_sessions.delete()
            self.stdout.write(self.style.SUCCESS(f"已删除 {expired_count} 个过期会话"))
        
        # 删除不活跃会话
        if inactive_days > 0:
            inactive_date = timezone.now() - timezone.timedelta(days=inactive_days)
            inactive_sessions = Session.objects.filter(
                last_activity__lt=inactive_date, 
                expire_date__gt=timezone.now()
            )
            inactive_count = inactive_sessions.count()
            
            self.stdout.write(f"找到 {inactive_count} 个不活跃会话 (超过 {inactive_days} 天未活动)")
            
            if not dry_run and inactive_count > 0:
                inactive_sessions.delete()
                self.stdout.write(self.style.SUCCESS(f"已删除 {inactive_count} 个不活跃会话"))
    
    def _cleanup_redis_sessions(self, force_cleanup, inactive_days, dry_run):
        """清理Redis中的会话数据"""
        try:
            # 获取Redis连接信息
            location = settings.CACHES['default'].get('LOCATION', '')
            if not location.startswith('redis://'):
                self.stdout.write(self.style.WARNING("Redis配置不正确，无法清理Redis会话"))
                return
                
            # 解析Redis连接
            parts = location[8:].split(':')
            host = parts[0]
            port = int(parts[1].split('/')[0]) if len(parts) > 1 else 6379
            
            # 获取Redis客户端
            redis_client = redis.Redis(host=host, port=port, socket_timeout=5)
            
            # 获取会话相关键
            key_prefix = settings.CACHES['default'].get('KEY_PREFIX', '')
            session_cookie_name = getattr(settings, 'SESSION_COOKIE_NAME', 'sessionid')
            session_pattern = f"{key_prefix}:*{session_cookie_name}*"
            
            session_keys = redis_client.keys(session_pattern)
            self.stdout.write(f"Redis中找到 {len(session_keys)} 个会话键")
            
            if force_cleanup:
                if not dry_run:
                    deleted_count = 0
                    for key in session_keys:
                        redis_client.delete(key)
                        deleted_count += 1
                    self.stdout.write(self.style.SUCCESS(f"已强制删除 {deleted_count} 个Redis会话"))
                else:
                    self.stdout.write(f"将删除 {len(session_keys)} 个Redis会话 (试运行模式)")
            else:
                self.stdout.write("跳过Redis会话清理 (未指定--force-redis-cleanup)")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Redis会话清理失败: {str(e)}"))
            logger.error(f"Redis会话清理失败: {str(e)}")
            return 