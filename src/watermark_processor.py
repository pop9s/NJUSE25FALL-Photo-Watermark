"""
水印处理模块
用于在图片上添加日期水印
"""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, Union
from enum import Enum


class WatermarkPosition(Enum):
    """水印位置枚举"""
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


class WatermarkProcessor:
    """水印处理器"""
    
    def __init__(self):
        pass
    
    def get_text_size(self, text: str, font) -> Tuple[int, int]:
        """获取文本在指定字体下的尺寸"""
        # 创建临时图像来测量文本尺寸
        temp_img = Image.new('RGB', (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        bbox = temp_draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return int(width), int(height)
    
    def calculate_position(self, image_size: Tuple[int, int], text_size: Tuple[int, int], 
                          position: WatermarkPosition, margin: int = 20) -> Tuple[int, int]:
        """根据位置枚举计算文本的实际坐标"""
        img_width, img_height = image_size
        text_width, text_height = text_size
        
        # 计算各个位置的坐标
        positions = {
            WatermarkPosition.TOP_LEFT: (margin, margin),
            WatermarkPosition.TOP_CENTER: ((img_width - text_width) // 2, margin),
            WatermarkPosition.TOP_RIGHT: (img_width - text_width - margin, margin),
            WatermarkPosition.CENTER_LEFT: (margin, (img_height - text_height) // 2),
            WatermarkPosition.CENTER: ((img_width - text_width) // 2, (img_height - text_height) // 2),
            WatermarkPosition.CENTER_RIGHT: (img_width - text_width - margin, (img_height - text_height) // 2),
            WatermarkPosition.BOTTOM_LEFT: (margin, img_height - text_height - margin),
            WatermarkPosition.BOTTOM_CENTER: ((img_width - text_width) // 2, img_height - text_height - margin),
            WatermarkPosition.BOTTOM_RIGHT: (img_width - text_width - margin, img_height - text_height - margin)
        }
        
        return positions[position]
    
    def get_font(self, font_size: int, font_path: Optional[str] = None):
        """获取字体对象"""
        try:
            if font_path and os.path.exists(font_path):
                return ImageFont.truetype(font_path, font_size)
            else:
                # 尝试使用系统默认字体
                try:
                    # Windows系统尝试使用微软雅黑
                    return ImageFont.truetype("msyh.ttc", font_size)
                except OSError:
                    try:
                        # 尝试使用Arial字体
                        return ImageFont.truetype("arial.ttf", font_size)
                    except OSError:
                        # 如果都失败，使用PIL默认字体
                        return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """将十六进制颜色转换为RGB元组"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError("颜色格式错误，请使用#RRGGBB格式")
        
        try:
            rgb_tuple = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return (rgb_tuple[0], rgb_tuple[1], rgb_tuple[2])
        except ValueError:
            raise ValueError("颜色格式错误，请使用#RRGGBB格式")
    
    def add_watermark(self, image_path: str, date_text: str, 
                     font_size: int = 36, color: str = "#FFFFFF", 
                     position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
                     font_path: Optional[str] = None,
                     opacity: float = 1.0) -> Image.Image:
        """
        在图片上添加日期水印
        
        Args:
            image_path: 图片路径
            date_text: 水印文本（日期）
            font_size: 字体大小
            color: 文字颜色（十六进制格式，如#FFFFFF）
            position: 水印位置
            font_path: 字体文件路径（可选）
            opacity: 透明度 (0.0-1.0)
            
        Returns:
            带水印的PIL图像对象
        """
        # 打开图片
        try:
            image = Image.open(image_path)
            # 确保图片为RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
        except Exception as e:
            raise ValueError(f"无法打开图片文件 {image_path}: {e}")
        
        # 创建绘图对象
        draw = ImageDraw.Draw(image)
        
        # 获取字体
        font = self.get_font(font_size, font_path)
        
        # 转换颜色
        try:
            rgb_color = self.hex_to_rgb(color)
        except ValueError:
            print(f"颜色格式错误，使用默认白色: {color}")
            rgb_color = (255, 255, 255)
        
        # 如果需要透明度，创建带alpha通道的颜色
        if opacity < 1.0:
            alpha = int(255 * opacity)
            rgba_color = rgb_color + (alpha,)
            
            # 创建透明水印层
            watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
            watermark_draw = ImageDraw.Draw(watermark_layer)
            
            # 计算文本位置
            text_size = self.get_text_size(date_text, font)
            text_position = self.calculate_position(image.size, text_size, position)
            
            # 在透明层上绘制文本
            watermark_draw.text(text_position, date_text, font=font, fill=rgba_color)
            
            # 将透明层合并到原图
            image = image.convert('RGBA')
            image = Image.alpha_composite(image, watermark_layer)
            image = image.convert('RGB')
        else:
            # 直接在图片上绘制文本
            text_size = self.get_text_size(date_text, font)
            text_position = self.calculate_position(image.size, text_size, position)
            draw.text(text_position, date_text, font=font, fill=rgb_color)
        
        return image
    
    def create_output_directory(self, input_path: str) -> str:
        """创建输出目录"""
        if os.path.isfile(input_path):
            # 如果输入是文件，在文件所在目录创建输出目录
            parent_dir = os.path.dirname(input_path)
            output_dir = os.path.join(parent_dir, os.path.basename(parent_dir) + "_watermark")
        else:
            # 如果输入是目录，在该目录下创建输出目录
            dir_name = os.path.basename(os.path.abspath(input_path))
            output_dir = os.path.join(input_path, dir_name + "_watermark")
        
        # 创建目录
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def save_watermarked_image(self, image: Image.Image, original_path: str, 
                              output_dir: str, quality: int = 95) -> str:
        """保存带水印的图片"""
        # 获取原文件名和扩展名
        filename = os.path.basename(original_path)
        name, ext = os.path.splitext(filename)
        
        # 生成输出文件名
        output_filename = f"{name}_watermarked{ext}"
        output_path = os.path.join(output_dir, output_filename)
        
        # 保存图片
        try:
            if ext.lower() in ['.jpg', '.jpeg']:
                image.save(output_path, 'JPEG', quality=quality)
            elif ext.lower() in ['.png']:
                image.save(output_path, 'PNG')
            elif ext.lower() in ['.tiff', '.tif']:
                image.save(output_path, 'TIFF')
            else:
                image.save(output_path, 'JPEG', quality=quality)
            
            return output_path
        except Exception as e:
            raise ValueError(f"保存图片失败 {output_path}: {e}")
    
    def process_single_image(self, image_path: str, date_text: str, output_dir: str,
                           font_size: int = 36, color: str = "#FFFFFF",
                           position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
                           font_path: Optional[str] = None,
                           opacity: float = 1.0) -> str:
        """处理单张图片"""
        # 添加水印
        watermarked_image = self.add_watermark(
            image_path, date_text, font_size, color, position, font_path, opacity
        )
        
        # 保存图片
        output_path = self.save_watermarked_image(watermarked_image, image_path, output_dir)
        
        return output_path