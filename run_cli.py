#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IDE运行入口脚本 - 命令行版本
用于IDE调试和测试命令行功能
"""

import os
import sys

# 确保工作目录为脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 添加项目路径到Python路径
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# 模拟命令行参数进行测试
def test_cli():
    """测试命令行功能"""
    print("🚀 启动照片水印命令行测试...")
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"🐍 Python版本: {sys.version}")
    
    # 模拟命令行参数
    test_args = [
        "main.py",
        "test_formats",  # 使用测试图片目录
        "--font-size", "36",
        "--color", "#FFFFFF",
        "--position", "bottom_right",
        "--output-format", "auto"
    ]
    
    # 设置模拟参数
    sys.argv = test_args
    
    try:
        from main import main
        main()
    except SystemExit:
        print("✅ 命令行测试完成")
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保安装了所有依赖：pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 运行失败: {e}")

if __name__ == "__main__":
    test_cli()