"""
EXIF信息读取模块
用于从图片文件中提取拍摄时间信息
"""

import os
import piexif
from datetime import datetime
from typing import Optional, List, Tuple


class ExifReader:
    """EXIF信息读取器"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.tiff', '.tif'}
    
    def __init__(self):
        pass
    
    def is_supported_image(self, file_path: str) -> bool:
        """检查文件是否为支持的图片格式"""
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.SUPPORTED_FORMATS
    
    def get_image_files(self, directory: str) -> List[str]:
        """获取目录下所有支持的图片文件"""
        image_files = []
        
        if not os.path.exists(directory):
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        if os.path.isfile(directory):
            # 如果输入的是单个文件
            if self.is_supported_image(directory):
                image_files.append(directory)
        else:
            # 如果输入的是目录
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path) and self.is_supported_image(filename):
                    image_files.append(file_path)
        
        return image_files
    
    def extract_date_from_exif(self, image_path: str) -> Optional[str]:
        """
        从图片EXIF信息中提取拍摄日期
        返回格式: YYYY-MM-DD
        """
        try:
            # 读取EXIF数据
            exif_data = piexif.load(image_path)
            
            # 尝试从多个可能的EXIF字段获取日期时间
            date_fields = [
                piexif.ExifIFD.DateTimeOriginal,  # 原始拍摄时间
                piexif.ExifIFD.DateTime,          # 修改时间  
                piexif.ImageIFD.DateTime          # 图片时间
            ]
            
            date_str = None
            
            # 首先尝试从Exif字段获取
            if "Exif" in exif_data:
                for field in date_fields[:2]:  # DateTimeOriginal 和 DateTime
                    if field in exif_data["Exif"]:
                        date_str = exif_data["Exif"][field].decode('utf-8')
                        break
            
            # 如果Exif中没有，尝试从0th字段获取
            if not date_str and "0th" in exif_data:
                if piexif.ImageIFD.DateTime in exif_data["0th"]:
                    date_str = exif_data["0th"][piexif.ImageIFD.DateTime].decode('utf-8')
            
            if date_str:
                # EXIF日期格式通常为: "YYYY:MM:DD HH:MM:SS"
                # 转换为标准格式: "YYYY-MM-DD"
                date_part = date_str.split(' ')[0]  # 只取日期部分
                formatted_date = date_part.replace(':', '-')
                
                # 验证日期格式是否正确
                try:
                    datetime.strptime(formatted_date, '%Y-%m-%d')
                    return formatted_date
                except ValueError:
                    pass
            
            return None
            
        except Exception as e:
            print(f"读取EXIF信息失败 {image_path}: {e}")
            return None
    
    def get_file_modification_date(self, image_path: str) -> str:
        """获取文件修改日期作为备选方案"""
        try:
            timestamp = os.path.getmtime(image_path)
            date_obj = datetime.fromtimestamp(timestamp)
            return date_obj.strftime('%Y-%m-%d')
        except Exception:
            # 如果获取失败，返回当前日期
            return datetime.now().strftime('%Y-%m-%d')
    
    def get_watermark_date(self, image_path: str) -> str:
        """
        获取用于水印的日期
        优先使用EXIF中的拍摄日期，如果没有则使用文件修改日期
        """
        exif_date = self.extract_date_from_exif(image_path)
        if exif_date:
            return exif_date
        else:
            print(f"未找到EXIF拍摄日期，使用文件修改日期: {os.path.basename(image_path)}")
            return self.get_file_modification_date(image_path)
    
    def process_images(self, input_path: str) -> List[Tuple[str, str]]:
        """
        处理输入路径中的所有图片，返回 (图片路径, 日期) 的列表
        """
        image_files = self.get_image_files(input_path)
        
        if not image_files:
            raise ValueError(f"在路径 {input_path} 中未找到支持的图片文件")
        
        results = []
        for image_path in image_files:
            date = self.get_watermark_date(image_path)
            results.append((image_path, date))
        
        return results