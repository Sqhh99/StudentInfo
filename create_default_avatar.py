from PIL import Image, ImageDraw
import os

# 创建一个200x200的白色背景图片
img = Image.new('RGB', (200, 200), color=(240, 240, 240))
draw = ImageDraw.Draw(img)

# 绘制一个简单的头像形状
draw.ellipse((40, 40, 160, 160), fill=(100, 149, 237))  # 绘制圆形
draw.ellipse((70, 70, 90, 90), fill=(240, 240, 240))  # 左眼
draw.ellipse((110, 70, 130, 90), fill=(240, 240, 240))  # 右眼
draw.arc((70, 100, 130, 130), start=0, end=180, fill=(240, 240, 240), width=3)  # 嘴巴、

# 确保目录存在
img_dir = 'static/images'
if not os.path.exists(img_dir):
    os.makedirs(img_dir)

# 保存图片到static目录，这样可以直接由Django的静态文件处理
img_path = os.path.join(img_dir, 'default-profile.png')
img.save(img_path)

# 同时保存到apps的静态目录
app_static_path = os.path.join('students', 'static', 'images', 'default-profile.png')
if not os.path.exists(os.path.dirname(app_static_path)):
    os.makedirs(os.path.dirname(app_static_path))
img.save(app_static_path)

print(f"默认头像已创建：{img_path} 和 {app_static_path}") 