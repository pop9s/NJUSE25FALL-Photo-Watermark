#!/usr/bin/env python
"""
测试颜色验证功能
"""

import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# 测试颜色验证功能
def test_color_validation():
    """测试颜色验证功能"""
    # 模拟GUI应用中的颜色验证方法
    def is_valid_hex_color(hex_color):
        """验证十六进制颜色格式"""
        if not isinstance(hex_color, str):
            return False
        
        # 移除可能的#前缀
        hex_color = hex_color.lstrip('#')
        
        # 检查长度是否为6
        if len(hex_color) != 6:
            return False
        
        # 检查是否只包含有效的十六进制字符
        try:
            int(hex_color, 16)
            return True
        except ValueError:
            return False
    
    # 测试用例
    test_cases = [
        ("#FFFFFF", True),   # 有效颜色
        ("#000000", True),   # 有效颜色
        ("#FF0000", True),   # 有效颜色
        ("#FFFPPP", False),  # 无效字符
        ("#FFF", False),     # 长度不足
        ("#FFFFFFFF", False), # 长度过长
        ("FFFFFF", True),    # 无#前缀
        ("", False),         # 空字符串
        (None, False),       # None值
        ("#GGGGGG", False),  # 无效字符
    ]
    
    print("测试颜色验证功能:")
    for color, expected in test_cases:
        result = is_valid_hex_color(color)
        status = "✓" if result == expected else "❌"
        print(f"  {status} {color} -> {result} (期望: {expected})")
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_color_validation()