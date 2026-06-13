import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import minecraft_launcher_lib
import subprocess, threading, json, os, sys
import ctypes
import requests
from ToolTip import ToolTip
from ErrorHandler import error_handler
from JVMArgumentsEditor import edit_jvm_arguments
from About import about
from ModStore import mod_store

myappid = 'com.usbugraus.bukilauncher'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

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
mod_dir = os.path.join(mc_dir, "mods")
process = None
data_directory = os.path.join(os.path.dirname(__file__), "Data")
tooltip_labels = {}
menu_labels = {}
labels = {}
dialogs = {}
tabs = {}


if hasattr(sys, "_MEIPASS"):
    icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
else:
    icon_path = os.path.join(os.path.dirname(__file__), "Icon.ico")

with open(os.path.join(data_directory, "ToolTipLabels.json"), "r", encoding="utf-8") as f:
    tooltip_dict = json.load(f)
    
with open(os.path.join(data_directory, "MenuLabels.json"), "r", encoding="utf-8") as f:
    menu_dict = json.load(f)
    
with open(os.path.join(data_directory, "Labels.json"), "r", encoding="utf-8") as f:
    label_dict = json.load(f)
    
with open(os.path.join(data_directory, "Dialogs.json"), "r", encoding="utf-8") as f:
    dialog_dict = json.load(f)

with open(os.path.join(data_directory, "DefaultConfiguration.json"), "r", encoding="utf-8") as f:
    default_configuration = json.load(f)
    
if not os.path.exists(mc_dir):
    os.makedirs(mc_dir, exist_ok=True)
    
if os.path.exists(configuration_file):
    try:
        with open(configuration_file, "r", encoding="utf-8") as f:
            configuration = json.load(f)

        for key, value in default_configuration.items():
            configuration.setdefault(key, value)

        if configuration["fabric"] is None:
            configuration["fabric"] = "None"
    except json.JSONDecodeError:
        messagebox.showwarning("Warning", "The configuration file is corrupt. Therefore, the settings have been reset.")
        configuration = default_configuration.copy()

else:
    messagebox.showwarning("Warning", "The configuration file has been moved to another location or deleted. Therefore, the settings have been reset.")
    configuration = default_configuration.copy()
    
def is_connected(timeout=3):
    test_urls = [
        "https://piston-meta.mojang.com",
        "https://launchermeta.mojang.com",
        "https://api.minecraftservices.com"
    ]

    headers = {
        "User-Agent": "BukiLauncher"
    }

    for url in test_urls:
        try:
            response = requests.get(
                url,
                timeout=timeout,
                headers=headers
            )

            if response.status_code < 500:
                return True

        except requests.RequestException:
            pass

    return False
    
if is_connected():
    if configuration["snapshots"]:
        mc_versions = [
            v["id"]
            for v in minecraft_launcher_lib.utils.get_version_list()
            if v["type"] in ["release", "snapshot", "old_beta", "old_alpha"]
        ]
    else:
        mc_versions = [
            v["id"]
            for v in minecraft_launcher_lib.utils.get_version_list()
            if v["type"] == "release"
        ]
else:
    mc_versions = [
        v["id"]
        for v in minecraft_launcher_lib.utils.get_installed_versions(mc_dir)
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

    if sys.platform == "win32":
        os.startfile(os.path.join(mc_dir))
    elif sys.platform == "darwin":
        os.system(f'open "{os.path.join(mc_dir)}"')
    else:
        os.system(f'xdg-open "{os.path.join(mc_dir)}"')
        
def select_java():
    global dialogs
    path = filedialog.askopenfilename(
        title=dialogs["java"][0],
        filetypes=[(dialogs["java"][1], "java.exe javaw.exe")])
    if path:
        global java_path
        java_path = path
        update_settings()

def launch():
    threading.Thread(target=launch_game, daemon=True).start()

def show_progress(text):
    def update():
        progress_label.config(text=text)

        if not progress_label.winfo_ismapped():
            progress_label.pack(
                padx=20,
                pady=(0, 20),
                fill="x"
            )

    win.after(0, update)

def install_fabric(mc_version, loader):
    try:
        minecraft_launcher_lib.fabric.install_fabric(
            minecraft_version=mc_version,
            loader_version=loader,
            minecraft_directory=mc_dir
        )
    except Exception:
        error_handler(*sys.exc_info(), language=language.get())
        win.after(0, lambda: start_button.config(state="normal"))
        return False

    return True

def hide_progress():
    win.after(0, progress_label.pack_forget)


def set_status(text):
    def update():
        display_text = text if len(text) <= 30 else text[:30] + "..."

        progress_label.config(text=display_text)

        if not progress_label.winfo_ismapped():
            progress_label.pack(
                padx=20,
                pady=(0, 20),
                fill="x"
            )

    win.after(0, update)

def launch_game():
    global process, mc_dir, dialogs

    try:

        if process and process.poll() is None:
            win.after(0, lambda: messagebox.showwarning(
                dialogs["mc_warn"][0],
                dialogs["mc_warn"][1]
            ))
            hide_progress()
            return

        if not java_path:
            win.after(0, lambda: messagebox.showerror(
                dialogs["non_java"][0],
                dialogs["non_java"][1]
            ))
            hide_progress()
            return

        if java_path == "rick":
            import webbrowser

            webbrowser.open(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )

            hide_progress()

            win.after(
                0,
                lambda: start_button.config(state="normal")
            )
            return

        username = username_entry.get()
        version = version_combobox.get()
        loader = fabric_combobox.get()

        if loader != "None":
            mc_version = version
            version_id = f"fabric-loader-{loader}-{mc_version}"

            installed = {
                v["id"]
                for v in minecraft_launcher_lib.utils.get_installed_versions(mc_dir)
            }

            if version_id not in installed:
                if is_connected():
                    win.after(
                        0,
                        lambda: start_button.config(state="disabled")
                    )

                    show_progress(tooltip_labels[4])

                    ok = install_fabric(
                        mc_version,
                        loader
                    )

                    if not ok:
                        hide_progress()
                        return

                else:
                    win.after(
                        0,
                        lambda: messagebox.showerror(
                            dialogs["ver_err"][0],
                            dialogs["ver_err"][1]
                        )
                    )

                    hide_progress()
                    return

            version = version_id

        if not username:
            win.after(0, lambda: messagebox.showerror(
                dialogs["non_name"][0],
                dialogs["non_name"][1]
            ))

            hide_progress()
            return

        if not version:
            win.after(0, lambda: messagebox.showerror(
                dialogs["non_ver"][0],
                dialogs["non_ver"][1]
            ))

            hide_progress()
            return

        installed_versions = {
            v["id"]
            for v in minecraft_launcher_lib.utils.get_installed_versions(mc_dir)
        }

        if version not in installed_versions:
            if is_connected():
                win.after(
                    0,
                    lambda: start_button.config(state="disabled")
                )

                show_progress(tooltip_labels[5])

                callback = {
                    "setStatus": set_status
                }

                minecraft_launcher_lib.install.install_minecraft_version(
                    version,
                    mc_dir,
                    callback=callback
                )

            else:
                win.after(
                    0,
                    lambda: messagebox.showerror(
                        dialogs["ver_err"][0],
                        dialogs["ver_err"][1]
                    )
                )

                hide_progress()
                return

        options = {
            "username": username,
            "uuid": "00000000000000000000000000000000",
            "token": "",
            "executablePath": java_path,
            "jvmArguments": jvm_arguments
        }

        command = minecraft_launcher_lib.command.get_minecraft_command(
            version,
            mc_dir,
            options
        )

        if isinstance(command, tuple):
            command = command[0]

        if isinstance(command, dict):
            command = command.get("command", command)

        if isinstance(command, str):
            command = command.split()

        win.after(0, lambda: (
            win.withdraw()
            if hide_when_start.get()
            else hide_progress()
        ))

        process = subprocess.Popen(command)

        def wait_game():
            global process

            try:
                if process is None:
                    return

                process.wait()

            except Exception:
                error_handler(
                    *sys.exc_info(),
                    language=language.get()
                )

            finally:
                win.after(0, lambda: (
                    win.deiconify(),
                    hide_progress(),
                    start_button.config(state="normal")
                ))

        threading.Thread(
            target=wait_game,
            daemon=True
        ).start()

    except Exception:
        error_handler(
            *sys.exc_info(),
            language=language.get()
        )

        hide_progress()

        win.after(
            0,
            lambda: start_button.config(state="normal")
        )
    
def save_settings():
    username = username_entry.get()
    version = version_combobox.get()
    fabric = fabric_combobox.get()
    snapshots = show_snapshots.get()
    hide = hide_when_start.get()
    lang = language.get()
    tlp = tooltips.get()
    jvmargs = jvm_arguments
    
    if fabric == "None":
        fabric = None
    
    config = {
        "username": username,
        "version": version,
        "java_path": java_path,
        "fabric": fabric,
        "snapshots": snapshots,
        "hide_when_start": hide,
        "language": lang,
        "show_tooltip": tlp,
        "jvm_arguments": jvmargs,
    }
    
    with open(configuration_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
        
def save_on_exit():
    save_settings()
    win.destroy()
    
def show_about():
    about(win, language=language.get())
    
def update_settings(*args):
    global mc_versions, tooltip_labels, tooltip_dict, menu_dict, menu_labels, labels, label_dict, dialogs, dialog_dict, shortcut_command, java_path, mc_dir

    fabric_loaders = ["None"]

    try:
        tooltip_labels = tooltip_dict[language.get()]
        menu_labels = menu_dict[language.get()]
        labels = label_dict[language.get()]
        dialogs = dialog_dict[language.get()]
    except:
        tooltip_labels = tooltip_dict["english"]
        menu_labels = menu_dict["english"]
        labels = label_dict["english"]
        dialogs = dialog_dict["english"]
    
    if is_connected():
        if show_snapshots.get():
            mc_versions = [
                v["id"]
                for v in minecraft_launcher_lib.utils.get_version_list()
                if v["type"] in ["release", "snapshot", "old_beta", "old_alpha"]
            ]
        else:
            mc_versions = [
                v["id"]
                for v in minecraft_launcher_lib.utils.get_version_list()
                if v["type"] == "release"
            ]
        fabric_combobox.config(state="readonly")
        try:
            fabric_loaders = ["None"]

            fabric_loaders_raw = minecraft_launcher_lib.fabric.get_all_loader_versions()

            if isinstance(fabric_loaders_raw, tuple):
                fabric_loaders_raw = fabric_loaders_raw[0]

            fabric_loaders += [
                v["version"]
                for v in fabric_loaders_raw
            ]

            fabric_combobox.config(
                values=fabric_loaders,
                state="readonly"
            )

            current_fabric = configuration.get("fabric")

            if current_fabric in fabric_loaders:
                fabric_combobox.set(current_fabric)
            else:
                fabric_combobox.set("None")

        except Exception:
            fabric_combobox.config(
                values=["None"],
                state="disabled"
            )
            fabric_combobox.set("None")

    else:
        fabric_combobox.config(
            values=["None"],
            state="disabled"
        )
        fabric_combobox.set("None")

    if configuration["fabric"] in fabric_loaders:
        fabric_combobox.set(configuration["fabric"])
    else:
        fabric_combobox.set("None")
        
    version_combobox.config(values=mc_versions)
        
    username_label.config(text=labels[0])
    version_label.config(text=labels[1])
    fabric_label.config(text=labels[2])
        
    settings_menu.entryconfig(0, label=menu_labels[0])
    settings_menu.entryconfig(1, label=menu_labels[1])
    settings_menu.entryconfig(2, label=menu_labels[2])
    settings_menu.entryconfig(3, label=menu_labels[3] if java_path else menu_labels[4])
    settings_menu.entryconfig(4, label=menu_labels[5])
    settings_menu.entryconfig(5, label=menu_labels[6])
    
    ToolTip(start_button, tooltip_labels[0], shown=tooltips.get())
    ToolTip(dir_button, tooltip_labels[1], shown=tooltips.get())
    ToolTip(settings_button, tooltip_labels[2], shown=tooltips.get())
    ToolTip(about_button, tooltip_labels[3], shown=tooltips.get())
    ToolTip(store_button, tooltip_labels[10], shown=tooltips.get())

    save_settings()

def set_jvmargs():
    global jvm_arguments
    jvmargs = edit_jvm_arguments(win, language=language.get(), args=jvm_arguments)
    jvm_arguments = jvmargs
    update_settings()

win = tk.Tk()
win.title("BukiLauncher")
win.resizable(False, False)

sys.excepthook = lambda t, v, tb: error_handler(t, v, tb, language=language.get())
win.report_callback_exception = lambda t, v, tb: error_handler(t, v, tb, language=language.get())

show_snapshots = tk.BooleanVar(value=configuration["snapshots"])
language = tk.StringVar(value=configuration["language"])
tooltips = tk.BooleanVar(value=configuration["show_tooltip"])
hide_when_start = tk.BooleanVar(value=configuration["hide_when_start"])
jvm_arguments = configuration["jvm_arguments"]

if os.path.exists(icon_path):
    win.iconbitmap(icon_path)

style = ttk.Style()
style.theme_use("default")

style.configure("TFrame", background="SystemButtonFace")
style.configure("Out.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.RAISED)
style.configure("In.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.SUNKEN)

style.configure("TEntry", focuswidth=2, focuscolor="#0040bf", selectbackground="#0040bf")

style.configure("TCombobox", focuswidth=2, focuscolor="#0040bf", arrowsize=14, selectbackground="#0040bf", background="SystemButtonFace")
style.map("TCombobox", fieldbackground=[("readonly", "#ffffff"), ("disabled", "SystemButtonFace")], background=[("active", "SystemButtonFace"), ("pressed", "#ffff00")])

style.map("TButton", background="SystemButtonFace")
style.map("TButton", background=[("pressed", "#ffff00"), ("active", "SystemButtonFace")])
style.configure("ToolbarButton.TButton", background="SystemButtonFace", relief=tk.FLAT, width=5, padding=(0, 5), font=("Segoe Fluent Icons", 10))
style.map("ToolbarButton.TButton", background=[("pressed", "#ffff00"), ("active", "SystemButtonFace")], foreground=[("disabled", "#404040")])
style.configure("MarkedToolbarButton.TButton", background="SystemButtonFace", foreground="#0040bf", relief=tk.FLAT, width=5, padding=(0, 5), font=("Segoe Fluent Icons", 10))
style.map("MarkedToolbarButton.TButton", background=[("pressed", "#0040bf"), ("active", "SystemButtonFace")], foreground=[("pressed", "#ffffff"), ("active", "#0040bf"), ("disabled", "#bfbf00")])
style.configure("DangerToolbarButton.TButton", background="SystemButtonFace", foreground="#bf0000", relief=tk.FLAT, width=5, padding=(0, 5), font=("Segoe Fluent Icons", 10))
style.map("DangerToolbarButton.TButton", background=[("pressed", "#bf0000"), ("active", "SystemButtonFace")], foreground=[("pressed", "#ffffff"), ("active", "#bf0000"), ("disabled", ("#804040"))])

ttk.Label(win, text="BukiLauncher", font=("Segoe UI", 12, "bold")).pack(padx=20, pady=(20, 0))

main_frame = ttk.Frame(win, padding=10, style="Out.TFrame")
main_frame.pack(padx=20, pady=20)

username_label = ttk.Label(main_frame, text="")
username_label.grid(row=0, column=0, padx=(0, 5), pady=(0, 5))

username_entry = ttk.Entry(main_frame, width=25)
username_entry.grid(row=0, column=1, pady=(0, 5))
username_entry.bind("<KeyRelease>", lambda e: save_settings())

version_label = ttk.Label(main_frame, text="")
version_label.grid(row=1, column=0, padx=(0, 5))
 
version_combobox = ttk.Combobox(main_frame, values=versions, state="readonly", width=20, takefocus=0)
version_combobox.grid(row=1, column=1, sticky="ew")
version_combobox.bind("<<ComboboxSelected>>", lambda e: save_settings())

fabric_label = ttk.Label(main_frame, text="")
fabric_label.grid(row=2, column=0, padx=(0, 5), pady=(5, 0))

fabric_combobox = ttk.Combobox(main_frame, state="readonly", width=20, takefocus=0, values=["None"])
fabric_combobox.grid(row=2, column=1, sticky="ew", pady=(5, 0))
    
fabric_combobox.bind("<<ComboboxSelected>>", lambda e: save_settings())

toolbar_frame = ttk.Frame(win)
toolbar_frame.pack(fill="x")

opt_toolbar = ttk.Frame(toolbar_frame, style="Out.TFrame", padding=5)
opt_toolbar.pack(padx=20, pady=(0, 20), side="left")

about_toolbar = ttk.Frame(toolbar_frame, style="Out.TFrame", padding=5)
about_toolbar.pack(padx=(0, 20), pady=(0, 20), side="right")

start_button = ttk.Button(opt_toolbar, text="\uE768", command=launch, style="MarkedToolbarButton.TButton")
start_button.grid(row=0, column=0)

dir_button = ttk.Button(opt_toolbar, text="\uE19C", command=open_dir, style="ToolbarButton.TButton")
dir_button.grid(row=0, column=1)

store_button = ttk.Button(opt_toolbar, text="\uE74C", command=lambda: mod_store(win, language=language.get(), version=version_combobox.get()), style="ToolbarButton.TButton")
store_button.grid(row=0, column=2)

settings_button = ttk.Button(opt_toolbar, text="\uE115", style="ToolbarButton.TButton")
settings_button.grid(row=0, column=3)
settings_button.bind('<ButtonRelease-1>', lambda event: settings_menu.tk_popup(event.x_root, event.y_root))

about_button = ttk.Button(about_toolbar, text="\uE946", command=show_about, style="ToolbarButton.TButton")
about_button.grid(row=0, column=0)

progress_label = tk.Label(win, text="")

username_entry.insert(0, configuration["username"])
version_combobox.set(configuration["version"])

def is_snapshot(version):
    return any(c.isalpha() for c in version)

def select_warning(event):
    selected = version_combobox.get()

    if is_snapshot(selected):
        messagebox.showwarning(dialogs["snp_warn"][0], dialogs["snp_warn"][1])
        return

    if version_tuple(selected) < version_tuple(threshold_version):
        messagebox.showwarning(dialogs["old_warn"][0], dialogs["old_warn"][1])
        
version_combobox.bind("<<ComboboxSelected>>", select_warning, add="+")
    
settings_menu = tk.Menu(win, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")
settings_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=show_snapshots, command=update_settings)
settings_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=hide_when_start, command=update_settings)
settings_menu.add_checkbutton(label="", onvalue=True, offvalue=False, variable=tooltips, command=update_settings)
settings_menu.add_command(label="", command=select_java)
settings_menu.add_command(label="", command=set_jvmargs)

lang_menu = tk.Menu(settings_menu, tearoff=0, activebackground="#0040bf", activeforeground="#ffffff")
lang_menu.add_radiobutton(label='Türkçe', variable=language, value="turkish", command=update_settings)
lang_menu.add_radiobutton(label='English', variable=language, value="english", command=update_settings)
lang_menu.add_radiobutton(label='Deutsch', variable=language, value="german", command=update_settings)
lang_menu.add_radiobutton(label='Pусский', variable=language, value="russian", command=update_settings)
lang_menu.add_radiobutton(label='Español', variable=language, value="spanish", command=update_settings)
lang_menu.add_radiobutton(label='Français', variable=language, value="french", command=update_settings)

settings_menu.add_cascade(menu=lang_menu, label="")

update_settings()

if not is_connected():
    messagebox.showwarning(dialogs["intr"][0], dialogs["intr"][1])

win.protocol("WM_DELETE_WINDOW", save_on_exit)
win.mainloop()