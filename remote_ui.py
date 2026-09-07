import tkinter as tk
from tkinter import messagebox

def build_ui(parent):
    """
    远程界面渲染入口
    :param parent: 主程序传进来的 tk.Frame 容器
    """
    # 标题面板
    header = tk.Frame(parent, bg="#2b2b2b", height=60)
    header.pack(fill="x")
    
    title = tk.Label(header, text="GitHub 动态界面 (v1.0)", fg="white", bg="#2b2b2b", font=("Arial", 14, "bold"))
    title.pack(pady=15)

    # 主内容区
    content = tk.Frame(parent)
    content.pack(expand=True, fill="both", padx=20, pady=20)

    info_label = tk.Label(
        content, 
        text="修改 GitHub 上的这段代码并 Commit，\n本地运行的窗口会在 10 秒内自动检测并刷出新界面！", 
        font=("Microsoft YaHei", 11)
    )
    info_label.pack(pady=20)

    # 交互按钮
    btn = tk.Button(
        content, 
        text="测试远程按钮事件", 
        bg="#4CAF50", 
        fg="white", 
        font=("Arial", 10),
        command=lambda: messagebox.showinfo("提示", "这是从 GitHub 远程运行的点击事件！")
    )
    btn.pack(pady=10)
