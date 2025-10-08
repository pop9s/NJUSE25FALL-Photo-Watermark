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
from PIL import Image, ImageTk, ImageDraw, ImageFont

# 尝试导入拖拽支持库
dnd_files_var = None
tkdnd_var = None
drag_drop_available_flag = False
try:
    from tkinterdnd2 import DND_FILES as dnd_files, TkinterDnD as tkdnd
    dnd_files_var = dnd_files
    tkdnd_var = tkdnd
    drag_drop_available_flag = True
except ImportError:
    print("警告: tkinterdnd2未安装，拖拽功能将不可用。请运行: pip install tkinterdnd2")

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from src.exif_reader import ExifReader
from src.watermark_processor import WatermarkProcessor, WatermarkPosition
from src.config_manager import ConfigManager, ConfigManagerUI


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
        self.root = root
            
        self.setup_window()
        
        # 初始化核心组件
        self.exif_reader = ExifReader()
        self.watermark_processor = WatermarkProcessor()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        
        # 存储导入的图片
        self.image_items: List[ImageItem] = []
        
        # 设置参数的默认值
        self.settings = {
            'font_size': 36,
            'color': '#FFFFFF',
            'position': 'bottom_right',
            'font_path': '',
            'opacity': 1.0,
            'output_format': 'auto',  # 输出格式设置
            # 新增导出设置
            'output_dir': '',
            'jpeg_quality': 95,
            'naming_rule': 'suffix',
            'custom_prefix': 'wm_',
            'custom_suffix': '_watermarked',
            'resize_mode': 'none',
            'resize_width': 800,
            'resize_height': 600,
            'resize_percent': 1.0,
            # 新增水印文本设置
            'custom_text': '',
            'font_style_bold': False,
            'font_style_italic': False,
            'shadow': False,
            'stroke': False,
            # 新增图片水印设置
            'image_watermark_path': '',
            'image_watermark_scale': 1.0,
            # 新增旋转设置
            'rotation': 0.0
        }
        
        # 初始化Tk变量
        self.font_size_var = tk.StringVar(value=str(self.settings['font_size']))
        self.color_var = tk.StringVar(value=str(self.settings['color']))
        self.position_var = tk.StringVar(value=str(self.settings['position']))
        self.opacity_var = tk.DoubleVar(value=float(self.settings['opacity']))
        self.output_format_var = tk.StringVar(value=str(self.settings['output_format']))
        self.output_dir_var = tk.StringVar(value=str(self.settings['output_dir']))
        self.naming_rule_var = tk.StringVar(value=str(self.settings['naming_rule']))
        self.custom_prefix_var = tk.StringVar(value=str(self.settings['custom_prefix']))
        self.custom_suffix_var = tk.StringVar(value=str(self.settings['custom_suffix']))
        self.jpeg_quality_var = tk.IntVar(value=int(self.settings['jpeg_quality']))
        self.resize_mode_var = tk.StringVar(value=str(self.settings['resize_mode']))
        self.resize_width_var = tk.IntVar(value=int(self.settings['resize_width']))
        self.resize_height_var = tk.IntVar(value=int(self.settings['resize_height']))
        self.resize_percent_var = tk.DoubleVar(value=float(self.settings['resize_percent']))
        self.custom_text_var = tk.StringVar(value=str(self.settings['custom_text']))
        self.font_style_bold_var = tk.BooleanVar(value=bool(self.settings['font_style_bold']))
        self.font_style_italic_var = tk.BooleanVar(value=bool(self.settings['font_style_italic']))
        self.shadow_var = tk.BooleanVar(value=bool(self.settings['shadow']))
        self.stroke_var = tk.BooleanVar(value=bool(self.settings['stroke']))
        self.image_watermark_path_var = tk.StringVar(value=str(self.settings['image_watermark_path']))
        self.image_watermark_scale_var = tk.DoubleVar(value=float(self.settings['image_watermark_scale']))
        # 新增旋转变量
        self.rotation_var = tk.DoubleVar(value=float(self.settings['rotation']))
        
        # 初始化标签变量
        self.opacity_label = None
        self.jpeg_quality_label = None
        self.resize_percent_label = None
        
        # 初始化其他变量
        self.image_tree: Optional[ttk.Treeview] = None
        self.preview_canvas: Optional[tk.Canvas] = None
        self.preview_photo = None
        self.current_preview_index = None
        self.status_var: Optional[tk.StringVar] = None
        self._window_resize_id = None
        self._preview_update_id = None
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.watermark_position = None  # 用于存储自定义水印位置
        self.watermark_canvas_item = None  # 用于存储水印在画布上的项目
        
        # 初始化字体相关变量
        self.font_path_var = tk.StringVar(value=str(self.settings['font_path']))
        font_display_text = "默认字体" if not self.settings['font_path'] else str(self.settings['font_path'])
        self.font_display_var = tk.StringVar(value=font_display_text)
        self.available_fonts = self.get_system_fonts()
        
        # 创建界面
        self.create_widgets()
        self.setup_drag_drop()
        
        # 绑定图片列表选择事件
        if self.image_tree is not None:
            self.image_tree.bind('<<TreeviewSelect>>', self.on_image_select)
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 加载上次会话设置
        self.load_last_session()
    
    def setup_window(self):
        """设置主窗口"""
        self.root.title("照片水印工具 - GUI版")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        # 设置窗口图标（如果有的话）
        try:
            # 这里可以设置应用图标
            pass
        except:
            pass
        
        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', self.on_window_configure)
        
        # 预览更新延迟ID
        self._preview_update_id = None
    
    def create_widgets(self):
        """创建所有界面组件"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky='ewns')
        
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
        # 创建包含滚动条的容器
        control_container = ttk.Frame(parent)
        control_container.grid(row=0, column=0, rowspan=2, sticky='ewns', padx=(0, 10))
        control_container.configure(width=250)
        control_container.rowconfigure(0, weight=1)
        
        # 创建Canvas和滚动条
        control_canvas = tk.Canvas(control_container, highlightthickness=0)
        control_scrollbar = ttk.Scrollbar(control_container, orient="vertical", command=control_canvas.yview)
        control_scrollable_frame = ttk.Frame(control_canvas)
        
        # 配置滚动区域
        control_scrollable_frame.bind(
            "<Configure>",
            lambda e: control_canvas.configure(
                scrollregion=control_canvas.bbox("all")
            )
        )
        
        # 在Canvas中创建窗口
        control_canvas.create_window((0, 0), window=control_scrollable_frame, anchor="nw")
        control_canvas.configure(yscrollcommand=control_scrollbar.set)
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            control_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            control_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            control_canvas.unbind_all("<MouseWheel>")
        
        control_canvas.bind('<Enter>', _bind_to_mousewheel)
        control_canvas.bind('<Leave>', _unbind_from_mousewheel)
        
        # 布局Canvas和滚动条
        control_canvas.grid(row=0, column=0, sticky='ewns')
        control_scrollbar.grid(row=0, column=1, sticky='ns')
        control_container.columnconfigure(0, weight=1)
        
        # 文件导入区域
        import_frame = ttk.LabelFrame(control_scrollable_frame, text="文件导入", padding="5")
        import_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        # 导入按钮
        ttk.Button(import_frame, text="选择图片文件", 
                  command=self.select_images).grid(row=0, column=0, sticky='ew', pady=2)
        ttk.Button(import_frame, text="选择文件夹", 
                  command=self.select_folder).grid(row=1, column=0, sticky='ew', pady=2)
        ttk.Button(import_frame, text="清空列表", 
                  command=self.clear_images).grid(row=2, column=0, sticky='ew', pady=2)
        
        import_frame.columnconfigure(0, weight=1)
        
        # 拖拽提示
        drag_label = ttk.Label(control_scrollable_frame, text="💡 提示：可直接拖拽图片或文件夹到右侧列表", 
                              foreground="blue", font=("", 9))
        drag_label.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        
        # 水印设置区域
        settings_frame = ttk.LabelFrame(control_scrollable_frame, text="水印设置", padding="5")
        settings_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10))
        
        # 字体大小
        ttk.Label(settings_frame, text="字体大小:").grid(row=0, column=0, sticky=tk.W, pady=2)
        font_size_spin = ttk.Spinbox(settings_frame, from_=12, to=100, 
                                    textvariable=self.font_size_var, width=10)
        font_size_spin.grid(row=0, column=1, sticky='ew', pady=2)
        
        # 颜色
        ttk.Label(settings_frame, text="颜色:").grid(row=1, column=0, sticky=tk.W, pady=2)
        color_frame = ttk.Frame(settings_frame)
        color_frame.grid(row=1, column=1, sticky='ew', pady=2)
        color_frame.columnconfigure(0, weight=1)
        
        color_entry = ttk.Entry(color_frame, textvariable=self.color_var, width=10)
        color_entry.grid(row=0, column=0, sticky='ew', padx=(0, 2))
        
        # 添加颜色选择按钮
        color_button = ttk.Button(color_frame, text="🎨", width=3, command=self.select_color)
        color_button.grid(row=0, column=1)
        
        # 位置
        ttk.Label(settings_frame, text="位置:").grid(row=2, column=0, sticky=tk.W, pady=2)
        position_combo = ttk.Combobox(settings_frame, textvariable=self.position_var, 
                                     values=['top_left', 'top_center', 'top_right',
                                            'center_left', 'center', 'center_right',
                                            'bottom_left', 'bottom_center', 'bottom_right'],
                                     state="readonly", width=12)
        position_combo.grid(row=2, column=1, sticky='ew', pady=2)
        
        # 透明度
        ttk.Label(settings_frame, text="透明度:").grid(row=3, column=0, sticky=tk.W, pady=2)
        opacity_scale = ttk.Scale(settings_frame, from_=0.1, to=1.0, 
                                 variable=self.opacity_var, orient=tk.HORIZONTAL)
        opacity_scale.grid(row=3, column=1, sticky='ew', pady=2)
        
        # 透明度显示
        self.opacity_label = ttk.Label(settings_frame, text=f"{self.settings['opacity']:.1f}")
        self.opacity_label.grid(row=4, column=1, sticky=tk.W, pady=2)
        opacity_scale.configure(command=self.on_opacity_change)
        
        # 九宫格位置按钮
        self.create_position_grid(settings_frame)
        
        # 绑定实时预览更新事件
        self.font_size_var.trace('w', self.on_setting_change)
        self.color_var.trace('w', self.on_setting_change)
        self.position_var.trace('w', self.on_setting_change)
        self.opacity_var.trace('w', self.on_setting_change)
        self.custom_text_var.trace('w', self.on_setting_change)
        self.font_style_bold_var.trace('w', self.on_setting_change)
        self.font_style_italic_var.trace('w', self.on_setting_change)
        self.shadow_var.trace('w', self.on_setting_change)
        self.stroke_var.trace('w', self.on_setting_change)
        self.image_watermark_path_var.trace('w', self.on_setting_change)
        self.image_watermark_scale_var.trace('w', self.on_setting_change)
        # 新增旋转绑定
        self.rotation_var.trace('w', self.on_setting_change)
        # 新增字体路径绑定
        self.font_path_var.trace('w', self.on_setting_change)
        
        # 输出格式
        ttk.Label(settings_frame, text="输出格式:").grid(row=5, column=0, sticky=tk.W, pady=2)
        format_combo = ttk.Combobox(settings_frame, textvariable=self.output_format_var,
                                   values=['auto', 'jpeg', 'png'],
                                   state="readonly", width=12)
        format_combo.grid(row=5, column=1, sticky='ew', pady=2)
        
        # 输出格式说明
        format_help = ttk.Label(settings_frame, text="auto: 保持原格式", 
                               foreground="gray", font=("Consolas", 8))
        format_help.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # 自定义文本
        ttk.Label(settings_frame, text="自定义文本:").grid(row=7, column=0, sticky=tk.W, pady=2)
        custom_text_entry = ttk.Entry(settings_frame, textvariable=self.custom_text_var, width=15)
        custom_text_entry.grid(row=7, column=1, sticky='ew', pady=2)
        
        # 字体选择
        ttk.Label(settings_frame, text="字体:").grid(row=8, column=0, sticky=tk.W, pady=2)
        font_frame = ttk.Frame(settings_frame)
        font_frame.grid(row=8, column=1, sticky='ew', pady=2)
        font_frame.columnconfigure(0, weight=1)
        
        # 字体显示标签
        self.font_display_var = tk.StringVar(value="默认字体" if not self.font_path_var.get() else self.font_path_var.get())
        font_display = ttk.Entry(font_frame, textvariable=self.font_display_var, width=10, state='readonly')
        font_display.grid(row=0, column=0, sticky='ew', padx=(0, 2))
        
        # 字体选择按钮
        font_button = ttk.Button(font_frame, text="选择字体", command=self.select_font)
        font_button.grid(row=0, column=1)
        
        # 字体样式
        ttk.Label(settings_frame, text="字体样式:").grid(row=9, column=0, sticky=tk.W, pady=2)
        
        font_style_frame = ttk.Frame(settings_frame)
        font_style_frame.grid(row=9, column=1, sticky='ew', pady=2)
        
        bold_check = ttk.Checkbutton(font_style_frame, text="粗体", variable=self.font_style_bold_var)
        bold_check.pack(side=tk.LEFT)
        
        italic_check = ttk.Checkbutton(font_style_frame, text="斜体", variable=self.font_style_italic_var)
        italic_check.pack(side=tk.LEFT, padx=(10, 0))
        
        # 阴影和描边效果
        ttk.Label(settings_frame, text="效果:").grid(row=10, column=0, sticky=tk.W, pady=2)
        
        effect_frame = ttk.Frame(settings_frame)
        effect_frame.grid(row=10, column=1, sticky='ew', pady=2)
        
        shadow_check = ttk.Checkbutton(effect_frame, text="阴影", variable=self.shadow_var)
        shadow_check.pack(side=tk.LEFT)
        
        self.stroke_var = tk.BooleanVar(value=bool(self.settings['stroke']))
        stroke_check = ttk.Checkbutton(effect_frame, text="描边", variable=self.stroke_var)
        stroke_check.pack(side=tk.LEFT, padx=(10, 0))
        
        settings_frame.columnconfigure(1, weight=1)
        
        # 初始化拖拽相关变量
        self.drag_data = {"x": 0, "y": 0, "item": None}
        self.watermark_position = None
        self.watermark_canvas_item = None
        
        # 导出设置区域
        export_frame = ttk.LabelFrame(control_scrollable_frame, text="导出设置", padding="5")
        export_frame.grid(row=3, column=0, sticky='ew', pady=(0, 10))
        
        # 输出目录
        ttk.Label(export_frame, text="输出目录:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.output_dir_var = tk.StringVar(value=str(self.settings['output_dir']))
        output_dir_frame = ttk.Frame(export_frame)
        output_dir_frame.grid(row=0, column=1, sticky='ew', pady=2)
        
        output_dir_entry = ttk.Entry(output_dir_frame, textvariable=self.output_dir_var, width=15)
        output_dir_entry.grid(row=0, column=0, sticky='ew', padx=(0, 2))
        ttk.Button(output_dir_frame, text="浏览", command=self.select_output_dir, width=8).grid(row=0, column=1)
        output_dir_frame.columnconfigure(0, weight=1)
        
        # 命名规则
        ttk.Label(export_frame, text="命名规则:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.naming_rule_var = tk.StringVar(value=str(self.settings['naming_rule']))
        naming_combo = ttk.Combobox(export_frame, textvariable=self.naming_rule_var,
                                   values=['original', 'prefix', 'suffix'],
                                   state="readonly", width=12)
        naming_combo.grid(row=1, column=1, sticky='ew', pady=2)
        
        # 自定义前缀
        ttk.Label(export_frame, text="自定义前缀:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.custom_prefix_var = tk.StringVar(value=str(self.settings['custom_prefix']))
        prefix_entry = ttk.Entry(export_frame, textvariable=self.custom_prefix_var, width=15)
        prefix_entry.grid(row=2, column=1, sticky='ew', pady=2)
        
        # 自定义后缀
        ttk.Label(export_frame, text="自定义后缀:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.custom_suffix_var = tk.StringVar(value=str(self.settings['custom_suffix']))
        suffix_entry = ttk.Entry(export_frame, textvariable=self.custom_suffix_var, width=15)
        suffix_entry.grid(row=3, column=1, sticky='ew', pady=2)
        
        # JPEG质量
        ttk.Label(export_frame, text="JPEG质量:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.jpeg_quality_var = tk.IntVar(value=int(self.settings['jpeg_quality']))
        quality_scale = ttk.Scale(export_frame, from_=1, to=100, 
                                 variable=self.jpeg_quality_var, orient=tk.HORIZONTAL)
        quality_scale.grid(row=4, column=1, sticky='ew', pady=2)
        
        # JPEG质量显示
        self.jpeg_quality_label = ttk.Label(export_frame, text=f"{self.settings['jpeg_quality']}")
        self.jpeg_quality_label.grid(row=5, column=1, sticky=tk.W, pady=2)
        quality_scale.configure(command=self.update_jpeg_quality_label)
        
        export_frame.columnconfigure(1, weight=1)
        
        # 图片尺寸调整区域
        resize_frame = ttk.LabelFrame(control_scrollable_frame, text="尺寸调整", padding="5")
        resize_frame.grid(row=4, column=0, sticky='ew', pady=(0, 10))
        
        # 缩放模式
        ttk.Label(resize_frame, text="缩放模式:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.resize_mode_var = tk.StringVar(value=str(self.settings['resize_mode']))
        resize_mode_combo = ttk.Combobox(resize_frame, textvariable=self.resize_mode_var,
                                        values=['none', 'width', 'height', 'percent'],
                                        state="readonly", width=12)
        resize_mode_combo.grid(row=0, column=1, sticky='ew', pady=2)
        
        # 目标宽度
        ttk.Label(resize_frame, text="目标宽度:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.resize_width_var = tk.IntVar(value=int(self.settings['resize_width']))
        width_spin = ttk.Spinbox(resize_frame, from_=100, to=5000, 
                                textvariable=self.resize_width_var, width=10)
        width_spin.grid(row=1, column=1, sticky='ew', pady=2)
        
        # 目标高度
        ttk.Label(resize_frame, text="目标高度:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.resize_height_var = tk.IntVar(value=int(self.settings['resize_height']))
        height_spin = ttk.Spinbox(resize_frame, from_=100, to=5000, 
                                 textvariable=self.resize_height_var, width=10)
        height_spin.grid(row=2, column=1, sticky='ew', pady=2)
        
        # 缩放百分比
        ttk.Label(resize_frame, text="缩放百分比:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.resize_percent_var = tk.DoubleVar(value=float(self.settings['resize_percent']))
        percent_scale = ttk.Scale(resize_frame, from_=0.1, to=3.0, 
                                 variable=self.resize_percent_var, orient=tk.HORIZONTAL)
        percent_scale.grid(row=3, column=1, sticky='ew', pady=2)
        
        # 百分比显示
        self.resize_percent_label = ttk.Label(resize_frame, text=f"{self.settings['resize_percent']:.1f}")
        self.resize_percent_label.grid(row=4, column=1, sticky=tk.W, pady=2)
        percent_scale.configure(command=self.update_resize_percent_label)
        
        resize_frame.columnconfigure(1, weight=1)
        
        # 图片水印设置区域
        image_watermark_frame = ttk.LabelFrame(control_scrollable_frame, text="图片水印设置", padding="5")
        image_watermark_frame.grid(row=5, column=0, sticky='ew', pady=(0, 10))
        
        # 图片水印路径
        ttk.Label(image_watermark_frame, text="水印图片:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.image_watermark_path_var = tk.StringVar(value=str(self.settings['image_watermark_path']))
        image_watermark_frame_row0 = ttk.Frame(image_watermark_frame)
        image_watermark_frame_row0.grid(row=0, column=1, sticky='ew', pady=2)
        
        image_watermark_path_entry = ttk.Entry(image_watermark_frame_row0, textvariable=self.image_watermark_path_var, width=15)
        image_watermark_path_entry.grid(row=0, column=0, sticky='ew', padx=(0, 2))
        ttk.Button(image_watermark_frame_row0, text="浏览", command=self.select_image_watermark, width=8).grid(row=0, column=1)
        image_watermark_frame_row0.columnconfigure(0, weight=1)
        
        # 图片水印缩放比例
        ttk.Label(image_watermark_frame, text="缩放比例:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.image_watermark_scale_var = tk.DoubleVar(value=float(self.settings['image_watermark_scale']))
        image_watermark_scale_spin = ttk.Spinbox(image_watermark_frame, from_=0.1, to=3.0, increment=0.1,
                                textvariable=self.image_watermark_scale_var, width=10)
        image_watermark_scale_spin.grid(row=1, column=1, sticky='ew', pady=2)
        
        # 新增旋转控制
        ttk.Label(image_watermark_frame, text="旋转角度:").grid(row=2, column=0, sticky=tk.W, pady=2)
        rotation_frame = ttk.Frame(image_watermark_frame)
        rotation_frame.grid(row=2, column=1, sticky='ew', pady=2)
        rotation_frame.columnconfigure(0, weight=1)
        
        # 旋转滑块
        rotation_scale = ttk.Scale(rotation_frame, from_=-180, to=180, 
                                  variable=self.rotation_var, orient=tk.HORIZONTAL)
        rotation_scale.grid(row=0, column=0, sticky='ew', padx=(0, 5))
        
        # 旋转输入框
        rotation_entry = ttk.Spinbox(rotation_frame, from_=-180, to=180, increment=1,
                                    textvariable=self.rotation_var, width=6)
        rotation_entry.grid(row=0, column=1)
        
        image_watermark_frame.columnconfigure(1, weight=1)
        
        # 配置管理区域
        self.config_manager_ui = ConfigManagerUI(control_scrollable_frame, self.config_manager, self)
        
        # 处理按钮区域
        button_frame = ttk.Frame(control_scrollable_frame)
        button_frame.grid(row=8, column=0, sticky='ew', pady=(10, 0))
        
        ttk.Button(button_frame, text="开始处理", 
                  command=self.start_processing, style="Accent.TButton").grid(row=0, column=0, sticky='ew')
        
        button_frame.columnconfigure(0, weight=1)
        
        control_scrollable_frame.columnconfigure(0, weight=1)
        
    def create_image_list_area(self, parent):
        """创建右侧图片列表和预览区域"""
        # 创建右侧主框架
        right_frame = ttk.Frame(parent)
        right_frame.grid(row=0, column=1, rowspan=2, sticky='ewns')
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # 图片列表区域
        list_frame = ttk.LabelFrame(right_frame, text="图片列表", padding="5")
        list_frame.grid(row=0, column=0, sticky='ewns', pady=(0, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview显示图片列表
        columns = ('文件名', '路径', '日期', '状态')
        self.image_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # 设置列
        self.image_tree.heading('文件名', text='文件名')
        self.image_tree.heading('路径', text='完整路径')
        self.image_tree.heading('日期', text='拍摄日期')
        self.image_tree.heading('状态', text='状态')
        
        # 设置列宽
        self.image_tree.column('文件名', width=150)
        self.image_tree.column('路径', width=200)
        self.image_tree.column('日期', width=80)
        self.image_tree.column('状态', width=60)
        
        # 滚动条
        tree_scroll_v = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.image_tree.yview)
        tree_scroll_h = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.image_tree.xview)
        self.image_tree.configure(yscrollcommand=tree_scroll_v.set, xscrollcommand=tree_scroll_h.set)
        
        # 布局
        self.image_tree.grid(row=0, column=0, sticky='ewns')
        tree_scroll_v.grid(row=0, column=1, sticky='ns')
        tree_scroll_h.grid(row=1, column=0, sticky='ew')
        
        # 预览区域
        preview_frame = ttk.LabelFrame(right_frame, text="预览", padding="5")
        preview_frame.grid(row=1, column=0, sticky='ewns')
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # 创建预览画布
        self.preview_canvas = tk.Canvas(preview_frame, bg='white')
        self.preview_canvas.grid(row=0, column=0, sticky='ewns')
        
        # 添加默认提示文本
        self.preview_canvas.create_text(
            200, 150,
            text="请选择图片进行预览",
            fill="gray"
        )
        
        # 绑定鼠标事件用于拖拽水印
        self.preview_canvas.bind("<Button-1>", self.on_watermark_click)
        self.preview_canvas.bind("<B1-Motion>", self.on_watermark_drag)
        self.preview_canvas.bind("<ButtonRelease-1>", self.on_watermark_release)
        
        # 预览区域滚动条
        preview_scroll_v = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_canvas.yview)
        preview_scroll_h = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_canvas.xview)
        self.preview_canvas.configure(yscrollcommand=preview_scroll_v.set, xscrollcommand=preview_scroll_h.set)
        
        # 布局
        preview_scroll_v.grid(row=0, column=1, sticky='ns')
        preview_scroll_h.grid(row=1, column=0, sticky='ew')
        
        # 当前预览的图片索引
        self.current_preview_index = None
        
    def create_status_bar(self, parent):
        """创建底部状态栏"""
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=2, column=0, columnspan=2, sticky='ew', pady=(10, 0))
    
    def create_position_grid(self, parent):
        """创建九宫格位置按钮"""
        # 创建九宫格框架
        grid_frame = ttk.Frame(parent)
        grid_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(5, 10))
        
        # 九宫格位置映射
        positions = [
            ('↖', 'top_left'), ('↑', 'top_center'), ('↗', 'top_right'),
            ('←', 'center_left'), ('●', 'center'), ('→', 'center_right'),
            ('↙', 'bottom_left'), ('↓', 'bottom_center'), ('↘', 'bottom_right')
        ]
        
        # 创建3x3网格按钮
        for i, (symbol, position_key) in enumerate(positions):
            row = i // 3
            col = i % 3
            btn = tk.Button(grid_frame, text=symbol, width=3, height=1,
                           command=lambda p=position_key: self.set_position(p))
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
        
        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.columnconfigure(2, weight=1)
    
    def set_position(self, position):
        """设置水印位置"""
        self.position_var.set(position)
        self.watermark_position = None  # 重置自定义位置
        self.on_setting_change()
    
    def on_watermark_click(self, event):
        """鼠标点击水印事件"""
        # 确保preview_canvas不为None
        if self.preview_canvas is None:
            return
            
        # 获取点击位置
        x, y = event.x, event.y
        
        # 查找点击的项目
        items = self.preview_canvas.find_overlapping(x-5, y-5, x+5, y+5)
        if items:
            # 检查是否点击了水印（假设水印是最后一个添加的项目）
            self.drag_data["item"] = items[-1]
            self.drag_data["x"] = x
            self.drag_data["y"] = y
    
    def on_watermark_drag(self, event):
        """鼠标拖拽水印事件"""
        # 确保preview_canvas不为None且有拖拽项目
        if self.preview_canvas is None or self.drag_data["item"] is None:
            return
            
        # 计算移动距离
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        # 移动水印
        self.preview_canvas.move(self.drag_data["item"], dx, dy)
        
        # 更新拖拽数据
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        
        # 显示当前位置坐标
        self.show_watermark_position(event.x, event.y)
    
    def show_watermark_position(self, x, y):
        """显示水印位置坐标"""
        # 在状态栏显示坐标
        self.update_status(f"水印位置: ({x}, {y})")
        
        # 可选：在画布上显示坐标标签
        # 确保preview_canvas不为None
        if self.preview_canvas is not None:
            # 清除之前的位置标签（如果存在）
            self.preview_canvas.delete("position_label")
            
            # 创建新的位置标签
            self.preview_canvas.create_text(
                x + 10, y - 10,
                text=f"({x}, {y})",
                fill="red",
                font=("Arial", 10),
                tags="position_label"
            )
    
    def on_watermark_release(self, event):
        """鼠标释放水印事件"""
        # 确保preview_canvas不为None且有拖拽项目
        if self.preview_canvas is None or self.drag_data["item"] is None:
            return
            
        # 获取水印当前位置
        coords = self.preview_canvas.coords(self.drag_data["item"])
        if coords:
            # 保存自定义位置
            self.watermark_position = (coords[0], coords[1])
            # 更新位置变量为自定义
            self.position_var.set('custom')
        
        # 重置拖拽数据
        self.drag_data["item"] = None
        self.drag_data["x"] = 0
        self.drag_data["y"] = 0
    
    def on_window_configure(self, event):
        """窗口大小变化时的处理"""
        # 只有当事件来自主窗口时才更新预览
        if event.widget == self.root:
            # 延迟更新预览，避免频繁刷新
            if hasattr(self, '_window_resize_id') and self._window_resize_id is not None:
                try:
                    self.root.after_cancel(self._window_resize_id)
                except ValueError:
                    pass  # 忽略无效的ID
            self._window_resize_id = self.root.after(500, self.update_preview)
        
    def setup_drag_drop(self):
        """设置拖拽功能"""
        if drag_drop_available_flag and dnd_files_var is not None and self.image_tree is not None:
            # 绑定拖拽事件到图片列表区域
            try:
                # 使用hasattr检查确保方法存在
                if (hasattr(self.image_tree, 'drop_target_register') and 
                    hasattr(self.image_tree, 'dnd_bind')):
                    # 使用getattr安全地获取方法并调用
                    drop_target_register = getattr(self.image_tree, 'drop_target_register')
                    dnd_bind = getattr(self.image_tree, 'dnd_bind')
                    drop_target_register(dnd_files_var)
                    dnd_bind('<<Drop>>', self.on_drop)
            except Exception as e:
                print(f"拖拽功能设置失败: {e}")
        else:
            # 如果没有拖拽支持，显示提示
            print("拖拽功能不可用，请使用按钮导入图片")
    
    def update_opacity_label(self, value):
        """更新透明度标签"""
        if self.opacity_label is not None:
            self.opacity_label.config(text=f"{float(value):.1f}")
    
    def on_opacity_change(self, *args):
        """透明度变化时的处理"""
        self.update_opacity_label(self.opacity_var.get())
        self.on_setting_change()
    
    def on_setting_change(self, *args):
        """水印设置变化时更新预览"""
        # 使用after方法延迟更新，避免频繁刷新
        if hasattr(self, '_preview_update_id') and self._preview_update_id is not None:
            try:
                self.root.after_cancel(self._preview_update_id)
            except ValueError:
                pass  # 忽略无效的ID
        self._preview_update_id = self.root.after(300, self.update_preview)
    
    def update_jpeg_quality_label(self, value):
        """更新JPEG质量标签"""
        if self.jpeg_quality_label is not None:
            self.jpeg_quality_label.config(text=f"{int(float(value))}")
    
    def update_resize_percent_label(self, value):
        """更新缩放百分比标签"""
        if self.resize_percent_label is not None:
            self.resize_percent_label.config(text=f"{float(value):.1f}")
    
    def select_color(self):
        """选择颜色"""
        try:
            # 尝试导入颜色选择对话框
            import tkinter.colorchooser as colorchooser
        except ImportError:
            messagebox.showerror("错误", "当前环境不支持颜色选择器")
            return
        
        # 获取当前颜色值
        current_color = self.color_var.get()
        
        # 验证当前颜色格式
        if not self.is_valid_hex_color(current_color):
            current_color = "#FFFFFF"  # 默认白色
        
        # 打开颜色选择对话框
        color = colorchooser.askcolor(
            color=current_color,
            title="选择水印颜色"
        )
        
        # 如果用户选择了颜色，更新颜色值
        if color[1] is not None:
            self.color_var.set(color[1])
    
    def is_valid_hex_color(self, hex_color):
        """验证十六进制颜色格式"""
        if not isinstance(hex_color, str):
            return False
        
        # 移除可能的#前缀
        hex_color = hex_color.lstrip('#')
        
        # 检查长度是否为6
        if len(hex_color) != 6:
            return False
        
        # 检查是否只包含有效的十六进制字符
        try:
            int(hex_color, 16)
            return True
        except ValueError:
            return False
    
    def get_system_fonts(self):
        """获取系统可用字体列表"""
        try:
            import tkinter.font as tkFont
            # 获取系统字体
            font_names = list(tkFont.families())
            # 排序字体名称
            font_names.sort()
            return font_names
        except Exception as e:
            print(f"获取系统字体失败: {e}")
            # 返回默认字体列表
            return ['Arial', 'Times New Roman', 'Courier New', 'Microsoft YaHei', 'SimHei']
    
    def select_font(self):
        """选择字体"""
        # 创建字体选择对话框
        font_window = tk.Toplevel(self.root)
        font_window.title("选择字体")
        font_window.geometry("400x300")
        font_window.transient(self.root)
        font_window.grab_set()
        
        # 创建字体列表框架
        font_frame = ttk.Frame(font_window)
        font_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建字体列表
        font_listbox = tk.Listbox(font_frame)
        font_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(font_frame, orient=tk.VERTICAL, command=font_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        font_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 填充字体列表
        for font_name in self.available_fonts:
            font_listbox.insert(tk.END, font_name)
        
        # 选择当前字体
        current_font = self.font_path_var.get()
        if current_font:
            try:
                index = self.available_fonts.index(current_font)
                font_listbox.selection_set(index)
                font_listbox.see(index)
            except ValueError:
                pass
        
        # 创建按钮框架
        button_frame = ttk.Frame(font_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 确定按钮
        def on_ok():
            selection = font_listbox.curselection()
            if selection:
                font_name = font_listbox.get(selection[0])
                self.font_path_var.set(font_name)
                self.font_display_var.set(font_name)
            font_window.destroy()
        
        # 取消按钮
        def on_cancel():
            font_window.destroy()
        
        ok_button = ttk.Button(button_frame, text="确定", command=on_ok)
        ok_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_button = ttk.Button(button_frame, text="取消", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT)
        
        # 双击选择
        font_listbox.bind('<Double-Button-1>', lambda e: on_ok())
    
    def select_output_dir(self):
        """选择输出目录"""
        output_dir = filedialog.askdirectory(title="选择输出目录")
        if output_dir:
            # 验证是否与原文件夹相同
            if self.image_items:
                first_image_path = self.image_items[0].file_path
                if not self.watermark_processor.validate_output_directory(first_image_path, output_dir):
                    messagebox.showerror("错误", "不能将文件导出到原文件夹，请选择其他目录")
                    return
            self.output_dir_var.set(output_dir)
    
    def select_image_watermark(self):
        """选择图片水印文件"""
        file_types = [
            ("图片文件", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.webp *.gif *.ico"),
            ("PNG文件", "*.png"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择图片水印文件",
            filetypes=file_types
        )
        
        if file_path:
            self.image_watermark_path_var.set(file_path)
    
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
        item_id = None  # 初始化item_id变量
        for file_path in file_paths:
            if self.exif_reader.is_supported_image(file_path):
                # 检查是否已存在
                if not any(item.file_path == file_path for item in self.image_items):
                    # 获取日期信息
                    date_text = self.exif_reader.get_watermark_date(file_path)
                    item = ImageItem(file_path, date_text)
                    self.image_items.append(item)
                    
                    # 添加到树形控件
                    if self.image_tree is not None:
                        item_id = self.image_tree.insert('', 'end', values=(
                            os.path.basename(file_path),
                            file_path,
                            date_text,
                            item.status
                        ))
                    new_count += 1
                    
                    # 如果是第一张图片，自动选中并显示预览
                    if len(self.image_items) == 1:
                        if self.image_tree is not None and item_id is not None:
                            self.image_tree.selection_set(item_id)
                        self.current_preview_index = 0
                        self.update_preview()
        
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
            if self.image_tree is not None:
                for item in self.image_tree.get_children():
                    self.image_tree.delete(item)
            self.update_status("已清空图片列表")
            
            # 重置预览
            self.current_preview_index = None
            if self.preview_canvas is not None:
                self.preview_canvas.delete("all")
                self.preview_canvas.create_text(
                    200, 150,
                    text="请选择图片进行预览",
                    fill="gray"
                )
    
    def on_drop(self, event):
        """处理拖拽事件"""
        if not drag_drop_available_flag:
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
    
    def on_image_select(self, event):
        """处理图片列表选择事件"""
        if self.image_tree is not None:
            selection = self.image_tree.selection()
            if selection:
                # 获取选中项的索引
                item_id = selection[0]
                index = self.image_tree.index(item_id)
                if 0 <= index < len(self.image_items):
                    self.current_preview_index = index
                    self.update_preview()
    
    def update_preview(self):
        """更新预览显示"""
        if self.current_preview_index is None or self.current_preview_index >= len(self.image_items):
            return
        
        # 确保preview_canvas不为None
        if self.preview_canvas is None:
            return
            
        try:
            # 获取当前选中的图片
            image_item = self.image_items[self.current_preview_index]
            
            # 获取当前设置
            settings = self.get_current_settings()
            if settings is None:
                return
            
            # 创建临时水印处理器
            from src.watermark_processor import WatermarkProcessor, WatermarkPosition
            temp_processor = WatermarkProcessor()
            
            # 处理位置参数
            position = self.get_position_from_string(str(settings['position']))
            
            # 安全地获取参数值
            font_size = self.safe_int(settings['font_size'])
            opacity = self.safe_float(settings['opacity'])
            image_watermark_scale = self.safe_float(settings['image_watermark_scale'])
            
            # 确保font_style是字典类型
            font_style = settings['font_style']
            if not isinstance(font_style, dict):
                font_style = {'bold': False, 'italic': False}
            
            # 生成带水印的预览图片
            preview_image = temp_processor.add_watermark(
                image_path=image_item.file_path,
                date_text=image_item.date_text,
                font_size=font_size,
                color=str(settings['color']),
                position=position,
                font_path=str(settings['font_path']) if settings['font_path'] else None,
                opacity=opacity,
                custom_text=str(settings['custom_text']) if settings['custom_text'] else None,
                font_style=font_style,
                shadow=bool(settings['shadow']),
                stroke=bool(settings['stroke']),
                image_watermark_path=str(settings['image_watermark_path']) if settings['image_watermark_path'] else None,
                image_watermark_scale=image_watermark_scale,
                rotation=self.safe_float(settings.get('rotation', 0.0))  # 新增旋转参数
            )
            
            # 调整图片大小以适应预览区域
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            # 如果画布大小为1（初始状态），使用默认大小
            if canvas_width <= 1:
                canvas_width = 400
            if canvas_height <= 1:
                canvas_height = 300
            
            # 计算缩放比例
            img_width, img_height = preview_image.size
            scale_x = canvas_width / img_width
            scale_y = canvas_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # 不放大图片
            
            # 如果图片比预览区域小，不进行缩放
            if scale >= 1.0:
                scale = 1.0
            
            # 调整图片大小
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            if scale != 1.0:
                preview_image = preview_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 清除画布
            self.preview_canvas.delete("all")
            
            # 将PIL图像转换为Tkinter PhotoImage
            self.preview_photo = ImageTk.PhotoImage(preview_image)
            
            # 在画布中心显示图片
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.preview_canvas.create_image(x, y, anchor=tk.NW, image=self.preview_photo)
            
            # 更新画布滚动区域
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
            import traceback
            print(f"预览更新失败: {e}")
            print(traceback.format_exc())
            # 显示错误信息
            self.preview_canvas.delete("all")
            self.preview_canvas.create_text(
                self.preview_canvas.winfo_width() // 2,
                self.preview_canvas.winfo_height() // 2,
                text=f"预览失败: {str(e)}",
                fill="red"
            )
    
    def safe_int(self, value):
        """安全地转换为整数"""
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0
    
    def safe_float(self, value):
        """安全地转换为浮点数"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def update_status(self, message):
        """更新状态栏"""
        if self.status_var is not None:
            self.status_var.set(message)
        self.root.update_idletasks()
    
    def get_current_settings(self):
        """获取当前设置"""
        try:
            font_size = self.font_size_var.get()
            color = self.color_var.get()
            position = self.position_var.get()
            opacity = self.opacity_var.get()
            output_format = self.output_format_var.get()
            font_path = self.font_path_var.get() if self.font_path_var.get() else None
            # 新增导出设置
            output_dir = self.output_dir_var.get()
            jpeg_quality = self.jpeg_quality_var.get()
            naming_rule = self.naming_rule_var.get()
            custom_prefix = self.custom_prefix_var.get()
            custom_suffix = self.custom_suffix_var.get()
            resize_mode = self.resize_mode_var.get()
            resize_width = self.resize_width_var.get()
            resize_height = self.resize_height_var.get()
            resize_percent = self.resize_percent_var.get()
            # 新增水印文本设置
            custom_text = self.custom_text_var.get() if self.custom_text_var.get() else None
            font_style = {
                'bold': bool(self.font_style_bold_var.get()),
                'italic': bool(self.font_style_italic_var.get())
            }
            shadow = bool(self.shadow_var.get())
            stroke = bool(self.stroke_var.get())
            # 新增图片水印设置
            image_watermark_path = self.image_watermark_path_var.get() if self.image_watermark_path_var.get() else None
            image_watermark_scale = self.image_watermark_scale_var.get()
            # 新增旋转设置
            rotation = self.rotation_var.get()
            
            return {
                'font_size': font_size,
                'color': color,
                'position': position,
                'opacity': opacity,
                'output_format': output_format,
                'font_path': font_path,
                # 新增导出设置
                'output_dir': output_dir,
                'jpeg_quality': jpeg_quality,
                'naming_rule': naming_rule,
                'custom_prefix': custom_prefix,
                'custom_suffix': custom_suffix,
                'resize_mode': resize_mode,
                'resize_width': resize_width,
                'resize_height': resize_height,
                'resize_percent': resize_percent,
                # 新增水印文本设置
                'custom_text': custom_text,
                'font_style': font_style,
                'shadow': shadow,
                'stroke': stroke,
                # 新增图片水印设置
                'image_watermark_path': image_watermark_path,
                'image_watermark_scale': image_watermark_scale,
                # 新增旋转设置
                'rotation': rotation
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
        
        # 验证输出目录
        if not settings['output_dir']:
            messagebox.showwarning("警告", "请选择输出目录")
            return
        
        # 验证输出目录不能与原文件夹相同
        first_image_path = self.image_items[0].file_path
        output_dir = str(settings['output_dir'])
        if not self.watermark_processor.validate_output_directory(first_image_path, output_dir):
            messagebox.showerror("错误", "不能将文件导出到原文件夹，请选择其他目录")
            return
        
        # 在后台线程中处理图片
        threading.Thread(target=self.process_images_thread, args=(settings,), daemon=True).start()
    
    def process_images_thread(self, settings):
        """在后台线程中处理图片"""
        try:
            # 使用用户指定的输出目录
            output_dir = str(settings['output_dir'])
            
            success_count = 0
            total_count = len(self.image_items)
            
            for i, item in enumerate(self.image_items):
                try:
                    # 更新状态
                    self.root.after(0, lambda idx=i: self.update_item_status(idx, "处理中"))
                    self.root.after(0, lambda: self.update_status(f"正在处理 {i+1}/{total_count}: {os.path.basename(item.file_path)}"))
                    
                    # 处理图片
                    position = self.get_position_from_string(settings['position'])
                    
                    # 安全地获取参数值
                    font_size = self.safe_int(settings['font_size'])
                    opacity = self.safe_float(settings['opacity'])
                    jpeg_quality = self.safe_int(settings['jpeg_quality'])
                    resize_width = self.safe_int(settings['resize_width']) if settings['resize_mode'] == 'width' else None
                    resize_height = self.safe_int(settings['resize_height']) if settings['resize_mode'] == 'height' else None
                    resize_percent = self.safe_float(settings['resize_percent']) if settings['resize_mode'] == 'percent' else None
                    image_watermark_scale = self.safe_float(settings['image_watermark_scale'])
                    
                    # 确保font_style是字典类型
                    font_style = settings['font_style']
                    if not isinstance(font_style, dict):
                        font_style = {'bold': False, 'italic': False}
                    
                    output_path = self.watermark_processor.process_single_image(
                        image_path=item.file_path,
                        date_text=item.date_text,
                        output_dir=output_dir,
                        font_size=font_size,
                        color=str(settings['color']),
                        position=position,
                        font_path=str(settings['font_path']) if settings['font_path'] else None,
                        opacity=opacity,
                        output_format=str(settings['output_format']),
                        quality=jpeg_quality,
                        naming_rule=str(settings['naming_rule']),
                        custom_prefix=str(settings['custom_prefix']),
                        custom_suffix=str(settings['custom_suffix']),
                        resize_mode=str(settings['resize_mode']),
                        resize_width=resize_width,
                        resize_height=resize_height,
                        resize_percent=resize_percent,
                        custom_text=str(settings['custom_text']) if settings['custom_text'] else None,
                        font_style=font_style,
                        shadow=bool(settings['shadow']),
                        stroke=bool(settings['stroke']),
                        image_watermark_path=str(settings['image_watermark_path']) if settings['image_watermark_path'] else None,
                        image_watermark_scale=image_watermark_scale,
                        rotation=self.safe_float(settings.get('rotation', 0.0))  # 新增旋转参数
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
            if self.image_tree is not None:
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

    def on_closing(self):
        """窗口关闭时的处理"""
        # 保存当前设置到上次会话
        current_settings = self.get_current_settings()
        if current_settings:
            self.config_manager.save_last_session(current_settings)
        
        # 关闭窗口
        self.root.destroy()
    
    def load_last_session(self):
        """加载上次会话设置"""
        last_settings = self.config_manager.load_last_session()
        if last_settings:
            try:
                # 应用各种设置到GUI变量
                self.font_size_var.set(str(last_settings.get('font_size', 36)))
                self.color_var.set(str(last_settings.get('color', '#FFFFFF')))
                self.position_var.set(str(last_settings.get('position', 'bottom_right')))
                self.font_path_var.set(str(last_settings.get('font_path', '')))
                self.opacity_var.set(float(last_settings.get('opacity', 1.0)))
                self.output_format_var.set(str(last_settings.get('output_format', 'auto')))
                self.output_dir_var.set(str(last_settings.get('output_dir', '')))
                self.jpeg_quality_var.set(int(last_settings.get('jpeg_quality', 95)))
                self.naming_rule_var.set(str(last_settings.get('naming_rule', 'suffix')))
                self.custom_prefix_var.set(str(last_settings.get('custom_prefix', 'wm_')))
                self.custom_suffix_var.set(str(last_settings.get('custom_suffix', '_watermarked')))
                self.resize_mode_var.set(str(last_settings.get('resize_mode', 'none')))
                self.resize_width_var.set(int(last_settings.get('resize_width', 800)))
                self.resize_height_var.set(int(last_settings.get('resize_height', 600)))
                self.resize_percent_var.set(float(last_settings.get('resize_percent', 1.0)))
                self.custom_text_var.set(str(last_settings.get('custom_text', '')))
                self.font_style_bold_var.set(bool(last_settings.get('font_style_bold', False)))
                self.font_style_italic_var.set(bool(last_settings.get('font_style_italic', False)))
                self.shadow_var.set(bool(last_settings.get('shadow', False)))
                self.stroke_var.set(bool(last_settings.get('stroke', False)))
                self.image_watermark_path_var.set(str(last_settings.get('image_watermark_path', '')))
                self.image_watermark_scale_var.set(float(last_settings.get('image_watermark_scale', 1.0)))
                self.rotation_var.set(float(last_settings.get('rotation', 0.0)))
                
                # 更新字体显示
                font_path = str(last_settings.get('font_path', ''))
                font_display_text = "默认字体" if not font_path else font_path
                self.font_display_var.set(font_display_text)
                
                print("已加载上次会话设置")
            except Exception as e:
                print(f"加载上次会话设置失败: {e}")


def main():
    """主函数"""
    if drag_drop_available_flag and tkdnd_var is not None:
        try:
            root = tkdnd_var.Tk()
        except:
            root = tk.Tk()
    else:
        root = tk.Tk()
        
    app = PhotoWatermarkGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()