"""
配置管理模块
用于保存、加载和管理水印设置模板
"""

import os
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录，默认为用户主目录下的.photo_watermark目录
        """
        if config_dir is None:
            # 使用用户主目录下的配置目录
            home_dir = Path.home()
            self.config_dir = home_dir / '.photo_watermark'
        else:
            self.config_dir = Path(config_dir)
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置文件路径
        self.templates_file = self.config_dir / 'templates.json'
        self.last_session_file = self.config_dir / 'last_session.json'
        
        # 默认模板
        self.default_template = {
            'name': '默认模板',
            'font_size': 36,
            'color': '#FFFFFF',
            'position': 'bottom_right',
            'font_path': '',
            'opacity': 1.0,
            'output_format': 'auto',
            'output_dir': '',
            'jpeg_quality': 95,
            'naming_rule': 'suffix',
            'custom_prefix': 'wm_',
            'custom_suffix': '_watermarked',
            'resize_mode': 'none',
            'resize_width': 800,
            'resize_height': 600,
            'resize_percent': 1.0,
            'custom_text': '',
            'font_style_bold': False,
            'font_style_italic': False,
            'shadow': False,
            'stroke': False,
            'image_watermark_path': '',
            'image_watermark_scale': 1.0,
            'rotation': 0.0
        }
    
    def get_all_templates(self) -> List[Dict[str, Any]]:
        """
        获取所有保存的模板
        
        Returns:
            模板列表
        """
        if not self.templates_file.exists():
            # 如果模板文件不存在，创建默认模板
            self.save_template(self.default_template)
            return [self.default_template]
        
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('templates', [self.default_template])
        except (json.JSONDecodeError, KeyError):
            # 如果文件损坏，返回默认模板
            return [self.default_template]
    
    def save_template(self, template: Dict[str, Any]) -> bool:
        """
        保存模板
        
        Args:
            template: 模板数据
            
        Returns:
            是否保存成功
        """
        try:
            # 获取现有模板
            templates = self.get_all_templates()
            
            # 检查是否已存在同名模板
            existing_index = None
            for i, t in enumerate(templates):
                if t['name'] == template['name']:
                    existing_index = i
                    break
            
            # 更新或添加模板
            if existing_index is not None:
                templates[existing_index] = template
            else:
                templates.append(template)
            
            # 保存到文件
            data = {'templates': templates}
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存模板失败: {e}")
            return False
    
    def delete_template(self, template_name: str) -> bool:
        """
        删除模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            是否删除成功
        """
        try:
            # 获取现有模板
            templates = self.get_all_templates()
            
            # 查找并删除模板
            new_templates = [t for t in templates if t['name'] != template_name]
            
            # 不能删除默认模板
            if not new_templates:
                return False
            
            # 保存到文件
            data = {'templates': new_templates}
            with open(self.templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"删除模板失败: {e}")
            return False
    
    def save_last_session(self, settings: Dict[str, Any]) -> bool:
        """
        保存最后一次会话设置
        
        Args:
            settings: 设置数据
            
        Returns:
            是否保存成功
        """
        try:
            with open(self.last_session_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存会话设置失败: {e}")
            return False
    
    def load_last_session(self) -> Optional[Dict[str, Any]]:
        """
        加载最后一次会话设置
        
        Returns:
            设置数据，如果不存在则返回None
        """
        if not self.last_session_file.exists():
            return None
        
        try:
            with open(self.last_session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception) as e:
            print(f"加载会话设置失败: {e}")
            return None


class ConfigManagerUI:
    """配置管理器UI组件"""
    
    def __init__(self, parent, config_manager: ConfigManager, gui_app):
        """
        初始化配置管理器UI
        
        Args:
            parent: 父级组件
            config_manager: 配置管理器实例
            gui_app: GUI应用实例
        """
        self.parent = parent
        self.config_manager = config_manager
        self.gui_app = gui_app
        
        # 创建配置管理区域
        self.create_config_ui()
    
    def create_config_ui(self):
        """创建配置管理UI"""
        # 配置管理区域
        config_frame = ttk.LabelFrame(self.parent, text="模板管理", padding="5")
        config_frame.grid(row=7, column=0, sticky='ew', pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # 模板选择
        ttk.Label(config_frame, text="选择模板:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(config_frame, textvariable=self.template_var,
                                         state="readonly", width=12)
        self.template_combo.grid(row=0, column=1, sticky='ew', pady=2)
        
        # 刷新模板列表按钮
        refresh_btn = ttk.Button(config_frame, text="刷新", command=self.refresh_templates, width=6)
        refresh_btn.grid(row=0, column=2, padx=(2, 0), pady=2)
        
        # 模板操作按钮框架
        template_btn_frame = ttk.Frame(config_frame)
        template_btn_frame.grid(row=1, column=0, columnspan=3, sticky='ew', pady=2)
        template_btn_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        # 保存当前设置为模板
        save_btn = ttk.Button(template_btn_frame, text="保存模板", 
                             command=self.save_current_template)
        save_btn.grid(row=0, column=0, sticky='ew', padx=(0, 2))
        
        # 应用选中模板
        apply_btn = ttk.Button(template_btn_frame, text="应用模板", 
                              command=self.apply_selected_template)
        apply_btn.grid(row=0, column=1, sticky='ew', padx=(0, 2))
        
        # 重命名模板
        rename_btn = ttk.Button(template_btn_frame, text="重命名", 
                               command=self.rename_template)
        rename_btn.grid(row=0, column=2, sticky='ew', padx=(0, 2))
        
        # 删除模板
        delete_btn = ttk.Button(template_btn_frame, text="删除模板", 
                               command=self.delete_template)
        delete_btn.grid(row=0, column=3, sticky='ew')
        
        # 初始化模板列表
        self.refresh_templates()
    
    def refresh_templates(self):
        """刷新模板列表"""
        templates = self.config_manager.get_all_templates()
        template_names = [t['name'] for t in templates]
        self.template_combo['values'] = template_names
        
        # 设置默认选中项
        if template_names:
            self.template_var.set(template_names[0])
    
    def save_current_template(self):
        """保存当前设置为模板"""
        # 获取当前设置
        current_settings = self.gui_app.get_current_settings()
        
        # 弹出对话框获取模板名称
        template_name = self._ask_template_name("保存模板", "请输入模板名称:")
        if not template_name:
            return
        
        # 添加模板名称到设置
        current_settings['name'] = template_name
        
        # 保存模板
        if self.config_manager.save_template(current_settings):
            messagebox.showinfo("成功", f"模板 '{template_name}' 保存成功!")
            self.refresh_templates()
            
            # 如果保存的是新模板，自动选中
            template_names = list(self.template_combo['values'])
            if template_name in template_names:
                self.template_var.set(template_name)
        else:
            messagebox.showerror("错误", "保存模板失败!")
    
    def apply_selected_template(self):
        """应用选中的模板"""
        selected_name = self.template_var.get()
        if not selected_name:
            messagebox.showwarning("警告", "请先选择一个模板!")
            return
        
        # 获取所有模板
        templates = self.config_manager.get_all_templates()
        
        # 查找选中的模板
        selected_template = None
        for template in templates:
            if template['name'] == selected_name:
                selected_template = template
                break
        
        if not selected_template:
            messagebox.showerror("错误", f"找不到模板 '{selected_name}'!")
            return
        
        # 应用模板设置
        self._apply_template_settings(selected_template)
        messagebox.showinfo("成功", f"模板 '{selected_name}' 应用成功!")
    
    def rename_template(self):
        """重命名模板"""
        selected_name = self.template_var.get()
        if not selected_name:
            messagebox.showwarning("警告", "请先选择一个模板!")
            return
        
        # 不能重命名默认模板
        if selected_name == "默认模板":
            messagebox.showwarning("警告", "不能重命名默认模板!")
            return
        
        # 获取新名称
        new_name = self._ask_template_name("重命名模板", "请输入新名称:", selected_name)
        if not new_name or new_name == selected_name:
            return
        
        # 检查新名称是否已存在
        template_names = list(self.template_combo['values'])
        if new_name in template_names:
            messagebox.showerror("错误", f"模板 '{new_name}' 已存在!")
            return
        
        # 获取所有模板
        templates = self.config_manager.get_all_templates()
        
        # 查找并重命名模板
        for template in templates:
            if template['name'] == selected_name:
                template['name'] = new_name
                break
        
        # 保存更新后的模板
        try:
            data = {'templates': templates}
            with open(self.config_manager.templates_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", f"模板 '{selected_name}' 已重命名为 '{new_name}'!")
            self.refresh_templates()
            self.template_var.set(new_name)
        except Exception as e:
            messagebox.showerror("错误", f"重命名模板失败: {e}")
    
    def delete_template(self):
        """删除模板"""
        selected_name = self.template_var.get()
        if not selected_name:
            messagebox.showwarning("警告", "请先选择一个模板!")
            return
        
        # 不能删除默认模板
        if selected_name == "默认模板":
            messagebox.showwarning("警告", "不能删除默认模板!")
            return
        
        # 确认删除
        if not messagebox.askyesno("确认删除", f"确定要删除模板 '{selected_name}' 吗?"):
            return
        
        # 删除模板
        if self.config_manager.delete_template(selected_name):
            messagebox.showinfo("成功", f"模板 '{selected_name}' 已删除!")
            self.refresh_templates()
        else:
            messagebox.showerror("错误", "删除模板失败!")
    
    def _ask_template_name(self, title: str, prompt: str, default: str = "") -> Optional[str]:
        """
        弹出对话框获取模板名称
        
        Args:
            title: 对话框标题
            prompt: 提示文本
            default: 默认值
            
        Returns:
            模板名称，如果取消则返回None
        """
        # 创建对话框
        dialog = tk.Toplevel(self.parent)
        dialog.title(title)
        dialog.geometry("300x120")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (dialog.winfo_screenheight() // 2) - (120 // 2)
        dialog.geometry(f"300x120+{x}+{y}")
        
        # 变量
        name_var = tk.StringVar(value=default)
        
        # 界面元素
        ttk.Label(dialog, text=prompt).pack(pady=(10, 5))
        
        name_entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        # 按钮框架
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        result: List[Optional[str]] = [None]  # 使用列表来存储结果，因为内部函数无法直接修改外部变量
        
        def on_ok():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("警告", "模板名称不能为空!")
                return
            result[0] = name
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ok_btn = ttk.Button(button_frame, text="确定", command=on_ok)
        ok_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        cancel_btn = ttk.Button(button_frame, text="取消", command=on_cancel)
        cancel_btn.pack(side=tk.LEFT)
        
        # 绑定回车键
        name_entry.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        # 等待对话框关闭
        dialog.wait_window()
        
        return result[0]
    
    def _apply_template_settings(self, template: Dict[str, Any]):
        """
        应用模板设置到GUI
        
        Args:
            template: 模板数据
        """
        # 应用各种设置到GUI变量
        self.gui_app.font_size_var.set(str(template.get('font_size', 36)))
        self.gui_app.color_var.set(template.get('color', '#FFFFFF'))
        self.gui_app.position_var.set(template.get('position', 'bottom_right'))
        self.gui_app.font_path_var.set(template.get('font_path', ''))
        self.gui_app.opacity_var.set(template.get('opacity', 1.0))
        self.gui_app.output_format_var.set(template.get('output_format', 'auto'))
        self.gui_app.output_dir_var.set(template.get('output_dir', ''))
        self.gui_app.jpeg_quality_var.set(template.get('jpeg_quality', 95))
        self.gui_app.naming_rule_var.set(template.get('naming_rule', 'suffix'))
        self.gui_app.custom_prefix_var.set(template.get('custom_prefix', 'wm_'))
        self.gui_app.custom_suffix_var.set(template.get('custom_suffix', '_watermarked'))
        self.gui_app.resize_mode_var.set(template.get('resize_mode', 'none'))
        self.gui_app.resize_width_var.set(template.get('resize_width', 800))
        self.gui_app.resize_height_var.set(template.get('resize_height', 600))
        self.gui_app.resize_percent_var.set(template.get('resize_percent', 1.0))
        self.gui_app.custom_text_var.set(template.get('custom_text', ''))
        self.gui_app.font_style_bold_var.set(template.get('font_style_bold', False))
        self.gui_app.font_style_italic_var.set(template.get('font_style_italic', False))
        self.gui_app.shadow_var.set(template.get('shadow', False))
        self.gui_app.stroke_var.set(template.get('stroke', False))
        self.gui_app.image_watermark_path_var.set(template.get('image_watermark_path', ''))
        self.gui_app.image_watermark_scale_var.set(template.get('image_watermark_scale', 1.0))
        self.gui_app.rotation_var.set(template.get('rotation', 0.0))
        
        # 更新字体显示
        font_display_text = "默认字体" if not template.get('font_path') else template.get('font_path')
        self.gui_app.font_display_var.set(font_display_text)
        
        # 触发一次预览更新
        self.gui_app.on_setting_change()