#!/usr/bin/env python
"""
照片水印GUI应用
提供图形界面支持拖拽导入、批量选择等功能
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Optional
import threading
from pathlib import Path
from PIL import Image, ImageTk

# 尝试导入拖拽支持库
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    print("警告: tkinterdnd2未安装，拖拽功能将不可用。请运行: pip install tkinterdnd2")

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from exif_reader import ExifReader
from watermark_processor import WatermarkProcessor, WatermarkPosition


class ImageItem:
    """图片项数据类"""
    def __init__(self, file_path: str, date_text: str = ""):
        self.file_path = file_path
        self.date_text = date_text
        self.thumbnail = None
        self.status = "待处理"  # 待处理、处理中、已完成、失败


class PhotoWatermarkGUI:
    """照片水印GUI应用"""
    
    def __init__(self, root):
        # 初始化窗口
        if DRAG_DROP_AVAILABLE:
            self.root = TkinterDnD.Tk() if not isinstance(root, TkinterDnD.Tk) else root
        else:
            self.root = root
            
        self.setup_window()
        
        # 初始化核心组件
        self.exif_reader = ExifReader()
        self.watermark_processor = WatermarkProcessor()
        
        # 存储导入的图片
        self.image_items: List[ImageItem] = []
        
        # 设置参数的默认值
        self.settings = {
            'font_size': 36,
            'color': '#FFFFFF',
            'position': 'bottom_right',
            'font_path': '',
            'opacity': 1.0,
            'output_format': 'auto'  # 新增输出格式设置
        }
        
        # 创建界面
        self.create_widgets()
        self.setup_drag_drop()
        
    def setup_window(self):
        """设置主窗口"""
        self.root.title("照片水印工具 - GUI版")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # 设置窗口图标（如果有的话）
        try:
            # 这里可以设置应用图标
            pass
        except:
            pass
    
    def create_widgets(self):
        """创建所有界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 左侧控制面板
        self.create_control_panel(main_frame)
        
        # 右侧图片列表区域
        self.create_image_list_area(main_frame)
        
        # 底部状态栏
        self.create_status_bar(main_frame)
        
    def create_control_panel(self, parent):
        """创建左侧控制面板"""
        control_frame = ttk.LabelFrame(parent, text="控制面板", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        control_frame.configure(width=250)
        
        # 文件导入区域
        import_frame = ttk.LabelFrame(control_frame, text="文件导入", padding="5")
        import_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 导入按钮
        ttk.Button(import_frame, text="选择图片文件", 
                  command=self.select_images).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(import_frame, text="选择文件夹", 
                  command=self.select_folder).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        ttk.Button(import_frame, text="清空列表", 
                  command=self.clear_images).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        
        import_frame.columnconfigure(0, weight=1)
        
        # 拖拽提示
        drag_label = ttk.Label(control_frame, text="💡 提示：可直接拖拽图片或文件夹到右侧列表", 
                              foreground="blue", font=("", 9))
        drag_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 水印设置区域
        settings_frame = ttk.LabelFrame(control_frame, text="水印设置", padding="5")
        settings_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 字体大小
        ttk.Label(settings_frame, text="字体大小:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.font_size_var = tk.StringVar(value=str(self.settings['font_size']))
        font_size_spin = ttk.Spinbox(settings_frame, from_=12, to=100, 
                                    textvariable=self.font_size_var, width=10)
        font_size_spin.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 颜色
        ttk.Label(settings_frame, text="颜色:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.color_var = tk.StringVar(value=self.settings['color'])
        color_entry = ttk.Entry(settings_frame, textvariable=self.color_var, width=15)
        color_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 位置
        ttk.Label(settings_frame, text="位置:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.position_var = tk.StringVar(value=self.settings['position'])
        position_combo = ttk.Combobox(settings_frame, textvariable=self.position_var, 
                                     values=['top_left', 'top_center', 'top_right',
                                            'center_left', 'center', 'center_right',
                                            'bottom_left', 'bottom_center', 'bottom_right'],
                                     state="readonly", width=12)
        position_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 透明度
        ttk.Label(settings_frame, text="透明度:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.opacity_var = tk.DoubleVar(value=self.settings['opacity'])
        opacity_scale = ttk.Scale(settings_frame, from_=0.1, to=1.0, 
                                 variable=self.opacity_var, orient=tk.HORIZONTAL)
        opacity_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 透明度显示
        self.opacity_label = ttk.Label(settings_frame, text=f"{self.settings['opacity']:.1f}")
        self.opacity_label.grid(row=4, column=1, sticky=tk.W, pady=2)
        opacity_scale.configure(command=self.update_opacity_label)
        
        # 输出格式
        ttk.Label(settings_frame, text="输出格式:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.output_format_var = tk.StringVar(value=self.settings['output_format'])
        format_combo = ttk.Combobox(settings_frame, textvariable=self.output_format_var,
                                   values=['auto', 'jpeg', 'png'],
                                   state="readonly", width=12)
        format_combo.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 输出格式说明
        format_help = ttk.Label(settings_frame, text="auto: 保持原格式", 
                               foreground="gray", font=("Consolas", 8))
        format_help.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        settings_frame.columnconfigure(1, weight=1)
        
        # 处理按钮区域
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="开始处理", 
                  command=self.start_processing, style="Accent.TButton").grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        button_frame.columnconfigure(0, weight=1)
        
        control_frame.columnconfigure(0, weight=1)
        
    def create_image_list_area(self, parent):
        """创建右侧图片列表区域"""
        list_frame = ttk.LabelFrame(parent, text="图片列表", padding="5")
        list_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建Treeview显示图片列表
        columns = ('文件名', '路径', '日期', '状态')
        self.image_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 设置列
        self.image_tree.heading('文件名', text='文件名')
        self.image_tree.heading('路径', text='完整路径')
        self.image_tree.heading('日期', text='拍摄日期')
        self.image_tree.heading('状态', text='状态')
        
        # 设置列宽
        self.image_tree.column('文件名', width=200)
        self.image_tree.column('路径', width=300)
        self.image_tree.column('日期', width=100)
        self.image_tree.column('状态', width=80)
        
        # 滚动条
        tree_scroll_v = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_tree.yview)
        tree_scroll_h = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.image_tree.xview)
        self.image_tree.configure(yscrollcommand=tree_scroll_v.set, xscrollcommand=tree_scroll_h.set)
        
        # 布局
        self.image_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
    def create_status_bar(self, parent):
        """创建底部状态栏"""
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def setup_drag_drop(self):
        """设置拖拽功能"""
        if DRAG_DROP_AVAILABLE:
            # 绑定拖拽事件到图片列表区域
            self.image_tree.drop_target_register(DND_FILES)
            self.image_tree.dnd_bind('<<Drop>>', self.on_drop)
        else:
            # 如果没有拖拽支持，显示提示
            print("拖拽功能不可用，请使用按钮导入图片")
    
    def update_opacity_label(self, value):
        """更新透明度标签"""
        self.opacity_label.config(text=f"{float(value):.1f}")
    
    def select_images(self):
        """选择图片文件"""
        file_types = [
            ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.webp *.gif *.ico"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("PNG文件", "*.png"),
            ("BMP文件", "*.bmp"),
            ("TIFF文件", "*.tiff *.tif"),
            ("WebP文件", "*.webp"),
            ("GIF文件", "*.gif"),
            ("图标文件", "*.ico"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="选择图片文件",
            filetypes=file_types
        )
        
        if files:
            self.add_images(files)
    
    def select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title="选择包含图片的文件夹")
        if folder:
            self.add_folder_images(folder)
    
    def add_images(self, file_paths):
        """添加图片到列表"""
        new_count = 0
        for file_path in file_paths:
            if self.exif_reader.is_supported_image(file_path):
                # 检查是否已存在
                if not any(item.file_path == file_path for item in self.image_items):
                    # 获取日期信息
                    date_text = self.exif_reader.get_watermark_date(file_path)
                    item = ImageItem(file_path, date_text)
                    self.image_items.append(item)
                    
                    # 添加到树形控件
                    self.image_tree.insert('', 'end', values=(
                        os.path.basename(file_path),
                        file_path,
                        date_text,
                        item.status
                    ))
                    new_count += 1
        
        self.update_status(f"添加了 {new_count} 张图片，总计 {len(self.image_items)} 张")
    
    def add_folder_images(self, folder_path):
        """添加文件夹中的图片"""
        image_files = self.exif_reader.get_image_files(folder_path)
        if image_files:
            self.add_images(image_files)
        else:
            messagebox.showinfo("提示", f"在文件夹 {folder_path} 中未找到支持的图片文件")
    
    def clear_images(self):
        """清空图片列表"""
        if self.image_items and messagebox.askyesno("确认", "确定要清空所有图片吗？"):
            self.image_items.clear()
            # 清空树形控件
            for item in self.image_tree.get_children():
                self.image_tree.delete(item)
            self.update_status("已清空图片列表")
    
    def on_drop(self, event):
        """处理拖拽事件"""
        if not DRAG_DROP_AVAILABLE:
            return
            
        # 获取拖拽的文件路径
        files = self.root.tk.splitlist(event.data)
        
        image_files = []
        folder_paths = []
        
        for file_path in files:
            file_path = file_path.strip('{}')  # 移除可能的大括号
            
            if os.path.isfile(file_path):
                if self.exif_reader.is_supported_image(file_path):
                    image_files.append(file_path)
            elif os.path.isdir(file_path):
                folder_paths.append(file_path)
        
        # 处理文件
        if image_files:
            self.add_images(image_files)
        
        # 处理文件夹
        for folder_path in folder_paths:
            self.add_folder_images(folder_path)
        
        if not image_files and not folder_paths:
            messagebox.showinfo("提示", "未找到支持的图片文件或文件夹")
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def get_current_settings(self):
        """获取当前设置"""
        try:
            return {
                'font_size': int(self.font_size_var.get()),
                'color': self.color_var.get(),
                'position': self.position_var.get(),
                'opacity': self.opacity_var.get(),
                'output_format': self.output_format_var.get(),
                'font_path': None  # 暂时不支持自定义字体路径
            }
        except ValueError as e:
            messagebox.showerror("设置错误", f"设置参数格式错误: {e}")
            return None
    
    def start_processing(self):
        """开始处理图片"""
        if not self.image_items:
            messagebox.showwarning("警告", "请先导入图片文件")
            return
        
        settings = self.get_current_settings()
        if settings is None:
            return
        
        # 在后台线程中处理图片
        threading.Thread(target=self.process_images_thread, args=(settings,), daemon=True).start()
    
    def process_images_thread(self, settings):
        """在后台线程中处理图片"""
        try:
            # 创建输出目录
            if self.image_items:
                first_image_path = self.image_items[0].file_path
                output_dir = self.watermark_processor.create_output_directory(
                    os.path.dirname(first_image_path)
                )
                
                success_count = 0
                total_count = len(self.image_items)
                
                for i, item in enumerate(self.image_items):
                    try:
                        # 更新状态
                        self.root.after(0, lambda idx=i: self.update_item_status(idx, "处理中"))
                        self.root.after(0, lambda: self.update_status(f"正在处理 {i+1}/{total_count}: {os.path.basename(item.file_path)}"))
                        
                        # 处理图片
                        position = self.get_position_from_string(settings['position'])
                        output_path = self.watermark_processor.process_single_image(
                            image_path=item.file_path,
                            date_text=item.date_text,
                            output_dir=output_dir,
                            font_size=settings['font_size'],
                            color=settings['color'],
                            position=position,
                            font_path=settings['font_path'],
                            opacity=settings['opacity'],
                            output_format=settings['output_format']
                        )
                        
                        # 更新成功状态
                        self.root.after(0, lambda idx=i: self.update_item_status(idx, "已完成"))
                        success_count += 1
                        
                    except Exception as e:
                        # 更新失败状态
                        self.root.after(0, lambda idx=i, err=str(e): self.update_item_status(idx, f"失败: {err}"))
                
                # 完成提示
                self.root.after(0, lambda: self.update_status(f"处理完成！成功 {success_count}/{total_count} 张，输出目录: {output_dir}"))
                self.root.after(0, lambda: messagebox.showinfo("完成", f"处理完成！\n成功: {success_count}/{total_count} 张\n输出目录: {output_dir}"))
                
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理过程中出现错误: {e}"))
            self.root.after(0, lambda: self.update_status("处理失败"))
    
    def update_item_status(self, index, status):
        """更新指定项目的状态"""
        if 0 <= index < len(self.image_items):
            self.image_items[index].status = status
            # 更新树形控件中对应行的状态
            items = self.image_tree.get_children()
            if index < len(items):
                item_id = items[index]
                values = list(self.image_tree.item(item_id)['values'])
                values[3] = status  # 状态列
                self.image_tree.item(item_id, values=values)
    
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
            'bottom_right': WatermarkPosition.BOTTOM_RIGHT
        }
        
        return position_map.get(position_str.lower(), WatermarkPosition.BOTTOM_RIGHT)


def main():
    """主函数"""
    if DRAG_DROP_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        
    app = PhotoWatermarkGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()