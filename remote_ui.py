import os
import json
import subprocess
from pathlib import Path

# 核心：直接精准导入具体组件类，不依赖 tk.xxx 的形式
from tkinter import StringVar, Label, Frame, Canvas, Entry, Button, filedialog, ttk

def build_ui(parent):
    APP_TITLE = "火麒麟多开"
    CONFIG_NAME = "launcher_config.json"

    def get_app_data_dir():
        appdata_dir = (
            Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
            / "MultiLauncher"
        )
        appdata_dir.mkdir(parents=True, exist_ok=True)
        return appdata_dir

    appdata_dir = get_app_data_dir()
    config_path = appdata_dir / CONFIG_NAME
    default_profile_root = appdata_dir / "profiles"

    # 使用直接导入的 StringVar，绝对不会引发 '_tkinter.tkapp' 报错
    exe_var = StringVar()
    profile_dir_var = StringVar(value=str(default_profile_root))
    count_var = StringVar(value="1")
    status_var = StringVar(value="")

    rows = []
    apps_config = {}
    current_custom_notes = {}

    root = parent.winfo_toplevel()
    root.title(APP_TITLE)

    def set_status(msg, is_error=True):
        status_var.set(msg)
        if is_error:
            status_label.config(fg="#d9534f", bg="#f2dede")
        else:
            status_label.config(fg="#3c763d", bg="#dff0d8")

    def clear_status():
        status_var.set("")

    def load_config():
        nonlocal apps_config, current_custom_notes
        if not config_path.exists():
            return
        try:
            data = json.loads(config_path.read_text("utf-8"))
            apps_config = data.get("apps", {})
            saved_profile = data.get("profile_dir", "")
            if saved_profile:
                profile_dir_var.set(saved_profile)

            last_exe = data.get("last_exe", "")
            if last_exe and Path(last_exe).exists():
                exe_var.set(last_exe)
                load_app_spec_config(last_exe)
        except Exception as e:
            set_status(f"加载配置失败: {e}")

    def load_app_spec_config(exe_path: str):
        nonlocal current_custom_notes
        exe_path = exe_path.strip()
        if not exe_path or exe_path not in apps_config:
            current_custom_notes = {}
            return

        app_data = apps_config[exe_path]
        count_var.set(str(max(1, min(50, int(app_data.get("count", 1))))))
        saved_notes = app_data.get("notes", [])
        current_custom_notes = {i + 1: note for i, note in enumerate(saved_notes)}

    def save_config():
        current_exe = exe_var.get().strip()
        current_notes = [note_var.get().strip() for note_var in rows]

        if current_exe:
            apps_config[current_exe] = {
                "count": get_count(),
                "notes": current_notes,
            }

        data = {
            "last_exe": current_exe,
            "profile_dir": profile_dir_var.get().strip(),
            "apps": apps_config,
        }
        try:
            config_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            set_status(f"保存配置失败: {e}")

    def get_count():
        try:
            value = int(count_var.get().strip())
        except Exception:
            value = 1
        value = max(1, min(50, value))
        count_var.set(str(value))
        return value

    def get_exe_stem() -> str:
        exe_path = exe_var.get().strip().strip('"')
        if exe_path:
            return Path(exe_path).stem
        return "App"

    def auto_detect_exe() -> str:
        possible_paths = [
            r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
            r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Lark\Lark.exe"),
        ]
        for p in possible_paths:
            if Path(p).is_file():
                return p
        return ""

    def launch_one(index: int, note: str):
        clear_status()
        exe_str = exe_var.get().strip().strip('"')
        exe = Path(exe_str)
        if not exe.is_file():
            set_status("错误: 请先选择有效的 EXE 程序")
            return

        profile_root = Path(profile_dir_var.get().strip()) if profile_dir_var.get().strip() else default_profile_root
        try:
            profile_root.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            set_status(f"目录错误: {exc}")
            return

        exe_stem = get_exe_stem()
        note = note.strip()
        profile_name = f"{exe_stem}-{index}({note})" if note else f"{exe_stem}-{index}"
        profile = (profile_root / profile_name).resolve()

        try:
            profile.mkdir(parents=True, exist_ok=True)
            app_id = f"MultiInstanceLauncher.{profile_name}"

            if os.name == "nt":
                cmd_str = f'start "" "{str(exe)}" --user-data-dir="{profile}" --class="{app_id}" --app-id="{app_id}"'
                subprocess.Popen(
                    cmd_str,
                    shell=True,
                    cwd=str(exe.parent),
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            else:
                cmd = [str(exe), f"--user-data-dir={profile}", f"--class={profile_name}"]
                subprocess.Popen(cmd, cwd=str(exe.parent))

            set_status(f"启动成功: {profile_name}", is_error=False)
            save_config()
        except Exception as exc:
            set_status(f"启动失败: {exc}")

    def refresh_rows():
        nonlocal rows
        for idx, note_var in enumerate(rows, start=1):
            current_custom_notes[idx] = note_var.get().strip()

        for widget in rows_frame.winfo_children():
            widget.destroy()

        rows = []
        count = get_count()
        exe_stem = get_exe_stem()

        for index in range(1, count + 1):
            row = ttk.Frame(rows_frame)
            row.pack(fill="x", padx=1, pady=1)

            default_note = current_custom_notes.get(index, "")
            note_var = StringVar(value=default_note)
            note_var.trace_add("write", lambda *args: save_config())

            label_text = f"{exe_stem}{index}"
            ttk.Label(row, text=label_text, width=6, anchor="w").pack(side="left")

            ttk.Entry(row, textvariable=note_var, width=8).pack(
                side="left", fill="x", expand=True, padx=(2, 2)
            )

            ttk.Button(
                row,
                text="启动",
                width=4,
                command=lambda idx=index, n=note_var: launch_one(idx, n.get()),
            ).pack(side="right")

            rows.append(note_var)

        calc_height = 115 + (count * 33)
        screen_height = root.winfo_screenheight()
        max_height = min(calc_height, screen_height - 100)
        root.geometry(f"230x{max_height}")
        save_config()

    def choose_exe():
        path = filedialog.askopenfilename(
            title="选择程序",
            filetypes=[("应用程序", "*.exe;*.lnk"), ("All files", "*.*")],
        )
        if path:
            exe_var.set(path)

    def choose_profile_dir():
        path = filedialog.askdirectory(title="选择数据存储路径")
        if path:
            profile_dir_var.set(path)
            save_config()

    main_frame = ttk.Frame(parent)
    main_frame.pack(fill="both", expand=True, padx=4, pady=4)

    status_label = Label(
        main_frame,
        textvariable=status_var,
        font=("Microsoft YaHei", 8),
        anchor="w",
        wraplength=210,
        justify="left"
    )
    status_label.pack(fill="x", pady=(0, 2))

    exe_frame = ttk.Frame(main_frame)
    exe_frame.pack(fill="x", pady=1)
    ttk.Label(exe_frame, text="程序").pack(side="left", padx=(0, 2))
    ttk.Entry(exe_frame, textvariable=exe_var, width=10).pack(side="left", fill="x", expand=True, padx=(0, 2))
    ttk.Button(exe_frame, text="浏览", width=4, command=choose_exe).pack(side="right")

    profile_frame = ttk.Frame(main_frame)
    profile_frame.pack(fill="x", pady=1)
    ttk.Label(profile_frame, text="存储").pack(side="left", padx=(0, 2))
    ttk.Entry(profile_frame, textvariable=profile_dir_var, width=10).pack(side="left", fill="x", expand=True, padx=(0, 2))
    ttk.Button(profile_frame, text="选择", width=4, command=choose_profile_dir).pack(side="right")

    options = ttk.Frame(main_frame)
    options.pack(fill="x", pady=1)
    ttk.Label(options, text="数量").pack(side="left", padx=(0, 2))
    count_entry = ttk.Entry(options, textvariable=count_var, width=6, justify="center")
    count_entry.pack(side="left", padx=(1, 4))
    count_entry.bind("<FocusOut>", lambda e: refresh_rows())
    count_entry.bind("<Return>", lambda e: refresh_rows())

    list_container = ttk.Frame(main_frame)
    list_container.pack(fill="both", expand=True, padx=0, pady=(2, 0))

    canvas = Canvas(list_container, highlightthickness=0)
    scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
    rows_frame = ttk.Frame(canvas)

    canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
    rows_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas_window = canvas.create_window((0, 0), window=rows_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    load_config()
    if not exe_var.get() or not Path(exe_var.get()).exists():
        detected = auto_detect_exe()
        if detected:
            exe_var.set(detected)

    exe_var.trace_add("write", lambda *args: refresh_rows())
    refresh_rows()
