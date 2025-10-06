#!/usr/bin/env python
"""
自定义水印功能测试脚本
测试新增的自定义文本、字体样式、阴影和描边功能
"""

import os
import sys
from PIL import Image, ImageDraw
from datetime import datetime
import piexif

def create_test_image():
    """创建测试图片"""
    # 创建测试目录
    test_dir = "test_custom"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建测试图片
    img = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # 添加一些装饰
    draw.rectangle([50, 50, 750, 550], outline="blue", width=3)
    draw.ellipse([200, 150, 600, 450], outline="red", width=2)
    
    # 添加EXIF信息
    exif_dict = {
        "0th": {},
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: "2024:03:15 10:30:00",
        },
        "GPS": {},
        "1st": {},
        "thumbnail": None
    }
    exif_bytes = piexif.dump(exif_dict)
    
    # 保存图片
    image_path = os.path.join(test_dir, "test_photo.jpg")
    img.save(image_path, "JPEG", exif=exif_bytes)
    
    print(f"✅ 测试图片已创建: {image_path}")
    return test_dir, image_path

def test_command_line_features():
    """测试命令行功能"""
    print("=== 命令行功能测试 ===")
    
    test_dir, image_path = create_test_image()
    
    # 测试用例
    test_cases = [
        {
            "name": "1. 基本自定义文本",
            "cmd": f'python main.py "{image_path}" --custom-text "测试水印" --output-dir "{test_dir}/output1"'
        },
        {
            "name": "2. 自定义文本+粗体",
            "cmd": f'python main.py "{image_path}" --custom-text "重要文档" --bold --font-size 48 --output-dir "{test_dir}/output2"'
        },
        {
            "name": "3. 自定义文本+阴影效果",
            "cmd": f'python main.py "{image_path}" --custom-text "版权所有" --shadow --color "#0000FF" --output-dir "{test_dir}/output3"'
        },
        {
            "name": "4. 自定义文本+描边效果",
            "cmd": f'python main.py "{image_path}" --custom-text "机密" --stroke --font-size 60 --color "#FF0000" --output-dir "{test_dir}/output4"'
        },
        {
            "name": "5. 综合效果：粗体+斜体+阴影+描边",
            "cmd": f'python main.py "{image_path}" --custom-text "综合效果测试" --bold --italic --shadow --stroke --font-size 40 --output-dir "{test_dir}/output5"'
        },
        {
            "name": "6. 保持原有功能：使用EXIF日期",
            "cmd": f'python main.py "{image_path}" --font-size 32 --color "#00AA00" --position "top_left" --output-dir "{test_dir}/output6"'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 {test_case['name']}")
        print(f"   命令: {test_case['cmd']}")
        
        try:
            result = os.system(test_case['cmd'])
            if result == 0:
                print("   ✅ 执行成功")
            else:
                print("   ❌ 执行失败")
        except Exception as e:
            print(f"   ❌ 执行错误: {e}")
    
    print(f"\n📁 测试结果保存在: {os.path.abspath(test_dir)}")

def test_gui_features():
    """测试GUI功能说明"""
    print("\n=== GUI功能测试说明 ===")
    print("1. 运行 'python gui_app.py' 启动GUI应用")
    print("2. 导入测试图片")
    print("3. 在水印设置区域测试以下功能:")
    print("   - 在'自定义文本'输入框中输入文本")
    print("   - 勾选'粗体'和'斜体'复选框")
    print("   - 勾选'阴影'和'描边'复选框")
    print("4. 调整其他参数并点击'开始处理'")
    print("5. 检查输出图片效果")

def main():
    """主函数"""
    print("🖼️  自定义水印功能测试")
    print("=" * 50)
    
    # 测试命令行功能
    test_command_line_features()
    
    # 测试GUI功能说明
    test_gui_features()
    
    print("\n🎉 测试完成！")
    print("请检查输出目录中的图片，验证新增功能是否正常工作。")

if __name__ == "__main__":
    main()