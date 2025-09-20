#!/usr/bin/env python3
"""
照片水印添加工具
从图片EXIF信息中提取拍摄日期，并在图片上添加日期水印
"""

import os
import sys
import argparse
from typing import List, Tuple, Optional

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from exif_reader import ExifReader
from watermark_processor import WatermarkProcessor, WatermarkPosition


class PhotoWatermarkApp:
    """照片水印应用主类"""
    
    def __init__(self):
        self.exif_reader = ExifReader()
        self.watermark_processor = WatermarkProcessor()
    
    def get_position_from_string(self, position_str: str) -> WatermarkPosition:
        """将字符串转换为位置枚举"""
        position_map = {
            'top_left': WatermarkPosition.TOP_LEFT,
            'top_center': WatermarkPosition.TOP_CENTER,
            'top_right': WatermarkPosition.TOP_RIGHT,
            'center_left': WatermarkPosition.CENTER_LEFT,
            'center': WatermarkPosition.CENTER,
            'center_right': WatermarkPosition.CENTER_RIGHT,
            'bottom_left': WatermarkPosition.BOTTOM_LEFT,
            'bottom_center': WatermarkPosition.BOTTOM_CENTER,
            'bottom_right': WatermarkPosition.BOTTOM_RIGHT,
            '左上': WatermarkPosition.TOP_LEFT,
            '上中': WatermarkPosition.TOP_CENTER,
            '右上': WatermarkPosition.TOP_RIGHT,
            '左中': WatermarkPosition.CENTER_LEFT,
            '居中': WatermarkPosition.CENTER,
            '右中': WatermarkPosition.CENTER_RIGHT,
            '左下': WatermarkPosition.BOTTOM_LEFT,
            '下中': WatermarkPosition.BOTTOM_CENTER,
            '右下': WatermarkPosition.BOTTOM_RIGHT
        }
        
        position_str = position_str.lower().strip()
        if position_str in position_map:
            return position_map[position_str]
        else:
            print(f"警告：未识别的位置 '{position_str}'，使用默认位置 '右下'")
            return WatermarkPosition.BOTTOM_RIGHT
    
    def process_images(self, input_path: str, font_size: int = 36, 
                      color: str = "#FFFFFF", position_str: str = "bottom_right",
                      font_path: Optional[str] = None, opacity: float = 1.0) -> None:
        """处理图片添加水印"""
        
        print(f"开始处理路径: {input_path}")
        
        # 验证输入路径
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"路径不存在: {input_path}")
        
        # 获取水印位置
        position = self.get_position_from_string(position_str)
        
        try:
            # 读取图片和日期信息
            print("正在读取图片EXIF信息...")
            image_date_pairs = self.exif_reader.process_images(input_path)
            
            if not image_date_pairs:
                print("未找到任何支持的图片文件")
                return
            
            print(f"找到 {len(image_date_pairs)} 个图片文件")
            
            # 创建输出目录
            output_dir = self.watermark_processor.create_output_directory(input_path)
            print(f"输出目录: {output_dir}")
            
            # 处理每张图片
            success_count = 0
            failed_count = 0
            
            for image_path, date_text in image_date_pairs:
                try:
                    print(f"处理图片: {os.path.basename(image_path)}, 日期: {date_text}")
                    
                    output_path = self.watermark_processor.process_single_image(
                        image_path=image_path,
                        date_text=date_text,
                        output_dir=output_dir,
                        font_size=font_size,
                        color=color,
                        position=position,
                        font_path=font_path,
                        opacity=opacity
                    )
                    
                    print(f"  -> 已保存: {os.path.basename(output_path)}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  -> 处理失败: {e}")
                    failed_count += 1
            
            print(f"\n处理完成！成功: {success_count}, 失败: {failed_count}")
            print(f"水印图片保存在: {output_dir}")
            
        except Exception as e:
            print(f"处理过程中出现错误: {e}")
            sys.exit(1)


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="为照片添加基于EXIF拍摄日期的水印",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py "/path/to/photos"
  python main.py "/path/to/photo.jpg" --font-size 48 --color "#FF0000"
  python main.py "/path/to/photos" --position "top_left" --opacity 0.8

支持的位置:
  top_left, top_center, top_right
  center_left, center, center_right  
  bottom_left, bottom_center, bottom_right
  或中文: 左上, 上中, 右上, 左中, 居中, 右中, 左下, 下中, 右下
        """
    )
    
    parser.add_argument(
        "input_path",
        help="输入图片文件路径或包含图片的目录路径"
    )
    
    parser.add_argument(
        "--font-size", "-s",
        type=int,
        default=36,
        help="水印字体大小 (默认: 36)"
    )
    
    parser.add_argument(
        "--color", "-c",
        type=str,
        default="#FFFFFF",
        help="水印文字颜色，十六进制格式 (默认: #FFFFFF 白色)"
    )
    
    parser.add_argument(
        "--position", "-p",
        type=str,
        default="bottom_right",
        help="水印位置 (默认: bottom_right)"
    )
    
    parser.add_argument(
        "--font-path", "-f",
        type=str,
        default=None,
        help="自定义字体文件路径 (可选)"
    )
    
    parser.add_argument(
        "--opacity", "-o",
        type=float,
        default=1.0,
        help="水印透明度 0.0-1.0 (默认: 1.0 不透明)"
    )
    
    return parser


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    # 验证参数
    if not (0.0 <= args.opacity <= 1.0):
        print("错误：透明度必须在 0.0 到 1.0 之间")
        sys.exit(1)
    
    if args.font_size <= 0:
        print("错误：字体大小必须大于 0")
        sys.exit(1)
    
    # 验证颜色格式
    if not args.color.startswith('#') or len(args.color) != 7:
        print("错误：颜色格式错误，请使用 #RRGGBB 格式（如 #FFFFFF）")
        sys.exit(1)
    
    # 验证字体文件
    if args.font_path and not os.path.exists(args.font_path):
        print(f"错误：字体文件不存在: {args.font_path}")
        sys.exit(1)
    
    # 创建应用实例并处理图片
    app = PhotoWatermarkApp()
    
    try:
        app.process_images(
            input_path=args.input_path,
            font_size=args.font_size,
            color=args.color,
            position_str=args.position,
            font_path=args.font_path,
            opacity=args.opacity
        )
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"程序执行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()