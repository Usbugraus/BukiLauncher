import tkinter as tk
from tkinter import ttk, messagebox
import minecraft_launcher_lib
import subprocess, threading, json, os, sys
import ctypes
from ToolTip import ToolTip

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

mc_versions = [
    v["id"]
    for v in minecraft_launcher_lib.utils.get_version_list()
    if v["type"] == "release"
]

versions = []
for v in mc_versions:
    versions.append(v)
    versions.append(f"{v} (Fabric)")
    
if not os.path.exists(mc_dir):
    os.makedirs(mc_dir, exist_ok=True)

installed_versions = minecraft_launcher_lib.utils.get_installed_versions(mc_dir)

for v in installed_versions:
    vid = v["id"]

    if vid.startswith("fabric-loader-"):
        continue

    if vid not in versions:
        versions.append(vid)
    
if os.path.exists(configuration_file):
    with open(configuration_file, "r", encoding="utf-8") as f:
        configuration = json.load(f)
else:
    configuration = {
        "username": "Player",
        "version": "1.21.11",
        "java_path": None,
        "fabric": "0.18.4"
    }
    
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
        filetypes=[("Java Executable", "java.exe")])
    if path:
        global java_path
        java_path = path
        java_button.config(fg="#0040bf")
        ToolTip(java_button, "Java: Seçildi" if java_path else "Java: Seçilmedi")

def launch():
    threading.Thread(target=launch_game, daemon=True).start()

def launch_game():
    global process, mc_dir
    
    progress_label.pack(pady=(0, 20), padx=20, fill="x")
        
    if not java_path:
        messagebox.showerror("Hata", "Java yürütülebilir dosyası seçilmedi. Java yürütülebilir dosyası olmadan Minecraft çalışamaz.")
        return
    
    username = username_entry.get()
    version = version_combobox.get()
    
    if version.endswith("(Fabric)"):
        mc_version = version.replace(" (Fabric)", "")
        loader = fabric_combobox.get()

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
        return

    if not version:
        messagebox.showerror("Hata", "Lütfen bir sürüm seçin.")
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
        
        progress_label.config(text="")
        win.withdraw()
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
            win.after(0, win.deiconify)
            progress_label.pack_forget()

    if process is not None:
        threading.Thread(target=wait_game, daemon=True).start()


def install_fabric(mc_version, loader):
    mc_dir = minecraft_launcher_lib.utils.get_minecraft_directory()
    version_id = f"fabric-loader-{loader}-{mc_version}"

    installed = {
        v["id"]
        for v in minecraft_launcher_lib.utils.get_installed_versions(mc_dir)
    }

    if mc_version not in installed:
        messagebox.showerror("Hata", f"Fabric kurulabilmesi için önce vanilla {mc_version} kurulmalıdır.")
        return False

    if version_id in installed:
        return True

    minecraft_launcher_lib.fabric.install_fabric(
        minecraft_version=mc_version,
        loader_version=loader,
        minecraft_directory=mc_dir
    )

    return True
    
def set_status(text):
    if len(text) < 30:
        progress_label.config(text=text)
    else:
        progress_label.config(text=text[:30] + "...")
        
    win.update_idletasks()
    
def save_on_exit():
    username = username_entry.get()
    version = version_combobox.get()
    fabric = fabric_combobox.get()
    
    configuration = {
        "username": username,
        "version": version,
        "java_path": java_path,
        "fabric": fabric
    }
    
    with open(configuration_file, "w", encoding="utf-8") as f:
        json.dump(configuration, f, ensure_ascii=False, indent=4)
        
    win.destroy()
    
def show_about():
    messagebox.showinfo("Hakkında", "BukiLauncher v1.0.0\n© Telif hakkı 2025-2026 Buğra US")

win = tk.Tk()
win.title("BukiLauncher")
win.resizable(False, False)

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

tk.Label(win, text="BukiLauncher", font=("Segoe UI", 12, "bold")).pack(padx=20, pady=(20, 0))

input_frame = tk.Frame(win, relief="raised", padx=10, pady=10, bd=1)
input_frame.pack(padx=20, pady=20, fill="x")

tk.Label(input_frame, text="Kullanıcı Adı: ").grid(row=0, column=0, padx=(0, 5), pady=(0, 5))
username_entry = tk.Entry(input_frame, width=25)
username_entry.grid(row=0, column=1, pady=(0, 5))

tk.Label(input_frame, text="Sürüm: ").grid(row=1, column=0, padx=(0, 5))

version_combobox = ttk.Combobox(input_frame, values=versions, state="readonly", width=20)
version_combobox.grid(row=1, column=1, sticky="ew")

tk.Label(input_frame, text="Fabric Loader:").grid(row=2, column=0, padx=(0, 5), pady=(5, 0))

fabric_loaders_raw = minecraft_launcher_lib.fabric.get_all_loader_versions()
fabric_loaders = [v["version"] for v in fabric_loaders_raw]

fabric_combobox = ttk.Combobox(input_frame, values=fabric_loaders, state="readonly", width=20)
fabric_combobox.grid(row=2, column=1, sticky="ew", pady=(5, 0))
fabric_combobox.set(fabric_loaders[0])

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
fabric_combobox.set(configuration["fabric"])

def select_warning(event):
    selected = version_combobox.get().replace(" (Fabric)", "")
    
    if version_tuple(selected) < version_tuple(threshold_version):
        messagebox.showwarning("Uyarı", "Bu sürüm çok eski olduğu için seçtiğiniz Java ile düzgün çalışmayabilir.")

def on_version_change(event):
    selected = version_combobox.get()

    if selected.endswith("(Fabric)"):
        fabric_combobox.config(state="readonly")
    else:
        fabric_combobox.config(state="disabled")

version_combobox.bind("<<ComboboxSelected>>", select_warning)
version_combobox.bind("<<ComboboxSelected>>", on_version_change, add="+")
win.protocol("WM_DELETE_WINDOW", save_on_exit)

ToolTip(start_button, "Başlat")
ToolTip(dir_button, "Minecraft Klasörünü Aç")
ToolTip(java_button, "Java: Seçildi" if java_path else "Java: Seçilmedi")
ToolTip(about_button, "Hakkında")

if version_combobox.get().endswith("(Fabric)"):
    fabric_combobox.config(state="readonly")
else:
    fabric_combobox.config(state="disabled")

win.mainloop()