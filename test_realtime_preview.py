#!/usr/bin/env python
"""
测试所有功能的实时预览功能
"""

import os
import sys
from PIL import Image

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

def test_realtime_preview():
    """测试实时预览功能"""
    print("=== 实时预览功能测试 ===")
    
    # 1. 测试颜色选择的实时预览
    print("1. 颜色选择实时预览测试:")
    print("   - 在GUI中点击颜色输入框旁的🎨按钮")
    print("   - 选择不同颜色，观察预览窗口是否实时更新")
    print("   - 验证颜色更改是否立即反映在水印上")
    
    # 2. 测试字体选择的实时预览
    print("\n2. 字体选择实时预览测试:")
    print("   - 在GUI中点击'选择字体'按钮")
    print("   - 选择不同字体，观察预览窗口是否实时更新")
    print("   - 验证字体更改是否立即反映在水印上")
    
    # 3. 测试旋转功能的实时预览
    print("\n3. 旋转功能实时预览测试:")
    print("   - 调整旋转滑块或输入框")
    print("   - 观察预览窗口是否实时更新")
    print("   - 验证旋转角度更改是否立即反映在水印上")
    
    # 4. 测试组合功能的实时预览
    print("\n4. 组合功能实时预览测试:")
    print("   - 同时调整多个参数（颜色、字体、旋转等）")
    print("   - 观察预览窗口是否实时更新所有更改")
    print("   - 验证所有参数更改是否协调一致地反映在水印上")
    
    print("\n测试说明:")
    print("- 所有参数更改都应触发延迟300ms的预览更新")
    print("- 预览更新应流畅且无明显卡顿")
    print("- 所有功能组合使用时应正常工作")
    
    print("\n请手动在GUI应用中执行以上测试步骤！")

if __name__ == "__main__":
    test_realtime_preview()