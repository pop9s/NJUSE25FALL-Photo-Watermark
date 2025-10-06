#!/usr/bin/env python
"""
测试字体功能
"""

import tkinter as tk
from tkinter import font

def test_fonts():
    """测试系统字体获取"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    try:
        # 获取系统字体
        font_families = list(font.families())
        print(f"系统中找到 {len(font_families)} 种字体")
        
        # 显示前10个字体
        print("前10个字体:")
        for i, font_name in enumerate(font_families[:10]):
            print(f"  {i+1}. {font_name}")
        
        # 检查常用中文字体
        common_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial', 'Times New Roman']
        print("\n常用字体检查:")
        for font_name in common_fonts:
            if font_name in font_families:
                print(f"  ✓ {font_name} - 可用")
            else:
                print(f"  ✗ {font_name} - 不可用")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")
    finally:
        root.destroy()

if __name__ == "__main__":
    test_fonts()