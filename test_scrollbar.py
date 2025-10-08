#!/usr/bin/env python
"""
测试滚动条功能
"""

import tkinter as tk
from tkinter import ttk

def test_scrollbar():
    """测试滚动条功能"""
    root = tk.Tk()
    root.title("滚动条功能测试")
    root.geometry("400x300")
    
    # 创建包含滚动条的容器
    container = ttk.Frame(root)
    container.pack(fill='both', expand=True, padx=10, pady=10)
    container.rowconfigure(0, weight=1)
    container.columnconfigure(0, weight=1)
    
    # 创建Canvas和滚动条
    canvas = tk.Canvas(container, highlightthickness=0)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    # 配置滚动区域
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    
    # 在Canvas中创建窗口
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # 添加测试内容
    for i in range(50):
        ttk.Label(scrollable_frame, text=f"测试行 {i+1}").pack(pady=5)
    
    # 布局
    canvas.grid(row=0, column=0, sticky='ewns')
    scrollbar.grid(row=0, column=1, sticky='ns')
    
    # 绑定鼠标滚轮事件
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _bind_to_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _unbind_from_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    
    canvas.bind('<Enter>', _bind_to_mousewheel)
    canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    root.mainloop()

if __name__ == "__main__":
    test_scrollbar()