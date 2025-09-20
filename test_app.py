#!/usr/bin/env python3
"""
测试脚本：创建一个简单的测试图片来验证水印功能
"""

import os
import sys
from PIL import Image, ImageDraw
from datetime import datetime
import piexif

def create_test_image_with_exif(output_path: str, width: int = 800, height: int = 600):
    """创建一个带有EXIF信息的测试图片"""
    
    # 创建一个简单的彩色图片
    image = Image.new('RGB', (width, height), color='lightblue')
    draw = ImageDraw.Draw(image)
    
    # 添加一些图形来让图片更有意思
    draw.rectangle([50, 50, width-50, height-50], outline='blue', width=3)
    draw.ellipse([width//4, height//4, 3*width//4, 3*height//4], outline='red', width=2)
    draw.text((width//2-100, height//2), "Test Image", fill='black')
    
    # 创建EXIF数据
    exif_data = {
        "0th": {},
        "Exif": {},
        "GPS": {},
        "1st": {},
        "thumbnail": None
    }
    
    # 设置拍摄时间为2023年12月25日
    date_time = "2023:12:25 10:30:00"
    exif_data["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_time.encode('utf-8')
    exif_data["0th"][piexif.ImageIFD.DateTime] = date_time.encode('utf-8')
    
    # 转换为二进制EXIF数据
    exif_bytes = piexif.dump(exif_data)
    
    # 保存图片
    image.save(output_path, "JPEG", exif=exif_bytes)
    print(f"测试图片已创建: {output_path}")
    print(f"EXIF拍摄日期: {date_time}")


def create_test_images():
    """创建多个测试图片"""
    
    examples_dir = "examples"
    if not os.path.exists(examples_dir):
        os.makedirs(examples_dir)
    
    # 创建第一个测试图片 - 2023年圣诞节
    create_test_image_with_exif(
        os.path.join(examples_dir, "test_photo_1.jpg"),
        800, 600
    )
    
    # 创建第二个测试图片 - 2024年新年
    image2 = Image.new('RGB', (600, 800), color='lightgreen')
    draw2 = ImageDraw.Draw(image2)
    draw2.rectangle([30, 30, 570, 770], outline='green', width=3)
    draw2.text((250, 400), "New Year", fill='darkgreen')
    
    exif_data2 = {
        "0th": {},
        "Exif": {},
        "GPS": {},
        "1st": {},
        "thumbnail": None
    }
    
    date_time2 = "2024:01:01 00:00:00"
    exif_data2["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_time2.encode('utf-8')
    
    exif_bytes2 = piexif.dump(exif_data2)
    image_path2 = os.path.join(examples_dir, "test_photo_2.jpg")
    image2.save(image_path2, "JPEG", exif=exif_bytes2)
    print(f"测试图片已创建: {image_path2}")
    print(f"EXIF拍摄日期: {date_time2}")
    
    # 创建第三个测试图片 - PNG格式（2025年春节）
    image3 = Image.new('RGB', (400, 300), color='lightcoral')
    draw3 = ImageDraw.Draw(image3)
    draw3.ellipse([50, 50, 350, 250], outline='red', width=3)
    draw3.text((150, 140), "Spring Festival", fill='darkred')
    
    # PNG文件不支持EXIF，所以会使用文件修改时间
    image_path3 = os.path.join(examples_dir, "test_photo_3.png")
    image3.save(image_path3, "PNG")
    print(f"测试图片已创建: {image_path3}")
    print(f"PNG格式：使用文件修改时间作为水印日期")


def test_watermark_functionality():
    """测试水印功能"""
    
    print("\n开始测试水印功能...")
    
    # 首先创建测试图片
    create_test_images()
    
    # 测试程序功能
    examples_dir = os.path.abspath("examples")
    
    print(f"\n现在可以运行以下命令来测试水印功能：")
    print(f"python main.py \"{examples_dir}\"")
    print(f"python main.py \"{examples_dir}\" --font-size 48 --color \"#FF0000\" --position \"top_left\"")
    print(f"python main.py \"{examples_dir}\" --position \"center\" --opacity 0.7")
    
    # 尝试自动运行测试
    try:
        import subprocess
        result = subprocess.run([sys.executable, "main.py", examples_dir], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("\n✓ 基本功能测试通过")
            print("输出:", result.stdout)
        else:
            print("\n✗ 测试失败")
            print("错误:", result.stderr)
    except Exception as e:
        print(f"\n自动测试失败: {e}")
        print("请手动运行上述命令进行测试")


if __name__ == "__main__":
    test_watermark_functionality()