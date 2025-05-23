from django.test import TestCase
from django.core.cache import cache
from django_redis import get_redis_connection

# Create your tests here.

class RedisConnectionTest(TestCase):
    def test_redis_connection(self):
        """测试Redis连接是否正常工作"""
        # 使用cache接口测试
        cache.set('test_key', 'test_value')
        self.assertEqual(cache.get('test_key'), 'test_value')
        
        # 直接使用Redis连接测试
        try:
            redis_conn = get_redis_connection("default")
            redis_conn.set('test_key_direct', 'test_value_direct')
            self.assertEqual(redis_conn.get('test_key_direct').decode(), 'test_value_direct')
            print("Redis连接成功测试通过！")
        except Exception as e:
            self.fail(f"Redis连接失败: {str(e)}")
