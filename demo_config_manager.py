#!/usr/bin/env python
"""
演示配置管理功能
"""

import os
import sys
from pathlib import Path

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from src.config_manager import ConfigManager


def demo_config_manager():
    """演示配置管理器功能"""
    print("=== 配置管理功能演示 ===")
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    print(f"配置目录: {config_manager.config_dir}")
    
    # 显示初始模板
    print("\n1. 初始模板:")
    templates = config_manager.get_all_templates()
    for template in templates:
        print(f"   - {template['name']}")
    
    # 创建几个测试模板
    templates_to_save = [
        {
            'name': '红色粗体模板',
            'font_size': 48,
            'color': '#FF0000',
            'position': 'top_left',
            'font_path': '',
            'opacity': 0.8,
            'output_format': 'png',
            'custom_text': '重要文档',
            'font_style_bold': True,
            'font_style_italic': False,
            'shadow': True,
            'stroke': False,
            'rotation': 0.0
        },
        {
            'name': '蓝色斜体模板',
            'font_size': 36,
            'color': '#0000FF',
            'position': 'bottom_right',
            'font_path': '',
            'opacity': 0.7,
            'output_format': 'jpeg',
            'custom_text': '机密资料',
            'font_style_bold': False,
            'font_style_italic': True,
            'shadow': False,
            'stroke': True,
            'rotation': 30.0
        },
        {
            'name': '绿色居中模板',
            'font_size': 60,
            'color': '#00FF00',
            'position': 'center',
            'font_path': '',
            'opacity': 0.9,
            'output_format': 'auto',
            'custom_text': '水印测试',
            'font_style_bold': True,
            'font_style_italic': True,
            'shadow': True,
            'stroke': True,
            'rotation': -45.0
        }
    ]
    
    # 保存模板
    print("\n2. 保存测试模板:")
    for template in templates_to_save:
        if config_manager.save_template(template):
            print(f"   ✓ '{template['name']}' 保存成功")
        else:
            print(f"   ✗ '{template['name']}' 保存失败")
    
    # 显示所有模板
    print("\n3. 所有模板:")
    templates = config_manager.get_all_templates()
    for template in templates:
        print(f"   - {template['name']}")
    
    # 演示会话设置保存和加载
    print("\n4. 会话设置功能:")
    session_settings = {
        'font_size': 42,
        'color': '#FFFF00',
        'position': 'top_right',
        'font_path': '/System/Library/Fonts/Arial.ttf',
        'opacity': 0.85,
        'output_format': 'png',
        'custom_text': '临时设置',
        'font_style_bold': False,
        'font_style_italic': False,
        'shadow': True,
        'stroke': False,
        'rotation': 15.0
    }
    
    # 保存会话设置
    if config_manager.save_last_session(session_settings):
        print("   ✓ 会话设置保存成功")
        
        # 加载会话设置
        loaded_settings = config_manager.load_last_session()
        if loaded_settings:
            print("   ✓ 会话设置加载成功")
            print(f"     字体大小: {loaded_settings.get('font_size')}")
            print(f"     颜色: {loaded_settings.get('color')}")
            print(f"     位置: {loaded_settings.get('position')}")
            print(f"     透明度: {loaded_settings.get('opacity')}")
            print(f"     自定义文本: {loaded_settings.get('custom_text')}")
        else:
            print("   ✗ 会话设置加载失败")
    else:
        print("   ✗ 会话设置保存失败")
    
    # 演示模板删除
    print("\n5. 模板删除功能:")
    templates_to_delete = ['红色粗体模板', '蓝色斜体模板']
    for template_name in templates_to_delete:
        if config_manager.delete_template(template_name):
            print(f"   ✓ '{template_name}' 删除成功")
        else:
            print(f"   ✗ '{template_name}' 删除失败")
    
    # 显示最终模板
    print("\n6. 最终模板:")
    templates = config_manager.get_all_templates()
    for template in templates:
        print(f"   - {template['name']}")
    
    print("\n=== 配置管理功能演示完成 ===")
    print("\n主要功能:")
    print("✅ 模板保存: 将当前水印设置保存为模板")
    print("✅ 模板加载: 应用已保存的模板设置")
    print("✅ 模板管理: 重命名、删除模板")
    print("✅ 会话保持: 自动保存和加载上次使用设置")
    print("✅ 默认模板: 提供系统默认配置")


if __name__ == "__main__":
    demo_config_manager()