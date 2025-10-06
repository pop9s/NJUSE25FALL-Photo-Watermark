"""
水印处理模块
用于在图片上添加日期水印
"""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, Optional, Union
from enum import Enum
from pathlib import Path


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
    
    def resize_image(self, image: Image.Image, resize_mode: str = "none", 
                    width: Optional[int] = None, height: Optional[int] = None, 
                    scale_percent: Optional[float] = None) -> Image.Image:
        """
        调整图片尺寸
        
        Args:
            image: 原始图像
            resize_mode: 缩放模式 ("none", "width", "height", "percent")
            width: 目标宽度
            height: 目标高度
            scale_percent: 缩放百分比 (0.1-5.0)
            
        Returns:
            调整后的图像
        """
        if resize_mode == "none":
            return image
            
        original_width, original_height = image.size
        
        if resize_mode == "width" and width:
            # 按宽度缩放，保持宽高比
            scale_ratio = width / original_width
            new_height = int(original_height * scale_ratio)
            new_size = (width, new_height)
            
        elif resize_mode == "height" and height:
            # 按高度缩放，保持宽高比
            scale_ratio = height / original_height
            new_width = int(original_width * scale_ratio)
            new_size = (new_width, height)
            
        elif resize_mode == "percent" and scale_percent:
            # 按百分比缩放
            new_width = int(original_width * scale_percent)
            new_height = int(original_height * scale_percent)
            new_size = (new_width, new_height)
            
        else:
            return image
        
        # 使用高质量重采样
        try:
            return image.resize(new_size, Image.Resampling.LANCZOS)
        except AttributeError:
            # 兼容较旧版本的Pillow
            return image.resize(new_size, Image.Resampling.LANCZOS)
    
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
    
    def get_font(self, font_size: int, font_path: Optional[str] = None, font_style: Optional[dict[str, bool]] = None):
        """获取字体对象"""
        try:
            # 处理字体样式
            if font_style:
                # 这里我们尝试通过字体文件名来支持粗体和斜体
                # 在实际应用中，可能需要更复杂的字体匹配逻辑
                if font_path and os.path.exists(font_path):
                    return ImageFont.truetype(font_path, font_size)
                else:
                    # 尝试使用系统默认字体
                    try:
                        # Windows系统尝试使用微软雅黑
                        font_name = "msyh.ttc"
                        if font_style.get('bold') and font_style.get('italic'):
                            font_name = "msyhbd.ttc"  # 粗体+斜体
                        elif font_style.get('bold'):
                            font_name = "msyhbd.ttc"  # 粗体
                        elif font_style.get('italic'):
                            # Windows微软雅黑斜体可能需要其他处理
                            pass
                        return ImageFont.truetype(font_name, font_size)
                    except OSError:
                        try:
                            # 尝试使用Arial字体
                            font_name = "arial.ttf"
                            if font_style.get('bold') and font_style.get('italic'):
                                font_name = "arialbi.ttf"  # 粗体+斜体
                            elif font_style.get('bold'):
                                font_name = "arialbd.ttf"  # 粗体
                            elif font_style.get('italic'):
                                font_name = "ariali.ttf"   # 斜体
                            return ImageFont.truetype(font_name, font_size)
                        except OSError:
                            # 如果都失败，使用PIL默认字体
                            return ImageFont.load_default()
            else:
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
                     opacity: float = 1.0,
                     custom_text: Optional[str] = None,
                     font_style: Optional[dict[str, bool]] = None,
                     shadow: bool = False,
                     stroke: bool = False,
                     image_watermark_path: Optional[str] = None,
                     image_watermark_scale: float = 1.0) -> Image.Image:
        """
        在图片上添加水印
        
        Args:
            image_path: 图片路径
            date_text: 水印文本（日期）
            font_size: 字体大小
            color: 文字颜色（十六进制格式，如#FFFFFF）
            position: 水印位置
            font_path: 字体文件路径（可选）
            opacity: 透明度 (0.0-1.0)
            custom_text: 自定义水印文本（可选）
            font_style: 字体样式字典，支持 'bold', 'italic' 键
            shadow: 是否添加阴影效果
            stroke: 是否添加描边效果
            image_watermark_path: 图片水印路径（可选）
            image_watermark_scale: 图片水印缩放比例（0.0-1.0）
            
        Returns:
            带水印的PIL图像对象
        """
        # 打开图片
        try:
            image = Image.open(image_path)
            original_mode = image.mode
            has_transparency = 'transparency' in image.info or original_mode in ('RGBA', 'LA')
            
            # 处理不同的图像模式
            if original_mode == 'P':  # 调色板模式
                if has_transparency:
                    image = image.convert('RGBA')
                else:
                    image = image.convert('RGB')
            elif original_mode in ('L', 'LA'):  # 灰度模式
                if has_transparency or original_mode == 'LA':
                    image = image.convert('RGBA')
                else:
                    image = image.convert('RGB')
            elif original_mode in ('1', 'P'):
                image = image.convert('RGB')
            elif original_mode not in ('RGB', 'RGBA'):
                # 其他不常见模式，尝试转换为RGB
                image = image.convert('RGB')
        except Exception as e:
            raise ValueError(f"无法打开图片文件 {image_path}: {e}")
        
        # 判断是否需要保持透明通道
        preserve_alpha = image.mode == 'RGBA'
        
        # 如果提供了图片水印路径，则使用图片水印
        if image_watermark_path and os.path.exists(image_watermark_path):
            try:
                # 打开水印图片
                watermark_image = Image.open(image_watermark_path)
                
                # 转换为RGBA模式以支持透明通道
                if watermark_image.mode != 'RGBA':
                    watermark_image = watermark_image.convert('RGBA')
                
                # 根据缩放比例调整水印图片大小
                if image_watermark_scale != 1.0:
                    original_size = watermark_image.size
                    new_size = (int(original_size[0] * image_watermark_scale), int(original_size[1] * image_watermark_scale))
                    watermark_image = watermark_image.resize(new_size, Image.Resampling.LANCZOS)
                
                # 应用水印透明度
                if opacity < 1.0:
                    # 分离alpha通道并调整透明度
                    alpha = watermark_image.split()[-1]  # 获取alpha通道
                    alpha = alpha.point(lambda p: int(p * opacity))  # 调整透明度
                    watermark_image.putalpha(alpha)
                
                # 计算水印位置
                img_width, img_height = image.size
                wm_width, wm_height = watermark_image.size
                x, y = self.calculate_position(image.size, watermark_image.size, position)
                
                # 创建临时图像用于粘贴水印
                if image.mode != 'RGBA':
                    temp_image = image.convert('RGBA')
                else:
                    temp_image = image.copy()
                
                # 粘贴水印图片
                temp_image.paste(watermark_image, (x, y), watermark_image)
                
                # 如果原图不是RGBA模式，转换回原模式
                if image.mode != 'RGBA':
                    if image.mode == 'RGB':
                        image = temp_image.convert('RGB')
                    elif image.mode == 'P':
                        image = temp_image.convert('P')
                    else:
                        image = temp_image.convert(image.mode)
                else:
                    image = temp_image
                
                return image
                
            except Exception as e:
                print(f"处理图片水印时出错: {e}")
                # 如果图片水印处理失败，继续使用文本水印
                pass
        
        # 创建绘图对象
        draw = ImageDraw.Draw(image)
        
        # 获取字体
        font = self.get_font(font_size, font_path, font_style)
        
        # 应用字体样式（如果需要）
        if font_style:
            # 注意：PIL的字体样式支持有限，这里只是预留接口
            pass
        
        # 确定使用的文本
        watermark_text = custom_text if custom_text is not None else date_text
        
        # 转换颜色
        try:
            rgb_color = self.hex_to_rgb(color)
        except ValueError:
            print(f"颜色格式错误，使用默认白色: {color}")
            rgb_color = (255, 255, 255)
        
        # 如果需要透明度，创建带alpha通道的颜色
        if opacity < 1.0 or shadow or stroke:
            alpha = int(255 * opacity) if opacity < 1.0 else 255
            rgba_color = rgb_color + (alpha,)
            
            # 创建透明水印层
            watermark_layer = Image.new('RGBA', image.size, (0, 0, 0, 0))
            watermark_draw = ImageDraw.Draw(watermark_layer)
            
            # 计算文本位置
            text_size = self.get_text_size(watermark_text, font)
            text_position = self.calculate_position(image.size, text_size, position)
            
            # 添加阴影效果
            if shadow:
                shadow_offset = max(1, font_size // 20)  # 阴影偏移量
                shadow_color = (0, 0, 0, int(alpha * 0.5))  # 半透明黑色阴影
                watermark_draw.text((text_position[0] + shadow_offset, text_position[1] + shadow_offset), 
                                  watermark_text, font=font, fill=shadow_color)
            
            # 添加描边效果
            if stroke:
                stroke_color = (0, 0, 0, alpha)  # 黑色描边
                stroke_width = max(1, font_size // 30)  # 描边宽度
                # 绘制多个方向的描边
                for dx in range(-stroke_width, stroke_width + 1):
                    for dy in range(-stroke_width, stroke_width + 1):
                        if dx != 0 or dy != 0:
                            watermark_draw.text((text_position[0] + dx, text_position[1] + dy), 
                                              watermark_text, font=font, fill=stroke_color)
            
            # 在透明层上绘制文本
            watermark_draw.text(text_position, watermark_text, font=font, fill=rgba_color)
            
            # 将透明层合并到原图
            if not preserve_alpha:
                image = image.convert('RGBA')
            image = Image.alpha_composite(image, watermark_layer)
            
            # 如果原图不是透明的，可以选择转回RGB
            if not preserve_alpha:
                # 这里保持RGBA，让用户在保存时选择格式
                pass
        else:
            # 直接在图片上绘制文本
            text_size = self.get_text_size(watermark_text, font)
            text_position = self.calculate_position(image.size, text_size, position)
            draw.text(text_position, watermark_text, font=font, fill=rgb_color)
        
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
    
    def generate_output_filename(self, original_path: str, naming_rule: str = "suffix",
                                custom_prefix: str = "wm_", custom_suffix: str = "_watermarked",
                                output_format: str = "auto") -> str:
        """
        生成输出文件名
        
        Args:
            original_path: 原始文件路径
            naming_rule: 命名规则 ("original", "prefix", "suffix")
            custom_prefix: 自定义前缀
            custom_suffix: 自定义后缀
            output_format: 输出格式
            
        Returns:
            输出文件名
        """
        filename = os.path.basename(original_path)
        name, original_ext = os.path.splitext(filename)
        
        # 决定输出扩展名
        if output_format.lower() == "auto":
            ext = original_ext
        elif output_format.lower() == "jpeg":
            ext = '.jpg'
        elif output_format.lower() == "png":
            ext = '.png'
        else:
            ext = original_ext
        
        # 根据命名规则生成文件名
        if naming_rule == "original":
            # 保持原文件名
            output_filename = name + ext
        elif naming_rule == "prefix":
            # 添加前缀
            output_filename = custom_prefix + name + ext
        elif naming_rule == "suffix":
            # 添加后缀
            output_filename = name + custom_suffix + ext
        else:
            # 默认使用后缀
            output_filename = name + custom_suffix + ext
        
        return output_filename
    
    def validate_output_directory(self, input_path: str, output_dir: str) -> bool:
        """
        验证输出目录是否合法（不能与原文件夹相同）
        
        Args:
            input_path: 输入文件或目录路径
            output_dir: 输出目录路径
            
        Returns:
            是否合法
        """
        try:
            # 获取输入文件的目录
            if os.path.isfile(input_path):
                input_dir = os.path.dirname(os.path.abspath(input_path))
            else:
                input_dir = os.path.abspath(input_path)
            
            output_dir_abs = os.path.abspath(output_dir)
            
            # 比较路径是否相同
            return os.path.normpath(input_dir) != os.path.normpath(output_dir_abs)
        except Exception:
            return True  # 如果无法判断，允许继续
    
    def save_watermarked_image(self, image: Image.Image, original_path: str, 
                              output_dir: str, output_format: str = "auto",
                              quality: int = 95, naming_rule: str = "suffix",
                              custom_prefix: str = "wm_", 
                              custom_suffix: str = "_watermarked") -> str:
        """
        保存带水印的图片
        
        Args:
            image: 带水印的图像对象
            original_path: 原始文件路径
            output_dir: 输出目录
            output_format: 输出格式 ("auto", "jpeg", "png")
            quality: JPEG质量 (1-100)
            naming_rule: 命名规则 ("original", "prefix", "suffix")
            custom_prefix: 自定义前缀
            custom_suffix: 自定义后缀
        
        Returns:
            输出文件路径
        """
        # 生成输出文件名
        output_filename = self.generate_output_filename(
            original_path, naming_rule, custom_prefix, custom_suffix, output_format
        )
        output_path = os.path.join(output_dir, output_filename)
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 决定保存格式
        _, ext = os.path.splitext(output_filename)
        if ext.lower() in ['.jpg', '.jpeg']:
            save_format = 'JPEG'
        elif ext.lower() == '.png':
            save_format = 'PNG'
        elif ext.lower() in ['.tiff', '.tif']:
            save_format = 'TIFF'
        elif ext.lower() == '.bmp':
            save_format = 'BMP'
        elif ext.lower() == '.webp':
            save_format = 'WEBP'
        else:
            save_format = 'JPEG'  # 默认
        
        # 保存图片
        try:
            if save_format == 'JPEG':
                # JPEG不支持透明通道，需要转换
                if image.mode in ('RGBA', 'LA'):
                    # 创建白色背景
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[3])  # 使用alpha通道作为遮罩
                    else:
                        background.paste(image)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(output_path, save_format, quality=quality)
            elif save_format == 'PNG':
                # PNG支持透明通道
                if image.mode not in ('RGBA', 'RGB', 'L', 'LA', 'P'):
                    image = image.convert('RGBA')
                image.save(output_path, save_format)
            elif save_format == 'TIFF':
                # TIFF支持多种模式
                image.save(output_path, save_format)
            elif save_format == 'BMP':
                # BMP不支持透明通道
                if image.mode in ('RGBA', 'LA'):
                    image = image.convert('RGB')
                image.save(output_path, save_format)
            elif save_format == 'WEBP':
                # WebP支持透明通道
                image.save(output_path, save_format, quality=quality)
            else:
                # 默认情况
                image.save(output_path, save_format)
            
            return output_path
        except Exception as e:
            raise ValueError(f"保存图片失败 {output_path}: {e}")
        """
        保存带水印的图片
        
        Args:
            image: 带水印的图像对象
            original_path: 原始文件路径
            output_dir: 输出目录
            output_format: 输出格式 ("auto", "jpeg", "png")
            quality: JPEG质量 (1-100)
        
        Returns:
            输出文件路径
        """
        # 获取原文件名和扩展名
        filename = os.path.basename(original_path)
        name, original_ext = os.path.splitext(filename)
        
        # 决定输出格式和扩展名
        if output_format.lower() == "auto":
            # 自动模式：保持原格式
            if original_ext.lower() in ['.jpg', '.jpeg']:
                save_format = 'JPEG'
                ext = '.jpg'
            elif original_ext.lower() == '.png':
                save_format = 'PNG'
                ext = '.png'
            elif original_ext.lower() in ['.tiff', '.tif']:
                save_format = 'TIFF'
                ext = '.tiff'
            elif original_ext.lower() == '.bmp':
                save_format = 'BMP'
                ext = '.bmp'
            elif original_ext.lower() == '.webp':
                save_format = 'WEBP'
                ext = '.webp'
            else:
                # 默认保存为JPEG
                save_format = 'JPEG'
                ext = '.jpg'
        elif output_format.lower() == "jpeg":
            save_format = 'JPEG'
            ext = '.jpg'
        elif output_format.lower() == "png":
            save_format = 'PNG'
            ext = '.png'
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
        
        # 生成输出文件名
        output_filename = f"{name}_watermarked{ext}"
        output_path = os.path.join(output_dir, output_filename)
        
        # 保存图片
        try:
            if save_format == 'JPEG':
                # JPEG不支持透明通道，需要转换
                if image.mode in ('RGBA', 'LA'):
                    # 创建白色背景
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'RGBA':
                        background.paste(image, mask=image.split()[3])  # 使用alpha通道作为遮罩
                    else:
                        background.paste(image)
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(output_path, save_format, quality=quality)
            elif save_format == 'PNG':
                # PNG支持透明通道
                if image.mode not in ('RGBA', 'RGB', 'L', 'LA', 'P'):
                    image = image.convert('RGBA')
                image.save(output_path, save_format)
            elif save_format == 'TIFF':
                # TIFF支持多种模式
                image.save(output_path, save_format)
            elif save_format == 'BMP':
                # BMP不支持透明通道
                if image.mode in ('RGBA', 'LA'):
                    image = image.convert('RGB')
                image.save(output_path, save_format)
            elif save_format == 'WEBP':
                # WebP支持透明通道
                image.save(output_path, save_format, quality=quality)
            else:
                # 默认情况
                image.save(output_path, save_format)
            
            return output_path
        except Exception as e:
            raise ValueError(f"保存图片失败 {output_path}: {e}")
    
    def process_single_image(self, image_path: str, date_text: str, output_dir: str,
                           font_size: int = 36, color: str = "#FFFFFF",
                           position: WatermarkPosition = WatermarkPosition.BOTTOM_RIGHT,
                           font_path: Optional[str] = None,
                           opacity: float = 1.0,
                           output_format: str = "auto",
                           quality: int = 95,
                           naming_rule: str = "suffix",
                           custom_prefix: str = "wm_",
                           custom_suffix: str = "_watermarked",
                           resize_mode: str = "none",
                           resize_width: Optional[int] = None,
                           resize_height: Optional[int] = None,
                           resize_percent: Optional[float] = None,
                           custom_text: Optional[str] = None,
                           font_style: Optional[dict[str, bool]] = None,
                           shadow: bool = False,
                           stroke: bool = False,
                           image_watermark_path: Optional[str] = None,
                           image_watermark_scale: float = 1.0) -> str:
        """处理单张图片"""
        # 添加水印
        watermarked_image = self.add_watermark(
            image_path, date_text, font_size, color, position, font_path, opacity,
            custom_text, font_style, shadow, stroke, image_watermark_path, image_watermark_scale
        )
        
        # 调整图片尺寸
        if resize_mode != "none":
            watermarked_image = self.resize_image(
                watermarked_image, resize_mode, resize_width, resize_height, resize_percent
            )
        
        # 保存图片
        output_path = self.save_watermarked_image(
            watermarked_image, image_path, output_dir, output_format, 
            quality, naming_rule, custom_prefix, custom_suffix
        )
        
        return output_path