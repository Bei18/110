import tkinter as tk
from tkinter import messagebox

def build_ui(parent):
    # ----------------------------------------------------
    # 1. 云端全权控制主窗口 (大小、标题等)
    # ----------------------------------------------------
    root.title("云端完全控制 - v3.0")
    root.geometry("600x450")  # 直接在这里改窗口大小
    root.resizable(True, True)

    # ----------------------------------------------------
    # 2. 绘制组件内容
    # ----------------------------------------------------
    # 顶部栏
    top_bar = tk.Frame(parent, bg="#1e1e2e", height=60)
    top_bar.pack(fill="x")

    title_label = tk.Label(
        top_bar, 
        text="纯内存热重载 + 全局窗口控制", 
        fg="#ffffff", 
        bg="#1e1e2e", 
        font=("Microsoft YaHei", 12, "bold")
    )
    title_label.pack(pady=15)

    # 内容容器
    content = tk.Frame(parent)
    content.pack(fill="both", expand=True, padx=20, pady=20)

    info_label = tk.Label(
        content, 
        text="现在修改 GitHub 上的 root.geometry('800x500')，\n本地窗口会自动调整大小，且绝对不会在本地产生任何文件！", 
        font=("Microsoft YaHei", 10),
        justify="center"
    )
    info_label.pack(pady=20)

    btn = tk.Button(
        content, 
        text="测试点击", 
        bg="#007acc", 
        fg="white", 
        font=("Microsoft YaHei", 10),
        command=lambda: messagebox.showinfo("提示", "运行成功！")
    )
    btn.pack(pady=10)
