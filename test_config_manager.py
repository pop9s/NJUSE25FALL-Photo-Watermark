#!/usr/bin/env python
"""
测试配置管理功能
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


def test_config_manager():
    """测试配置管理器功能"""
    print("=== 测试配置管理器功能 ===")
    
    # 创建配置管理器
    config_dir = Path.home() / '.photo_watermark_test'
    config_manager = ConfigManager(str(config_dir))
    
    print(f"配置目录: {config_manager.config_dir}")
    
    # 测试获取所有模板
    templates = config_manager.get_all_templates()
    print(f"初始模板数量: {len(templates)}")
    
    # 测试保存模板
    test_template = {
        'name': '测试模板',
        'font_size': 48,
        'color': '#FF0000',
        'position': 'top_left',
        'font_path': '',
        'opacity': 0.8,
        'output_format': 'png',
        'custom_text': '测试水印',
        'font_style_bold': True,
        'font_style_italic': False,
        'shadow': True,
        'stroke': False,
        'rotation': 45.0
    }
    
    print("\n保存测试模板...")
    if config_manager.save_template(test_template):
        print("✓ 模板保存成功")
    else:
        print("✗ 模板保存失败")
    
    # 测试获取所有模板
    templates = config_manager.get_all_templates()
    print(f"保存后模板数量: {len(templates)}")
    
    # 显示所有模板
    print("\n所有模板:")
    for template in templates:
        print(f"  - {template['name']}")
    
    # 测试加载上次会话
    print("\n测试会话设置...")
    session_settings = {
        'font_size': 36,
        'color': '#00FF00',
        'position': 'center',
        'opacity': 0.9
    }
    
    if config_manager.save_last_session(session_settings):
        print("✓ 会话设置保存成功")
        
        # 加载会话设置
        loaded_settings = config_manager.load_last_session()
        if loaded_settings:
            print("✓ 会话设置加载成功")
            print(f"  字体大小: {loaded_settings.get('font_size')}")
            print(f"  颜色: {loaded_settings.get('color')}")
            print(f"  位置: {loaded_settings.get('position')}")
            print(f"  透明度: {loaded_settings.get('opacity')}")
        else:
            print("✗ 会话设置加载失败")
    else:
        print("✗ 会话设置保存失败")
    
    # 测试删除模板
    print("\n测试删除模板...")
    if config_manager.delete_template('测试模板'):
        print("✓ 模板删除成功")
    else:
        print("✗ 模板删除失败")
    
    # 检查删除后的模板数量
    templates = config_manager.get_all_templates()
    print(f"删除后模板数量: {len(templates)}")
    
    # 清理测试目录
    try:
        import shutil
        shutil.rmtree(config_dir)
        print(f"\n✓ 测试目录已清理: {config_dir}")
    except Exception as e:
        print(f"\n✗ 清理测试目录失败: {e}")
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_config_manager()