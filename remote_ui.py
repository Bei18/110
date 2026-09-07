import tkinter as tk
from tkinter import messagebox

def build_ui():
    # ----------------------------------------------------
    # 1. 在这里全权控制【主窗口属性】
    # ----------------------------------------------------
    root.title("云端完全接管窗口 - v2.0")  # 修改窗口标题
    root.geometry("650x500")               # 修改窗口大小 (长x宽)
    root.resizable(True, True)             # 是否允许缩放 (宽, 高)
    # root.attributes("-topmost", True)    # 取消注释可以让窗口置顶

    # ----------------------------------------------------
    # 2. 在这里构建【界面内容与逻辑】
    # ----------------------------------------------------
    # 顶部栏
    top_bar = tk.Frame(parent, bg="#2d3748", height=70)
    top_bar.pack(fill="x")

    title_label = tk.Label(
        top_bar, 
        text="窗口尺寸/标题/组件全部由 GitHub 云端控制", 
        fg="#ffffff", 
        bg="#2d3748", 
        font=("Microsoft YaHei", 12, "bold")
    )
    title_label.pack(pady=20)

    # 内容区
    content = tk.Frame(parent, bg="#f7fafc")
    content.pack(fill="both", expand=True, padx=25, pady=25)

    info_label = tk.Label(
        content, 
        text="当你修改 GitHub 上的 root.geometry('800x600') 并 Commit 后，\n本地窗口大小会在 10 秒内自动调整，且本地不会产生任何垃圾文件！", 
        bg="#f7fafc",
        font=("Microsoft YaHei", 10),
        justify="center"
    )
    info_label.pack(pady=30)

    btn = tk.Button(
        content, 
        text="测试按钮", 
        bg="#4299e1", 
        fg="white", 
        font=("Microsoft YaHei", 10, "bold"),
        relief="flat",
        padx=15, 
        pady=8,
        command=lambda: messagebox.showinfo("提示", "纯内存加载运行成功！")
    )
    btn.pack(pady=10)
