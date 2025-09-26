#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IDE运行入口脚本 - GUI版本
确保工作目录正确并启动GUI应用
"""

import os
import sys

# 确保工作目录为脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 添加项目路径到Python路径
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# 导入并运行GUI应用
try:
    from gui_app import main
    print("🚀 启动照片水印GUI应用...")
    print(f"📁 工作目录: {os.getcwd()}")
    print(f"🐍 Python版本: {sys.version}")
    main()
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保安装了所有依赖：pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ 运行失败: {e}")
    sys.exit(1)