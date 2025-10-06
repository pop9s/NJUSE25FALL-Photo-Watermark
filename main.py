#!/usr/bin/env python
"""
照片水印添加工具
从图片EXIF信息中提取拍摄日期，并在图片上添加日期水印
"""

import os
import sys
import argparse
from typing import List, Tuple, Optional

# 添加src目录到Python路径（使用相对路径，适配不同环境）
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

# 添加当前目录和src目录到Python路径
for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

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
                      font_path: Optional[str] = None, opacity: float = 1.0,
                      output_format: str = "auto", output_dir: Optional[str] = None,
                      jpeg_quality: int = 95, naming_rule: str = "suffix",
                      custom_prefix: str = "wm_", custom_suffix: str = "_watermarked",
                      resize_mode: str = "none", resize_width: Optional[int] = None,
                      resize_height: Optional[int] = None, resize_percent: Optional[float] = None,
                      custom_text: Optional[str] = None, bold: bool = False,
                      italic: bool = False, shadow: bool = False, stroke: bool = False,
                      image_watermark: Optional[str] = None, image_watermark_scale: float = 1.0) -> None:
        """处理图片添加水印"""
        
        print(f"开始处理路径: {input_path}")
        print(f"配置参数: 字体大小={font_size}, 颜色={color}, 位置={position_str}, 透明度={opacity}, 输出格式={output_format}")
        
        if output_dir:
            print(f"输出目录: {output_dir}")
        if jpeg_quality != 95:
            print(f"JPEG质量: {jpeg_quality}")
        if naming_rule != "suffix":
            print(f"命名规则: {naming_rule}")
        if resize_mode != "none":
            print(f"尺寸调整: {resize_mode}")
        
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
            if output_dir:
                # 使用用户指定的输出目录
                if not self.watermark_processor.validate_output_directory(input_path, output_dir):
                    print("错误：不能将文件导出到原文件夹，请选择其他目录")
                    sys.exit(1)
                final_output_dir = output_dir
            else:
                # 使用默认输出目录
                final_output_dir = self.watermark_processor.create_output_directory(input_path)
            print(f"输出目录: {output_dir}")
            
            # 处理每张图片
            success_count = 0
            failed_count = 0
            total_count = len(image_date_pairs)
            
            for idx, (image_path, date_text) in enumerate(image_date_pairs, 1):
                try:
                    print(f"[{idx}/{total_count}] 处理图片: {os.path.basename(image_path)}, 日期: {date_text}")
                    
                    # 准备字体样式参数
                    font_style = {}
                    if bold:
                        font_style['bold'] = True
                    if italic:
                        font_style['italic'] = True
                    
                    output_path = self.watermark_processor.process_single_image(
                        image_path=image_path,
                        date_text=date_text,
                        output_dir=final_output_dir,
                        font_size=font_size,
                        color=color,
                        position=position,
                        font_path=font_path,
                        opacity=opacity,
                        output_format=output_format,
                        quality=jpeg_quality,
                        naming_rule=naming_rule,
                        custom_prefix=custom_prefix,
                        custom_suffix=custom_suffix,
                        resize_mode=resize_mode,
                        resize_width=resize_width,
                        resize_height=resize_height,
                        resize_percent=resize_percent,
                        custom_text=custom_text,
                        font_style=font_style if font_style else None,
                        shadow=shadow,
                        stroke=stroke,
                        image_watermark_path=image_watermark,
                        image_watermark_scale=image_watermark_scale
                    )
                    
                    print(f"  ✅ 已保存: {os.path.basename(output_path)}")
                    success_count += 1
                    
                except Exception as e:
                    print(f"  ❌ 处理失败: {e}")
                    failed_count += 1
            
            print(f"\n🎉 处理完成！")
            print(f"📊 统计: 总计 {total_count} 张图片，成功 {success_count} 张，失败 {failed_count} 张")
            if success_count > 0:
                print(f"💾 水印图片保存在: {final_output_dir}")
            if failed_count > 0:
                print(f"⚠️  有 {failed_count} 张图片处理失败，请检查错误信息")
            
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
    
    parser.add_argument(
        "--output-format", "-of",
        type=str,
        default="auto",
        choices=["auto", "jpeg", "png"],
        help="输出格式 (auto: 保持原格式, jpeg: JPEG格式, png: PNG格式, 默认: auto)"
    )
    
    parser.add_argument(
        "--output-dir", "-od",
        type=str,
        default=None,
        help="输出目录路径 (默认: 在原目录下创建子目录)"
    )
    
    parser.add_argument(
        "--jpeg-quality", "-jq",
        type=int,
        default=95,
        help="JPEG质量 1-100 (默认: 95)"
    )
    
    parser.add_argument(
        "--naming-rule", "-nr",
        type=str,
        default="suffix",
        choices=["original", "prefix", "suffix"],
        help="文件命名规则 (默认: suffix)"
    )
    
    parser.add_argument(
        "--custom-prefix", "-cp",
        type=str,
        default="wm_",
        help="自定义前缀 (默认: wm_)"
    )
    
    parser.add_argument(
        "--custom-suffix", "-cs",
        type=str,
        default="_watermarked",
        help="自定义后缀 (默认: _watermarked)"
    )
    
    parser.add_argument(
        "--resize-mode", "-rm",
        type=str,
        default="none",
        choices=["none", "width", "height", "percent"],
        help="尺寸调整模式 (默认: none)"
    )
    
    parser.add_argument(
        "--resize-width", "-rw",
        type=int,
        default=800,
        help="目标宽度像素 (默认: 800)"
    )
    
    parser.add_argument(
        "--resize-height", "-rh",
        type=int,
        default=600,
        help="目标高度像素 (默认: 600)"
    )
    
    parser.add_argument(
        "--resize-percent", "-rp",
        type=float,
        default=1.0,
        help="缩放百分比 0.1-3.0 (默认: 1.0)"
    )
    
    # 新增自定义文本水印参数
    parser.add_argument(
        "--custom-text", "-ct",
        type=str,
        default=None,
        help="自定义水印文本 (默认: 使用EXIF日期)"
    )
    
    parser.add_argument(
        "--bold", "-b",
        action="store_true",
        help="使用粗体字体"
    )
    
    parser.add_argument(
        "--italic", "-i",
        action="store_true",
        help="使用斜体字体"
    )
    
    parser.add_argument(
        "--shadow", "-sh",
        action="store_true",
        help="添加阴影效果"
    )
    
    parser.add_argument(
        "--stroke", "-st",
        action="store_true",
        help="添加描边效果"
    )
    
    # 新增图片水印参数
    parser.add_argument(
        "--image-watermark", "-iw",
        type=str,
        default=None,
        help="图片水印文件路径 (可选)"
    )
    
    parser.add_argument(
        "--image-watermark-scale", "-iws",
        type=float,
        default=1.0,
        help="图片水印缩放比例 0.1-3.0 (默认: 1.0)"
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
    
    if not (1 <= args.jpeg_quality <= 100):
        print("错误：JPEG质量必须在 1 到 100 之间")
        sys.exit(1)
    
    if not (0.1 <= args.resize_percent <= 3.0):
        print("错误：缩放百分比必须在 0.1 到 3.0 之间")
        sys.exit(1)
    
    # 验证颜色格式
    if not args.color.startswith('#') or len(args.color) != 7:
        print("错误：颜色格式错误，请使用 #RRGGBB 格式（如 #FFFFFF）")
        sys.exit(1)
    
    # 验证字体文件
    if args.font_path and not os.path.exists(args.font_path):
        print(f"错误：字体文件不存在: {args.font_path}")
        sys.exit(1)
    
    # 验证图片水印文件
    if args.image_watermark and not os.path.exists(args.image_watermark):
        print(f"错误：图片水印文件不存在: {args.image_watermark}")
        sys.exit(1)
    
    # 验证图片水印缩放比例
    if not (0.1 <= args.image_watermark_scale <= 3.0):
        print("错误：图片水印缩放比例必须在 0.1 到 3.0 之间")
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
            opacity=args.opacity,
            output_format=args.output_format,
            output_dir=args.output_dir,
            jpeg_quality=args.jpeg_quality,
            naming_rule=args.naming_rule,
            custom_prefix=args.custom_prefix,
            custom_suffix=args.custom_suffix,
            resize_mode=args.resize_mode,
            resize_width=args.resize_width,
            resize_height=args.resize_height,
            resize_percent=args.resize_percent,
            custom_text=args.custom_text,
            bold=args.bold,
            italic=args.italic,
            shadow=args.shadow,
            stroke=args.stroke,
            image_watermark=args.image_watermark,
            image_watermark_scale=args.image_watermark_scale
        )
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"程序执行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()