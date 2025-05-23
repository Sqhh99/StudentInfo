from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User
from students.models import Student, Class, Major, Department, Course, Score
import random
import datetime
from faker import Faker

fake = Faker('zh_CN')

# 用来生成测试数据的常量
MAJORS = ["计算机科学与技术", "软件工程", "人工智能", "数据科学", "网络工程"]
CLASS_YEARS = [2020, 2021, 2022, 2023]

# 课程数据
COURSE_DATA = [
    {"name": "计算机导论", "code": "CS101", "credit": 3.0, "semester": "大一上学期", "description": "计算机科学基础概念介绍"},
    {"name": "数据结构与算法", "code": "CS201", "credit": 4.0, "semester": "大二上学期", "description": "基本数据结构与算法"},
    {"name": "高等数学", "code": "MATH201", "credit": 5.0, "semester": "大一上学期", "description": "微积分与线性代数基础"},
    {"name": "大学物理", "code": "PHY102", "credit": 4.0, "semester": "大一下学期", "description": "物理学基础知识"},
    {"name": "大学英语", "code": "LANG101", "credit": 3.0, "semester": "大一上学期", "description": "大学英语基础课程"},
    {"name": "微观经济学", "code": "ECON202", "credit": 3.0, "semester": "大二下学期", "description": "经济学基础理论"},
    {"name": "数据库系统", "code": "CS301", "credit": 3.5, "semester": "大三上学期", "description": "关系型数据库理论与实践"},
    {"name": "人工智能", "code": "CS401", "credit": 4.0, "semester": "大四上学期", "description": "人工智能基础理论与应用"},
    {"name": "计算机网络", "code": "CS302", "credit": 3.0, "semester": "大三上学期", "description": "网络协议与架构"},
    {"name": "操作系统", "code": "CS303", "credit": 4.0, "semester": "大三下学期", "description": "操作系统原理与设计"},
    {"name": "软件工程", "code": "SE301", "credit": 4.0, "semester": "大三上学期", "description": "软件开发流程与管理"},
    {"name": "Web开发技术", "code": "SE302", "credit": 3.0, "semester": "大三下学期", "description": "Web应用程序设计与开发"},
    {"name": "机器学习", "code": "AI301", "credit": 4.0, "semester": "大四上学期", "description": "机器学习算法与应用"},
    {"name": "深度学习", "code": "AI302", "credit": 3.0, "semester": "大四下学期", "description": "深度神经网络理论与应用"},
    {"name": "大数据技术", "code": "DS301", "credit": 4.0, "semester": "大三上学期", "description": "大数据处理框架与技术"},
    {"name": "云计算", "code": "CS402", "credit": 3.0, "semester": "大四下学期", "description": "云计算架构与服务"},
    {"name": "编译原理", "code": "CS304", "credit": 3.5, "semester": "大三下学期", "description": "编程语言编译原理"},
    {"name": "移动应用开发", "code": "SE401", "credit": 3.0, "semester": "大四上学期", "description": "移动平台应用程序开发"},
    {"name": "网络安全", "code": "CS403", "credit": 3.0, "semester": "大四下学期", "description": "网络与信息安全技术"},
    {"name": "毕业设计", "code": "CS499", "credit": 6.0, "semester": "大四下学期", "description": "本科毕业项目设计与实现"}
]

class Command(BaseCommand):
    help = '向系统添加测试数据，包括专业、班级、学生、课程和成绩信息'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=50,
            help='要创建的学生数量(默认: 50)',
        )
        
        parser.add_argument(
            '--clear',
            action='store_true',
            help='清除现有数据后再添加新数据',
        )
        
    def handle(self, *args, **options):
        students_count = options['students']
        clear_data = options['clear']
        
        if clear_data:
            self.clear_existing_data()
            
        self.stdout.write("创建专业和班级数据...")
        majors = self.create_majors()
        classes = self.create_classes(majors)
        
        self.stdout.write("创建院系数据...")
        departments = self.create_departments()
        
        self.stdout.write("创建课程数据...")
        courses = self.create_courses(departments)
        
        self.stdout.write(f"创建{students_count}名学生数据...")
        students = self.create_students(students_count, classes)
        
        self.stdout.write("创建学生成绩数据...")
        scores = self.create_scores(students, courses)
        
        self.stdout.write(self.style.SUCCESS('成功添加测试数据!'))
        self.stdout.write(f"- 创建了 {len(majors)} 个专业")
        self.stdout.write(f"- 创建了 {len(departments)} 个院系")
        self.stdout.write(f"- 创建了 {len(classes)} 个班级")
        self.stdout.write(f"- 创建了 {len(courses)} 门课程")
        self.stdout.write(f"- 创建了 {len(students)} 名学生")
        self.stdout.write(f"- 创建了 {scores} 条成绩记录")
    
    def clear_existing_data(self):
        """清除现有数据"""
        self.stdout.write("清除现有数据...")
        Score.objects.all().delete()
        Student.objects.all().delete()
        Course.objects.all().delete()
        Class.objects.all().delete()
        Major.objects.all().delete()
        Department.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS("数据已清除"))
    
    def create_majors(self):
        """创建专业数据"""
        majors = []
        for major_name in MAJORS:
            major_code = ''.join(major_name[:2]) + ''.join([str(random.randint(0, 9)) for _ in range(2)])
            major, created = Major.objects.get_or_create(
                name=major_name,
                defaults={
                    'code': major_code,
                    'description': f"{major_name}专业培养具有扎实理论基础和专业技能的人才"
                }
            )
            majors.append(major)
            if created:
                self.stdout.write(f"  创建专业: {major.name} (代码: {major.code})")
        return majors
    
    def create_departments(self):
        """创建院系数据"""
        departments = []
        department_data = [
            {"name": "计算机科学与技术学院", "code": "CS-DEPT"},
            {"name": "数学与统计学院", "code": "MATH-DEPT"},
            {"name": "物理与电子工程学院", "code": "PHY-DEPT"},
            {"name": "外国语学院", "code": "LANG-DEPT"},
            {"name": "经济管理学院", "code": "ECON-DEPT"}
        ]
        
        for dept in department_data:
            department, created = Department.objects.get_or_create(
                name=dept["name"],
                defaults={
                    'code': dept["code"],
                    'description': f"{dept['name']}是培养{dept['name'][:-2]}专业人才的重要学院"
                }
            )
            departments.append(department)
            if created:
                self.stdout.write(f"  创建院系: {department.name}")
        return departments
    
    def create_classes(self, majors):
        """创建班级数据"""
        classes = []
        for major in majors:
            for year in CLASS_YEARS:
                for class_num in range(1, 3):  # 每个专业每年有2个班
                    class_name = f"{major.name}{year}级{class_num}班"
                    class_code = f"{major.code}-{year}-{class_num}"
                    
                    class_obj, created = Class.objects.get_or_create(
                        name=class_name,
                        code=class_code,
                        defaults={
                            'major': major,
                            'admission_year': year,
                        }
                    )
                    classes.append(class_obj)
                    if created:
                        self.stdout.write(f"  创建班级: {class_obj.name} (代码: {class_obj.code})")
        return classes
    
    def create_courses(self, departments):
        """创建课程数据"""
        courses = []
        for course_data in COURSE_DATA:
            # 根据课程代码前缀确定所属院系
            code_prefix = course_data["code"][:2]
            if code_prefix == "CS" or code_prefix == "SE" or code_prefix == "AI" or code_prefix == "DS":
                department = next((d for d in departments if d.code == "CS-DEPT"), departments[0])
            elif code_prefix == "MA":
                department = next((d for d in departments if d.code == "MATH-DEPT"), departments[0])
            elif code_prefix == "PH":
                department = next((d for d in departments if d.code == "PHY-DEPT"), departments[0])
            elif code_prefix == "LA":
                department = next((d for d in departments if d.code == "LANG-DEPT"), departments[0])
            elif code_prefix == "EC":
                department = next((d for d in departments if d.code == "ECON-DEPT"), departments[0])
            else:
                department = random.choice(departments)
            
            try:
                course, created = Course.objects.get_or_create(
                    code=course_data["code"],
                    defaults={
                        'name': course_data["name"],
                        'credit': course_data["credit"],
                        'teacher': fake.name(),
                        'description': course_data.get("description", ""),
                        'department': department,
                        'class_time': f"周{random.randint(1, 5)} {random.choice(['1-2节', '3-5节', '6-8节'])}",
                        'location': f"{random.choice(['主教学楼', '科学楼', '工程楼'])}{random.randint(1, 4)}-{random.randint(101, 505)}",
                        'capacity': random.randint(30, 120),
                        'semester': course_data.get("semester", ""),
                        'status': random.choice(['active', 'pending', 'completed']),
                    }
                )
                courses.append(course)
                if created:
                    self.stdout.write(f"  创建课程: {course.name} ({course.code})")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"创建课程失败: {str(e)}"))
        return courses
    
    def create_students(self, count, classes):
        """创建学生数据"""
        students = []
        student_count = 0
        
        # 确保每个班至少有一些学生
        for class_obj in classes:
            # 每个班创建2-5名学生
            class_students_count = random.randint(2, 5)
            for i in range(class_students_count):
                student_count += 1
                student = self._create_student(class_obj, student_count)
                if student:
                    students.append(student)
        
        # 创建剩余的随机学生，直到达到总数
        remaining_count = count - student_count
        if remaining_count > 0:
            for i in range(remaining_count):
                student_count += 1
                # 随机选择一个班级
                class_obj = random.choice(classes)
                student = self._create_student(class_obj, student_count)
                if student:
                    students.append(student)
        
        return students
    
    def _create_student(self, class_obj, count):
        """创建单个学生"""
        # 生成学号 (年份 + 序号)
        student_id = f"{class_obj.admission_year}{count:04d}"
        
        # 随机性别
        gender = random.choice(['male', 'female'])
        
        # 生成入学日期
        admission_date = datetime.date(class_obj.admission_year, 9, 1)
        
        try:
            student, created = Student.objects.get_or_create(
                student_id=student_id,
                defaults={
                    'name': fake.name(),
                    'gender': gender,
                    'class_obj': class_obj,
                    'major': class_obj.major,
                    'admission_date': admission_date,
                    'phone': fake.phone_number(),
                    'email': fake.email(),
                    'status': random.choice(['active', 'inactive', 'graduated', 'transferred']),
                }
            )
            if created and count % 10 == 0:  # 只显示每10个创建的学生
                self.stdout.write(f"  创建学生: {student.name} (学号: {student.student_id})")
            return student
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"创建学生失败: {str(e)}"))
            return None
    
    def create_scores(self, students, courses):
        """为学生创建课程成绩数据"""
        score_count = 0
        
        for student in students:
            # 根据学生年级选择适当的课程
            student_year = student.admission_date.year
            current_year = datetime.date.today().year
            study_years = current_year - student_year
            
            # 根据学习年限筛选可选课程
            available_courses = []
            for course in courses:
                if "大一" in course.semester and study_years >= 0:
                    available_courses.append(course)
                elif "大二" in course.semester and study_years >= 1:
                    available_courses.append(course)
                elif "大三" in course.semester and study_years >= 2:
                    available_courses.append(course)
                elif "大四" in course.semester and study_years >= 3:
                    available_courses.append(course)
            
            # 如果没有可选课程，使用所有课程
            if not available_courses:
                available_courses = courses
            
            # 每个学生随机选择5-10门课程
            selected_courses = random.sample(
                available_courses, 
                min(random.randint(5, 10), len(available_courses))
            )
            
            for course in selected_courses:
                # 90%的概率通过课程
                if random.random() < 0.9:
                    # 不同等级的成绩分布
                    if random.random() < 0.2:  # 20%优秀
                        score_value = random.randint(90, 100)
                    elif random.random() < 0.5:  # 30%良好
                        score_value = random.randint(80, 89)
                    elif random.random() < 0.8:  # 30%中等
                        score_value = random.randint(70, 79)
                    else:  # 20%及格
                        score_value = random.randint(60, 69)
                else:  # 10%不及格
                    score_value = random.randint(0, 59)
                
                try:
                    # 确定学期
                    semester_year = student_year + (1 if "下学期" in course.semester else 0)
                    semester = f"{semester_year}-{semester_year+1} {course.semester}"
                    
                    score, created = Score.objects.get_or_create(
                        student=student,
                        course=course,
                        semester=semester,
                        defaults={
                            'score': score_value,
                            'comment': random.choice(['', '优秀', '良好', '需要努力']) if random.random() < 0.3 else ''
                        }
                    )
                    
                    if created:
                        score_count += 1
                        if score_count % 100 == 0:  # 只显示每100条成绩记录
                            self.stdout.write(f"  已创建 {score_count} 条成绩记录...")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"创建成绩失败: {str(e)}"))
        
        self.stdout.write(f"  共创建 {score_count} 条成绩记录")
        return score_count 