import os
import datetime
from django.core.management.base import BaseCommand
from django.db import transaction
from students.models import Major, Class, Student

class Command(BaseCommand):
    help = '初始化专业、班级和学生数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化数据...')
        
        # 使用事务确保数据一致性
        with transaction.atomic():
            # 清空现有数据（可选）
            self.stdout.write('清空现有数据...')
            Student.objects.all().delete()
            Class.objects.all().delete()
            Major.objects.all().delete()
            
            # 创建专业数据
            self.stdout.write('创建专业数据...')
            cs_major = Major.objects.create(
                name='计算机科学与技术',
                code='CS',
                description='计算机科学与技术专业培养具备计算机、网络及信息系统等方面的知识，能够从事计算机应用、研究和开发的专业人才。'
            )
            
            se_major = Major.objects.create(
                name='软件工程',
                code='SE',
                description='软件工程专业培养能够从事软件开发、测试、维护和项目管理的专业人才。'
            )
            
            ai_major = Major.objects.create(
                name='人工智能',
                code='AI',
                description='人工智能专业培养具备机器学习、深度学习、自然语言处理等方面知识的专业人才。'
            )
            
            # 创建班级数据
            self.stdout.write('创建班级数据...')
            cs_class1 = Class.objects.create(
                name='计算机科学与技术1班',
                code='CS2023-1',
                major=cs_major,
                admission_year=2023
            )
            
            cs_class2 = Class.objects.create(
                name='计算机科学与技术2班',
                code='CS2023-2',
                major=cs_major,
                admission_year=2023
            )
            
            se_class1 = Class.objects.create(
                name='软件工程1班',
                code='SE2023-1',
                major=se_major,
                admission_year=2023
            )
            
            se_class2 = Class.objects.create(
                name='软件工程2班',
                code='SE2023-2',
                major=se_major,
                admission_year=2023
            )
            
            ai_class1 = Class.objects.create(
                name='人工智能1班',
                code='AI2023-1',
                major=ai_major,
                admission_year=2023
            )
            
            # 创建学生数据
            self.stdout.write('创建学生数据...')
            
            # 计算机科学与技术1班学生
            students_data = [
                {
                    'student_id': '202301001',
                    'name': '张三',
                    'gender': 'male',
                    'class_obj': cs_class1,
                    'major': cs_major,
                    'admission_date': datetime.date(2023, 9, 1),
                    'phone': '13800001234',
                    'email': 'zhangsan@example.com',
                    'status': 'active'
                },
                {
                    'student_id': '202301002',
                    'name': '李四',
                    'gender': 'male',
                    'class_obj': cs_class1,
                    'major': cs_major,
                    'admission_date': datetime.date(2023, 9, 1),
                    'phone': '13800002345',
                    'email': 'lisi@example.com',
                    'status': 'active'
                },
                {
                    'student_id': '202301003',
                    'name': '王五',
                    'gender': 'male',
                    'class_obj': cs_class1,
                    'major': cs_major,
                    'admission_date': datetime.date(2023, 9, 1),
                    'phone': '13800003456',
                    'email': 'wangwu@example.com',
                    'status': 'active'
                },
                
                # 计算机科学与技术2班学生
                {
                    'student_id': '202302001',
                    'name': '赵六',
                    'gender': 'female',
                    'class_obj': cs_class2,
                    'major': cs_major,
                    'admission_date': datetime.date(2023, 9, 1),
                    'phone': '13800004567',
                    'email': 'zhaoliu@example.com',
                    'status': 'active'
                },
                {
                    'student_id': '202302002',
                    'name': '钱七',
                    'gender': 'male',
                    'class_obj': cs_class2,
                    'major': cs_major,
                    'admission_date': datetime.date(2023, 9, 1),
                    'phone': '13800005678',
                    'email': 'qianqi@example.com',
                    'status': 'inactive'
                },
                
                # 软件工程1班学生
                {
                    'student_id': '202303001',
                    'name': '孙八',
                    'gender': 'female',
                    'class_obj': se_class1,
                    'major': se_major,
                    'admission_date': datetime.date(2023, 9, 1),
                    'phone': '13800006789',
                    'email': 'sunba@example.com',
                    'status': 'active'
                },
                {
                    'student_id': '202303002',
                    'name': '周九',
                    'gender': 'male',
                    'class_obj': se_class1,
                    'major': se_major,
                    'admission_date': datetime.date(2023, 9, 1),
                    'phone': '13800007890',
                    'email': 'zhoujiu@example.com',
                    'status': 'active'
                },
                
                # 软件工程2班学生
                {
                    'student_id': '202304001',
                    'name': '吴十',
                    'gender': 'female',
                    'class_obj': se_class2,
                    'major': se_major,
                    'admission_date': datetime.date(2023, 9, 1),
                    'phone': '13800008901',
                    'email': 'wushi@example.com',
                    'status': 'active'
                },
                
                # 人工智能1班学生
                {
                    'student_id': '202305001',
                    'name': '郑十一',
                    'gender': 'male',
                    'class_obj': ai_class1,
                    'major': ai_major,
                    'admission_date': datetime.date(2023, 9, 1),
                    'phone': '13800009012',
                    'email': 'zhengshiyi@example.com',
                    'status': 'active'
                },
                {
                    'student_id': '202305002',
                    'name': '刘十二',
                    'gender': 'female',
                    'class_obj': ai_class1,
                    'major': ai_major,
                    'admission_date': datetime.date(2023, 9, 1),
                    'phone': '13800000123',
                    'email': 'liushier@example.com',
                    'status': 'graduated'
                }
            ]
            
            for student_data in students_data:
                Student.objects.create(**student_data)
            
            self.stdout.write(self.style.SUCCESS('数据初始化完成!'))
            self.stdout.write(f'- 创建了 {Major.objects.count()} 个专业')
            self.stdout.write(f'- 创建了 {Class.objects.count()} 个班级')
            self.stdout.write(f'- 创建了 {Student.objects.count()} 名学生') 