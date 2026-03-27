import tkinter as tk
from tkinter import ttk, messagebox
import minecraft_launcher_lib
import subprocess, threading, json, os, sys
import ctypes
from ToolTip import ToolTip
from ErrorHandler import error_handler

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

configuration_file = "Configuration.json"
threshold_version = "1.16.5"
mc_dir = minecraft_launcher_lib.utils.get_minecraft_directory()
process = None
    
if not os.path.exists(mc_dir):
    os.makedirs(mc_dir, exist_ok=True)
    
if os.path.exists(configuration_file):
    try:
        with open(configuration_file, "r", encoding="utf-8") as f:
            configuration = json.load(f)
            
        if configuration["fabric"] is None:
            configuration["fabric"] = "Yok"
    except:
        messagebox.showwarning("Uyarı", "Yapılandırma dosyası bozuk. Bu nedenle ayarlar sıfırlandı.")
        configuration = {
            "username": "Oyuncu",
            "version": "26.1",
            "java_path": None,
            "fabric": None,
            "snapshots": False
        }
    
else:
    messagebox.showwarning("Uyarı", "Yapılandırma dosyası başka bir yere taşınmış veya silinmiş. Bu nedenle ayarlar sıfırlandı.")
    configuration = {
        "username": "Oyuncu",
        "version": "26.1",
        "java_path": None,
        "fabric": None,
        "snapshots": False
    }
    
if configuration["snapshots"]:
    mc_versions = [
        v["id"]
        for v in minecraft_launcher_lib.utils.get_version_list()
        if v["type"] in ["release", "snapshot"]
    ]
else:
    mc_versions = [
        v["id"]
        for v in minecraft_launcher_lib.utils.get_version_list()
        if v["type"] == "release"
    ]
    
versions = mc_versions.copy()

installed_versions = minecraft_launcher_lib.utils.get_installed_versions(mc_dir)

for v in installed_versions:
    vid = v["id"]

    if vid.startswith("fabric-loader-"):
        continue

    if vid not in versions:
        versions.append(vid)
    
java_path = configuration["java_path"]

def version_tuple(v):
    return tuple(map(int, v.split(".")))

def is_vanilla_installed(mc_version: str) -> bool:
    installed = minecraft_launcher_lib.utils.get_installed_versions(
        minecraft_launcher_lib.utils.get_minecraft_directory()
    )

    return any(
        v["id"] == mc_version and v["type"] == "release"
        for v in installed
    )
    
def open_dir():
    global mc_dir
    if not os.path.exists(mc_dir):
        os.makedirs(mc_dir, exist_ok=True)
    
    games_dir = mc_dir
    
    if sys.platform == "win32":
        os.startfile(games_dir)
    elif sys.platform == "darwin":
        os.system(f'open "{games_dir}"')
    else:
        os.system(f'xdg-open "{games_dir}"')
        
def select_java():
    from tkinter import filedialog
    path = filedialog.askopenfilename(
        title="Java Yürütülebilir Dosyası Seç",
        filetypes=[("Java Yürütülebilir Dosyası", "java.exe javaw.exe")])
    if path:
        global java_path
        java_path = path
        java_button.config(fg="#0040bf")
        ToolTip(java_button, "Java: Seçildi" if java_path else "Java: Seçilmedi")
        save_settings()

def launch():
    threading.Thread(target=launch_game, daemon=True).start()

def launch_game():
    global process, mc_dir
    
    progress_label.pack(pady=(0, 20), padx=20, fill="x")
        
    if not java_path:
        messagebox.showerror("Hata", "Java yürütülebilir dosyası seçilmedi. Java yürütülebilir dosyası olmadan Minecraft çalışamaz.")
        progress_label.pack_forget()
        return
    
    username = username_entry.get()
    version = version_combobox.get()
    
    loader = fabric_combobox.get()

    if loader != "Yok":
        mc_version = version
        version_id = f"fabric-loader-{loader}-{mc_version}"

        installed = {
            v["id"]
            for v in minecraft_launcher_lib.utils.get_installed_versions(mc_dir)
        }

        if version_id not in installed:
            progress_label.config(text="Fabric kuruluyor…")
            ok = install_fabric(mc_version, loader)
            if not ok:
                progress_label.config(text="")
                progress_label.pack_forget()
                return

        version = version_id

    if not username:
        messagebox.showerror("Hata", "Lütfen bir kullanıcı adı girin.")
        progress_label.pack_forget()
        return

    if not version:
        messagebox.showerror("Hata", "Lütfen bir sürüm seçin.")
        progress_label.pack_forget()
        return

    try:
        installed_versions = {
            v["id"]
            for v in minecraft_launcher_lib.utils.get_installed_versions(mc_dir)
        }

        if version not in installed_versions:
            progress_label.config(text="Minecraft indiriliyor…")

            callback = {
                "setStatus": set_status,
            }

            minecraft_launcher_lib.install.install_minecraft_version(
                version, mc_dir, callback=callback
            )

        options = {
            "username": username,
            "uuid": "00000000000000000000000000000000",
            "token": "",
            "executablePath": java_path
        }
        
        command = minecraft_launcher_lib.command.get_minecraft_command(
            version, mc_dir, options
        )

        if isinstance(command, tuple):
            command = command[0]

        if isinstance(command, dict):
            command = command.get("command", command)

        if isinstance(command, str):
            command = command.split()
        
        progress_label.config(text="Başlatılıyor...")

        win.after(0, win.withdraw)

        process = subprocess.Popen(command)
        
    except Exception as e:
        messagebox.showerror("Hata", f"Başlatılırken bir hata oluştu:\n{str(e)}")

    def wait_game():
        global process

        if process is None:
            return

        try:
            process.wait()
        finally:
            win.after(0, lambda: (
                win.deiconify(),
                progress_label.pack_forget()
            ))

    if process is not None:
        threading.Thread(target=wait_game, daemon=True).start()

def install_fabric(mc_version, loader):
    mc_dir = minecraft_launcher_lib.utils.get_minecraft_directory()

    try:
        minecraft_launcher_lib.fabric.install_fabric(
            minecraft_version=mc_version,
            loader_version=loader,
            minecraft_directory=mc_dir
        )
    except Exception as e:
        messagebox.showerror("Hata", f"Fabric kurulamadı:\n{e}")
        return False

    return True
    
def set_status(text):
    if len(text) < 30:
        progress_label.config(text=text)
    else:
        progress_label.config(text=text[:30] + "...")
        
    win.update_idletasks()
    
def save_settings():
    username = username_entry.get()
    version = version_combobox.get()
    fabric = fabric_combobox.get()
    snapshots = show_snapshots.get()
    
    if fabric.lower() == "yok":
        fabric = None
    
    configuration = {
        "username": username,
        "version": version,
        "java_path": java_path,
        "fabric": fabric,
        "snapshots": snapshots
    }
    
    with open(configuration_file, "w", encoding="utf-8") as f:
        json.dump(configuration, f, ensure_ascii=False, indent=4)
        
def save_on_exit():
    save_settings()
    win.destroy()
    
def show_about():
    messagebox.showinfo("Hakkında", "BukiLauncher v1.1.0\n© telif hakkı 2026 Buğra US")
    
def change_snapshot_shown(*args):
    global mc_versions
    
    if show_snapshots.get():
        mc_versions = [
            v["id"]
            for v in minecraft_launcher_lib.utils.get_version_list()
            if v["type"] in ["release", "snapshot"]
        ]
    else:
        mc_versions = [
            v["id"]
            for v in minecraft_launcher_lib.utils.get_version_list()
            if v["type"] == "release"
        ]
        version_combobox.set(mc_versions[0])
        
    version_combobox.config(values=mc_versions)
    version_combobox.set(mc_versions[0])

win = tk.Tk()
win.title("BukiLauncher")
win.resizable(False, False)

def report_callback_exception(exc_type, exc_value, exc_traceback):
    error_handler(exc_type, exc_value, exc_traceback, parent=win)

win.report_callback_exception = report_callback_exception

show_snapshots = tk.BooleanVar(value=configuration["snapshots"])

if hasattr(sys, "_MEIPASS"):
    icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
else:
    icon_path = os.path.join(os.path.dirname(__file__), "Icon.ico")

if os.path.exists(icon_path):
    win.iconbitmap(icon_path)

style = ttk.Style()
style.theme_use("default")

style.configure("TCombobox", background="SystemButtonFace", fieldbackground="SystemButtonFace", selectborderwidth=0, selectbackground="#0078D7", arrowsize=15)
style.map("TCombobox", background=[("active", "SystemButtonFace")], fieldbackground=[("readonly", "#ffffff")], relief=[("pressed", "sunken")])

style.configure("Vertical.TScrollbar", background="SystemButtonFace", troughcolor="#dddddd", width=15)
style.map("Vertical.TScrollbar", background=[("active", "SystemButtonFace")])

style.configure("TCheckbutton", background="SystemButtonFace")
style.map("TCheckbutton", indicatorcolor=[("pressed", "#ffff00"), ("selected", "#0040bf")], background=[("active", "SystemButtonFace")])

tk.Label(win, text="BukiLauncher", font=("Segoe UI", 12, "bold")).pack(padx=20, pady=(20, 0))

input_frame = tk.Frame(win, relief="raised", padx=10, pady=10, bd=1)
input_frame.pack(padx=20, pady=20, fill="x")

tk.Label(input_frame, text="Kullanıcı adı: ").grid(row=0, column=0, padx=(0, 5), pady=(0, 5))
username_entry = tk.Entry(input_frame, width=25)
username_entry.grid(row=0, column=1, pady=(0, 5))
username_entry.bind("<KeyRelease>", lambda e: save_settings())

tk.Label(input_frame, text="Sürüm: ").grid(row=1, column=0, padx=(0, 5))

version_combobox = ttk.Combobox(input_frame, values=versions, state="readonly", width=20)
version_combobox.grid(row=1, column=1, sticky="ew")
version_combobox.bind("<<ComboboxSelected>>", lambda e: save_settings())

tk.Label(input_frame, text="Fabric loader:").grid(row=2, column=0, padx=(0, 5), pady=(5, 0))

fabric_loaders_raw = minecraft_launcher_lib.fabric.get_all_loader_versions()
if isinstance(fabric_loaders_raw, tuple):
    fabric_loaders_raw = fabric_loaders_raw[0]

fabric_loaders = ["Yok"] + [v["version"] for v in fabric_loaders_raw]

fabric_combobox = ttk.Combobox(input_frame, values=fabric_loaders, state="readonly", width=20)
fabric_combobox.grid(row=2, column=1, sticky="ew", pady=(5, 0))
    
fabric_combobox.bind("<<ComboboxSelected>>", lambda e: save_settings())

snapshot_checkbutton = ttk.Checkbutton(input_frame, text="Snapshot'ları göster", variable=show_snapshots, command=change_snapshot_shown)
snapshot_checkbutton.grid(row=3, column=0, columnspan=2, pady=(5, 0))

toolbar_frame = tk.Frame(win)
toolbar_frame.pack(fill="x")

opt_toolbar = tk.Frame(toolbar_frame, relief="raised", padx=3, pady=3, bd=1)
opt_toolbar.pack(padx=20, pady=(0, 20), side="left")

about_toolbar = tk.Frame(toolbar_frame, relief="raised", padx=3, pady=3, bd=1)
about_toolbar.pack(padx=(0, 20), pady=(0, 20), side="right")

start_button = tk.Button(opt_toolbar, text="\uE768", command=launch, bd=0, activebackground="#0040bf", activeforeground="#ffffff", fg="#0040bf", width=5, pady=4, font=("segoe Fluent Icons", 10))
start_button.grid(row=0, column=0)

dir_button = tk.Button(opt_toolbar, text="\uE19C", command=open_dir, bd=0, activebackground="#ffff00", width=5, pady=4, font=("segoe Fluent Icons", 10))
dir_button.grid(row=0, column=1)

java_button = tk.Button(opt_toolbar, text="\uEC32", command=select_java, bd=0, activebackground="#ffff00", fg="#0040bf" if java_path else "#bf0000", activeforeground="#000000", width=5, pady=4, font=("segoe Fluent Icons", 10))
java_button.grid(row=0, column=2)

about_button = tk.Button(about_toolbar, text="\uE712", command=show_about, bd=0, activebackground="#ffff00", activeforeground="#000000", width=5, pady=4, font=("segoe Fluent Icons", 10))
about_button.grid(row=0, column=0)

progress_label = tk.Label(win, text="")

username_entry.insert(0, configuration["username"])
version_combobox.set(configuration["version"])

if configuration["fabric"] is not None:
    fabric_combobox.set(configuration["fabric"])
else:
    fabric_combobox.set(fabric_combobox.cget("values")[0])

def is_snapshot(version):
    return any(c.isalpha() for c in version)

def select_warning(event):
    selected = version_combobox.get()

    if is_snapshot(selected):
        messagebox.showwarning(
            "Uyarı",
            "Bu sürüm kararlı olmadığından bazı kaynak paketleri veya modlar çalışmayabilir."
        )
        return

    if version_tuple(selected) < version_tuple(threshold_version):
        messagebox.showwarning(
            "Uyarı",
            "Bu sürüm çok eski olduğu için seçtiğiniz Java yürütülebilir dosyası ile düzgün çalışmayabilir."
        )
        
version_combobox.bind("<<ComboboxSelected>>", select_warning)

ToolTip(start_button, "Başlat")
ToolTip(dir_button, "Minecraft Klasörünü Aç")
ToolTip(java_button, "Java: Seçildi" if java_path else "Java: Seçilmedi")
ToolTip(about_button, "Hakkında")

if configuration["fabric"] in fabric_loaders:
    fabric_combobox.set(configuration["fabric"])
else:
    fabric_combobox.set("Yok")

win.protocol("WM_DELETE_WINDOW", save_on_exit)
win.mainloop()