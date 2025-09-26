#!/usr/bin/env python
"""
GUI功能测试脚本
创建测试图片并测试GUI功能
"""

import os
import sys
from PIL import Image, ImageDraw
from datetime import datetime
import piexif

def create_test_images():
    """创建测试图片"""
    # 创建测试目录
    test_dir = "test_images"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建几张测试图片
    images_info = [
        ("test1.jpg", (800, 600), "red", "2024:01:15 10:30:00"),
        ("test2.jpg", (1024, 768), "blue", "2024:02:20 14:15:30"),
        ("test3.png", (640, 480), "green", None),  # PNG通常没有EXIF
    ]
    
    for filename, size, color, exif_date in images_info:
        # 创建图片
        img = Image.new('RGB', size, color)
        draw = ImageDraw.Draw(img)
        
        # 添加一些内容让图片更有意思
        draw.rectangle([50, 50, size[0]-50, size[1]-50], outline="white", width=5)
        draw.text((100, 100), f"Test Image: {filename}", fill="white")
        draw.text((100, 150), f"Size: {size[0]}x{size[1]}", fill="white")
        draw.text((100, 200), f"Color: {color}", fill="white")
        
        filepath = os.path.join(test_dir, filename)
        
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
            img.save(filepath, "JPEG", exif=exif_bytes)
        else:
            img.save(filepath)
        
        print(f"已创建测试图片: {filepath}")
    
    print(f"\n测试图片已保存到目录: {os.path.abspath(test_dir)}")
    return test_dir

def main():
    """主函数"""
    print("=== GUI功能测试 ===")
    
    # 创建测试图片
    test_dir = create_test_images()
    
    print("\n测试步骤:")
    print("1. 运行 'python gui_app.py' 启动GUI应用")
    print("2. 测试文件选择功能：点击'选择图片文件'按钮")
    print("3. 测试文件夹选择功能：点击'选择文件夹'按钮")
    print(f"4. 测试拖拽功能：将 {test_dir} 文件夹拖拽到图片列表区域")
    print("5. 调整水印参数（字体大小、颜色、位置、透明度）")
    print("6. 点击'开始处理'按钮测试水印添加功能")
    print("7. 检查输出目录中的水印图片")
    
    print("\n预期结果:")
    print("- 界面应该正常显示")
    print("- 能够导入图片并在列表中显示")
    print("- 能够显示图片的拍摄日期（EXIF日期或文件修改日期）")
    print("- 处理完成后在输出目录找到带水印的图片")
    
    # 可选：尝试启动GUI
    try:
        print("\n正在尝试启动GUI应用...")
        import subprocess
        subprocess.Popen([sys.executable, "gui_app.py"])
        print("GUI应用已启动！")
    except Exception as e:
        print(f"启动GUI失败: {e}")
        print("请手动运行: python gui_app.py")

if __name__ == "__main__":
    main()