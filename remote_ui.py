import tkinter as tk
from tkinter import messagebox

def build_ui(parent):
    """
    远程界面构造入口
    :param parent: 主程序传过来的 tk.Frame 容器
    """
    # 顶部标题栏
    top_bar = tk.Frame(parent, bg="#1e1e2e", height=60)
    top_bar.pack(fill="x")
    
    title_label = tk.Label(
        top_bar, 
        text="GitHub 远程界面 - 当前版本: v1.0", 
        fg="#cdd6f4", 
        bg="#1e1e2e", 
        font=("Microsoft YaHei", 12, "bold")
    )
    title_label.pack(pady=15)

    # 主操作区
    content_area = tk.Frame(parent, bg="#f5f5f7")
    content_area.pack(fill="both", expand=True, padx=20, pady=20)

    desc = tk.Label(
        content_area, 
        text="这是来自 Bei18/110 仓库的 UI 界面。\n尝试在 GitHub 上修改这段文字或按钮颜色，提交 Commit 后，\n本地窗口会自动替换更新！",
        bg="#f5f5f7",
        font=("Microsoft YaHei", 10),
        justify="center"
    )
    desc.pack(pady=30)

    # 演示按钮
    action_btn = tk.Button(
        content_area, 
        text="点击测试远程逻辑", 
        bg="#89b4fa", 
        fg="#11111b",
        font=("Microsoft YaHei", 10, "bold"),
        relief="flat",
        padx=15,
        pady=5,
        command=lambda: messagebox.showinfo("响应", "这是远程 remote_ui.py 中定义的点击事件！")
    )
    action_btn.pack(pady=10)
