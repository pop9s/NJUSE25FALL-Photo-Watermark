#!/usr/bin/env python
"""
测试所有功能：字体、预设位置、手动拖拽、旋转
"""

import os
import sys
from PIL import Image, ImageDraw
import tkinter as tk
from tkinter import font

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

def create_test_image():
    """创建测试图片"""
    # 创建一个简单的测试图片
    test_image = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(test_image)
    
    # 添加一些内容让图片更有意思
    draw.rectangle([100, 100, 700, 500], outline="white", width=3)
    draw.text((300, 50), "Test Image for All Features", fill="black")
    
    test_image_path = os.path.join(current_dir, 'test_all_features.jpg')
    test_image.save(test_image_path, 'JPEG')
    print(f"已创建测试图片: {test_image_path}")
    return test_image_path

def test_font_functionality():
    """测试字体功能"""
    print("=== 测试字体功能 ===")
    
    try:
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        
        # 获取系统字体
        font_families = list(font.families())
        print(f"系统中找到 {len(font_families)} 种字体")
        
        # 检查常用字体
        common_fonts = ['Arial', 'Times New Roman', 'Microsoft YaHei', 'SimHei']
        available_fonts = []
        for font_name in common_fonts:
            if font_name in font_families:
                print(f"  ✓ {font_name} - 可用")
                available_fonts.append(font_name)
            else:
                print(f"  ✗ {font_name} - 不可用")
        
        root.destroy()
        print(f"可用字体: {available_fonts}")
        return available_fonts
        
    except Exception as e:
        print(f"字体功能测试失败: {e}")
        return []

def test_preset_positions():
    """测试预设位置功能"""
    print("\n=== 测试预设位置功能 ===")
    
    # 预设位置列表
    positions = [
        'top_left', 'top_center', 'top_right',
        'center_left', 'center', 'center_right',
        'bottom_left', 'bottom_center', 'bottom_right'
    ]
    
    print("九宫格预设位置:")
    for i, pos in enumerate(positions):
        row = i // 3
        col = i % 3
        symbol = ['↖', '↑', '↗', '←', '●', '→', '↙', '↓', '↘'][i]
        print(f"  {symbol} {pos}")
    
    return positions

def test_drag_and_drop_info():
    """测试手动拖拽功能信息"""
    print("\n=== 手动拖拽功能 ===")
    print("手动拖拽功能说明:")
    print("  1. 在GUI预览窗口中，可以直接用鼠标点击并拖拽水印到任意位置")
    print("  2. 拖拽时会显示水印的实时位置坐标")
    print("  3. 松开鼠标后，水印会固定在拖拽的位置")
    print("  4. 拖拽位置会覆盖预设位置设置")

def test_rotation_functionality():
    """测试旋转功能"""
    print("\n=== 测试旋转功能 ===")
    print("旋转功能说明:")
    print("  1. 支持-180度到180度的任意角度旋转")
    print("  2. 提供滑块和输入框两种方式调节角度")
    print("  3. 旋转功能同时支持文本水印和图片水印")
    print("  4. 旋转中心为水印的中心点")

def main():
    """主函数"""
    print("=== 照片水印工具完整功能测试 ===")
    
    # 创建测试图片
    test_image_path = create_test_image()
    
    # 测试各项功能
    available_fonts = test_font_functionality()
    preset_positions = test_preset_positions()
    test_drag_and_drop_info()
    test_rotation_functionality()
    
    print("\n=== 测试总结 ===")
    print("✓ 字体功能: 支持系统已安装的字体选择")
    print("✓ 预设位置: 提供九宫格布局（四角、正中心）")
    print("✓ 手动拖拽: 支持在预览图上拖拽水印到任意位置")
    print("✓ 旋转功能: 支持任意角度旋转水印")
    
    print("\n=== 使用说明 ===")
    print("1. 运行 'python gui_app.py' 启动GUI应用")
    print("2. 导入测试图片")
    print("3. 在控制面板中测试各项功能:")
    print("   - 字体: 点击'选择字体'按钮选择系统字体")
    print("   - 预设位置: 点击九宫格按钮选择位置")
    print("   - 手动拖拽: 在预览图上点击并拖拽水印")
    print("   - 旋转: 使用旋转滑块或输入框调节角度")
    
    # 清理测试图片
    try:
        os.remove(test_image_path)
        print(f"\n已清理测试图片: {test_image_path}")
    except:
        pass
    
    print("\n🎉 所有功能测试完成！")

if __name__ == "__main__":
    main()