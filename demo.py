#!/usr/bin/env python3
"""
演示脚本：展示各种水印效果
"""

import os
import sys
import subprocess

def run_demo():
    """运行演示"""
    
    print("🖼️  照片水印工具演示")
    print("=" * 50)
    
    # 确保有测试图片
    if not os.path.exists("examples"):
        print("正在创建测试图片...")
        subprocess.run([sys.executable, "test_app.py"], check=True)
    
    examples_dir = "examples"
    
    demos = [
        {
            "name": "基本水印（右下角白色）",
            "cmd": f'python main.py "{examples_dir}"'
        },
        {
            "name": "大字体红色水印（左上角）",
            "cmd": f'python main.py "{examples_dir}" --font-size 48 --color "#FF0000" --position "top_left"'
        },
        {
            "name": "居中半透明水印",
            "cmd": f'python main.py "{examples_dir}" --position "center" --opacity 0.6 --font-size 40'
        },
        {
            "name": "底部居中蓝色水印", 
            "cmd": f'python main.py "{examples_dir}" --position "bottom_center" --color "#0066CC" --font-size 32'
        }
    ]
    
    for i, demo in enumerate(demos, 1):
        print(f"\n📝 演示 {i}: {demo['name']}")
        print(f"命令: {demo['cmd']}")
        print("-" * 50)
        
        try:
            result = subprocess.run(demo['cmd'], shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 成功！")
                print(result.stdout.strip())
            else:
                print("❌ 失败！")
                print(result.stderr.strip())
        except Exception as e:
            print(f"❌ 执行错误: {e}")
        
        input("\n按回车键继续下一个演示...")
    
    print("\n🎉 所有演示完成！")
    print(f"📁 查看输出结果: {os.path.abspath('examples/examples_watermark')}")

if __name__ == "__main__":
    run_demo()