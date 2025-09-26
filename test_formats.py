#!/usr/bin/env python
"""
扩展格式支持测试脚本
测试新增的BMP, TIFF, WebP等格式支持，以及输出格式选择功能
"""

import os
import sys
from PIL import Image, ImageDraw
from datetime import datetime
import piexif

def create_multi_format_test_images():
    """创建多种格式的测试图片"""
    # 创建测试目录
    test_dir = "test_formats"
    os.makedirs(test_dir, exist_ok=True)
    
    # 定义要创建的图片格式和信息
    images_info = [
        # (文件名, 尺寸, 颜色, EXIF日期, 描述)
        ("test_jpeg.jpg", (800, 600), "red", "2024:01:15 10:30:00", "标准JPEG格式"),
        ("test_png_rgb.png", (640, 480), "blue", None, "PNG RGB格式（无透明）"),
        ("test_png_rgba.png", (640, 480), None, None, "PNG RGBA格式（有透明）"),
        ("test_bmp.bmp", (600, 400), "green", None, "Windows BMP格式"),
        ("test_tiff.tiff", (700, 500), "yellow", "2024:02:20 14:15:30", "TIFF格式"),
        ("test_webp.webp", (640, 480), "purple", None, "现代WebP格式"),
        ("test_gif.gif", (500, 400), "orange", None, "GIF格式"),
        ("test_ico.ico", (256, 256), "cyan", None, "图标格式"),
    ]
    
    for filename, size, color, exif_date, description in images_info:
        try:
            print(f"正在创建: {filename} - {description}")
            
            # 创建图像
            if filename == "test_png_rgba.png":
                # 创建带透明背景的PNG
                img = Image.new('RGBA', size, (0, 0, 0, 0))  # 完全透明背景
                draw = ImageDraw.Draw(img)
                
                # 绘制半透明的彩色矩形
                colors = [(255, 0, 0, 128), (0, 255, 0, 128), (0, 0, 255, 128)]
                for i, rgba_color in enumerate(colors):
                    x = i * size[0] // 3
                    draw.rectangle([x, 0, x + size[0]//3, size[1]], fill=rgba_color)
                
                # 添加文本
                draw.text((50, 50), "透明PNG测试", fill=(255, 255, 255, 255))
                draw.text((50, 100), filename, fill=(0, 0, 0, 255))
                
            else:
                # 创建普通图像
                if color:
                    img = Image.new('RGB', size, color)
                else:
                    # 创建渐变背景
                    img = Image.new('RGB', size)
                    pixels = img.load()
                    for y in range(size[1]):
                        for x in range(size[0]):
                            r = int(255 * x / size[0])
                            g = int(255 * y / size[1])
                            b = 128
                            pixels[x, y] = (r, g, b)
                
                draw = ImageDraw.Draw(img)
                
                # 添加装饰性内容
                draw.rectangle([20, 20, size[0]-20, size[1]-20], outline="white", width=3)
                draw.text((50, 50), f"格式测试: {filename}", fill="white")
                draw.text((50, 100), f"尺寸: {size[0]}x{size[1]}", fill="white")
                draw.text((50, 150), description, fill="white")
            
            filepath = os.path.join(test_dir, filename)
            
            # 保存图片，根据格式处理EXIF
            if filename.endswith('.jpg') and exif_date:
                # 为JPEG添加EXIF信息
                exif_dict = {
                    "0th": {},
                    "Exif": {
                        piexif.ExifIFD.DateTimeOriginal: exif_date,
                        piexif.ExifIFD.DateTimeDigitized: exif_date,
                    },
                    "GPS": {},
                    "1st": {},
                    "thumbnail": None
                }
                exif_bytes = piexif.dump(exif_dict)
                img.save(filepath, "JPEG", exif=exif_bytes, quality=95)
                
            elif filename.endswith('.tiff') and exif_date:
                # TIFF也可以包含EXIF信息
                exif_dict = {
                    "0th": {},
                    "Exif": {
                        piexif.ExifIFD.DateTimeOriginal: exif_date,
                        piexif.ExifIFD.DateTimeDigitized: exif_date,
                    },
                    "GPS": {},
                    "1st": {},
                    "thumbnail": None
                }
                exif_bytes = piexif.dump(exif_dict)
                img.save(filepath, "TIFF", exif=exif_bytes)
                
            elif filename.endswith('.png'):
                img.save(filepath, "PNG")
                
            elif filename.endswith('.bmp'):
                # BMP不支持透明通道，需要转换
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                img.save(filepath, "BMP")
                
            elif filename.endswith('.webp'):
                img.save(filepath, "WEBP", quality=90)
                
            elif filename.endswith('.gif'):
                # GIF需要转换为调色板模式
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background
                img = img.convert('P', palette=Image.ADAPTIVE)
                img.save(filepath, "GIF")
                
            elif filename.endswith('.ico'):
                # ICO格式，保持为较小尺寸
                if img.size[0] > 256:
                    img = img.resize((256, 256), Image.Resampling.LANCZOS)
                img.save(filepath, "ICO")
                
            else:
                img.save(filepath)
            
            print(f"  ✅ 成功创建: {filepath}")
            
        except Exception as e:
            print(f"  ❌ 创建失败 {filename}: {e}")
    
    print(f"\n测试图片已保存到目录: {os.path.abspath(test_dir)}")
    return test_dir

def test_format_support():
    """测试格式支持"""
    print("=== 格式支持测试 ===")
    
    # 创建测试图片
    test_dir = create_multi_format_test_images()
    
    print("\n支持的输入格式:")
    from src.exif_reader import ExifReader
    reader = ExifReader()
    print(f"  {', '.join(sorted(reader.SUPPORTED_FORMATS))}")
    
    print("\n测试步骤:")
    print("1. 运行 'python gui_app.py' 启动GUI应用")
    print(f"2. 导入 {test_dir} 文件夹中的所有测试图片")
    print("3. 测试不同的输出格式设置:")
    print("   - auto: 保持原格式")
    print("   - jpeg: 强制输出为JPEG")
    print("   - png: 强制输出为PNG")
    print("4. 特别注意PNG透明通道的处理效果")
    print("5. 检查各种格式的水印添加效果")
    
    print("\n预期结果:")
    print("✅ 所有格式都能正确导入并显示在列表中")
    print("✅ JPEG和TIFF格式能读取EXIF日期")
    print("✅ PNG, BMP, GIF等格式使用文件修改日期")
    print("✅ PNG透明背景得到正确处理")
    print("✅ 输出格式选择功能正常工作")
    print("✅ JPEG输出时透明图片转换为白色背景")
    print("✅ PNG输出时保持透明通道")
    
    return test_dir

def main():
    """主函数"""
    test_dir = test_format_support()
    
    print(f"\n📁 测试文件位置: {os.path.abspath(test_dir)}")
    print("\n🎯 重点测试项目:")
    print("1. PNG透明背景处理")
    print("2. 输出格式选择 (auto/jpeg/png)")
    print("3. 各种输入格式支持")
    print("4. EXIF信息读取兼容性")

if __name__ == "__main__":
    main()