import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from Functions import is_connected, get_minecraft_versions, is_version_installed, launch_minecraft, update_widgets, open_minecraft_directory, set_theme
from MCInstaller import install
from Constants import icon_path, configuration_file, default_configuration_file, language_configuration_file, fonts_directory, theme_configuration_file
from Tooltips import Tooltip
from JVMArgsEdit import set_jvm_arguments
from ErrorHandler import error_handler
from About import show_about
from UUIDEdit import set_uuid
from CrashReport import crash_report
from ModManager import mod_manager
import os, json, sys, minecraft_launcher_lib, ctypes, threading

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

sys.excepthook = error_handler

win = tk.Tk()
win.title("BukiLauncher")
win.resizable(False, False)

if os.path.exists(icon_path):
    win.iconbitmap(icon_path)

if os.path.exists(default_configuration_file):
    with open(default_configuration_file, "r", encoding="utf-8") as f:
        default_configuration = json.load(f)
else:
    messagebox.showerror("Error", "The default configuration file not found.")
    sys.exit()

if os.path.exists(language_configuration_file):
    with open(language_configuration_file, "r", encoding="utf-8") as f:
        language_configuration = json.load(f)
else:
    messagebox.showerror("Error", "The language configuration file not found.")
    sys.exit()

if os.path.exists(theme_configuration_file):
    with open(theme_configuration_file, "r", encoding="utf-8") as f:
        theme_configuration = json.load(f)
else:
    messagebox.showerror("Error", "The theme configuration file not found.")
    sys.exit()

if os.path.exists(configuration_file):
    try:
        with open(configuration_file, "r", encoding="utf-8") as f:
            configuration = json.load(f)

        for key, value in default_configuration.items():
            configuration.setdefault(key, value)

    except json.JSONDecodeError:
        messagebox.showwarning("Warning", "The configuration file is corrupt. Therefore, the settings have been reset.")
        configuration = default_configuration.copy()
else:
    messagebox.showwarning("Warning", "The configuration file has been moved to another location or deleted. Therefore, the settings have been reset.")
    configuration = default_configuration.copy()

try:
    language_file = os.path.join("Resources", "Languages", f"{configuration.get("language")}.json")

    with open(language_file, "r", encoding="utf-8") as f:
        language_data = json.load(f)
except FileNotFoundError:
    messagebox.showerror("Error", "The language data not found.")
    sys.exit()
except json.JSONDecodeError as e:
    messagebox.showerror("Error", "The language data is corrupt.")
    sys.exit()

snapshots_variable = tk.BooleanVar(value=configuration.get("show_snapshots"))
hide_when_launch_variable = tk.BooleanVar(value=configuration.get("hide_when_launch"))
tooltips_variable = tk.BooleanVar(value=configuration.get("show_tooltips"))
theme_variable = tk.StringVar(value=configuration.get("theme"))
language_variable = tk.StringVar(value=configuration.get("language"))

if configuration.get("java_path") is not None:
    if os.path.exists(configuration.get("java_path")):
        java = configuration.get("java_path")
    else:
        java = None
else:
    java = None

jvm_args = configuration.get("jvm_args")
uuid = configuration.get("uuid")

if configuration.get("minecraft_directory") is not None:
    if os.path.exists(configuration.get("minecraft_directory")):
        minecraft_directory = configuration.get("minecraft_directory")
    else:
        minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
else:
    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()

style = ttk.Style()
style.theme_use("default")

header_label = ttk.Label(win, text="BukiLauncher", font=("Segoe UI", 12, "bold"))
header_label.pack(padx=20, pady=20)

options_frame = ttk.Frame(win, style="Out.TFrame", padding=10)
options_frame.pack(padx=20, pady=(0, 20))

username_label = ttk.Label(options_frame, text="")
version_label = ttk.Label(options_frame, text="")
loader_label = ttk.Label(options_frame, text="")
loader_version_label = ttk.Label(options_frame, text="")

username_entry = ttk.Entry(options_frame, width=25)
version_combobox = ttk.Combobox(options_frame, width=20, style="TCombobox", values=[], state="readonly")
loader_combobox = ttk.Combobox(options_frame, width=20, style="TCombobox", values=["Vanilla", "Fabric", "Forge", "NeoForge", "Quilt"], state="readonly")
loader_version_combobox = ttk.Combobox(options_frame, width=20, style="TCombobox", values=[], state="readonly")

username_entry.grid(row=0, column=1, pady=(0, 5))
username_label.grid(row=0, column=0, padx=(0, 5), pady=(0, 5))
version_label.grid(row=1, column=0, padx=(0, 5), pady=(0, 5))
version_combobox.grid(row=1, column=1, pady=(0, 5), sticky="ew")
loader_label.grid(row=2, column=0, padx=(0, 5), pady=(0, 5))
loader_combobox.grid(row=2, column=1, pady=(0, 5), sticky="ew")
loader_version_label.grid(row=3, column=0, padx=(0, 5))
loader_version_combobox.grid(row=3, column=1, sticky="ew")

username_entry.insert(0, configuration.get("username"))
version_combobox.set(configuration.get("version"))
loader_combobox.set(configuration.get("loader"))
loader_version_combobox.set(configuration.get("loader_version"))

def select_java(parent=None):
    global java

    java_path = filedialog.askopenfilename(parent=parent, filetypes=[(language_data.get("SelectJava.Executable"), "java.exe javaw.exe")], title=language_data.get("SelectJava.Title"))
    if java_path:
        java = java_path

    threading.Thread(target=update_settings, daemon=True).start()

def select_minecraft_directory(parent=None):
    global minecraft_directory

    new_directory = filedialog.askdirectory(parent=parent, title=language_data.get("SelectMCDir.Title"))
    if new_directory:
        minecraft_directory = new_directory

    threading.Thread(target=update_settings, daemon=True).start()

def launch():
    if java:
        if not len(username_entry.get()) >= 3 and len(username_entry.get()) <= 16:
            messagebox.showwarning(language_data.get("Messagebox.Title.Warning"), language_data.get("Messagebox.Content.UsernameWarning"))
            return

        installed = is_version_installed(
            version=version_combobox.get(),
            mod_loader=loader_combobox.get().lower(),
            loader_version=loader_version_combobox.get(),
            minecraft_directory=minecraft_directory
        )

        if installed:
            out = launch_minecraft(
                window=win,
                username=username_entry.get(),
                version=version_combobox.get(),
                mod_loader=loader_combobox.get().lower(),
                loader_version=loader_version_combobox.get(),
                java_path=java,
                hide_window=hide_when_launch_variable.get(),
                jvm_arguments=jvm_args,
                minecraft_directory=minecraft_directory
            )
            if out[2] != 0:
                crash_report(win, language_data=language_data, stderr=out[1], theme=theme_variable.get())
        else:
            try:
                install(
                    parent=win,
                    language_data=language_data,
                    theme=theme_variable.get(),
                    version=version_combobox.get(),
                    mod_loader=loader_combobox.get().lower(),
                    loader_version=loader_version_combobox.get(),
                    java_path=java,
                    minecraft_directory = minecraft_directory
                )
            except:
                messagebox.showerror(language_data.get("Messagebox.Title.Error"), language_data.get("Messagebox.Content.InstallError"))
    else:
        messagebox.showerror(language_data.get("Messagebox.Title.Warning"), language_data.get("Messagebox.Content.NoJavaWarning"))

def save_settings():
    configuration = {
        "username": username_entry.get(),
        "version": version_combobox.get(),
        "loader": loader_combobox.get(),
        "loader_version": loader_version_combobox.get(),
        "show_snapshots": snapshots_variable.get(),
        "hide_when_launch": hide_when_launch_variable.get(),
        "show_tooltips": tooltips_variable.get(),
        "java_path": java,
        "minecraft_directory": minecraft_directory,
        "jvm_args": jvm_args,
        "uuid": uuid,
        "theme": theme_variable.get(),
        "language": language_variable.get()
    }

    with open(configuration_file, "w", encoding="utf-8") as f:
        json.dump(configuration, f, indent=4)


def update_settings(event=None):
    global language_data

    triggered_widget = event.widget if event else None

    language_file = os.path.join("Resources", "Languages", language_configuration.get(language_variable.get()).get("file"))

    with open(language_file, "r", encoding="utf-8") as f:
        language_data = json.load(f)

    set_theme(
        theme=theme_variable.get(),
        window=win,
        style=style,
        menus={
            "settings": settings_menu,
            "themes": theme_menu,
            "languages": language_menu
        },
        java_selected=java
    )

    update_widgets(
        widgets=[
            username_label,
            version_label,
            loader_label,
            loader_version_label
        ],
        tooltips=[
            launch_tooltip,
            open_dir_tooltip,
            settings_tooltip,
            mod_manager_tooltip
        ],
        menus={
            "settings": settings_menu,
            "themes": theme_menu
        },
        language_data=language_data,
        java_selected=java,
        theme=theme_variable.get()
    )

    versions = get_minecraft_versions(
        mod_loader=loader_combobox.get().lower(),
        version=version_combobox.get(),
        snapshots=snapshots_variable.get(),
        minecraft_directory=minecraft_directory
    )

    version_combobox.config(values=versions[0])
    loader_version_combobox.config(values=versions[1])

    if len(versions[0]) > 0 or len(versions[1]) > 0:
        if version_combobox.get() not in versions[0]:
            version_combobox.set(versions[0][0])

        if triggered_widget == loader_combobox:
            if loader_combobox.get().lower() != "vanilla" and versions[1]:
                loader_version_combobox.set(versions[1][0])
            else:
                loader_version_combobox.set("")

    if not is_connected():
        loader_combobox.set("Vanilla")
        loader_version_combobox.config(values=[])
        loader_version_combobox.set("")

    loader_combobox.config(state="readonly" if is_connected() else "disabled")
    loader_version_combobox.config(state="readonly" if is_connected() else "disabled")
    mod_manager_button.config(state="disabled" if loader_combobox.get() == "Vanilla" else "normal")

    save_settings()

def edit_jvm_args():
    global jvm_args

    new_arguments = set_jvm_arguments(win, language_data=language_data, jvm_args=jvm_args, theme=theme_variable.get())
    jvm_args = new_arguments

    threading.Thread(target=update_settings, daemon=True).start()

def edit_uuid():
    global uuid

    new_uuid = set_uuid(win, language_data=language_data, uuid=uuid, theme=theme_variable.get())
    uuid = new_uuid

    threading.Thread(target=update_settings, daemon=True).start()

toolbar = ttk.Frame(win, name="toolbar")
toolbar.pack(padx=20, pady=(0, 20), fill="x")

launch_button = ttk.Button(toolbar, text="\ue102", style="MarkedToolbarButton.TButton", command=launch, name="launch_button")
launch_button.grid(row=0, column=0)
launch_tooltip = Tooltip(launch_button, text="")

open_dir_button = ttk.Button(toolbar, text="\ue197", style="ToolbarButton.TButton", command=lambda: open_minecraft_directory(minecraft_directory=minecraft_directory))
open_dir_button.grid(row=0, column=1)
open_dir_tooltip = Tooltip(open_dir_button, text="")

mod_manager_button = ttk.Button(toolbar, text="\ue74c", style="ToolbarButton.TButton", command=lambda: threading.Thread(target=lambda: mod_manager(parent=win, version=version_combobox.get(), loader=loader_combobox.get(), theme=theme_variable.get(), language_data=language_data, minecraft_directory=minecraft_directory), daemon=True).start())
mod_manager_button.grid(row=0, column=2)
mod_manager_tooltip = Tooltip(mod_manager_button, text="")

settings_button = ttk.Button(toolbar, text="\ue115", style="ToolbarButton.TButton")
settings_button.grid(row=0, column=3)
settings_button.bind('<ButtonRelease-1>', lambda event: settings_menu.tk_popup(event.x_root, event.y_root))
settings_tooltip = Tooltip(settings_button, text="")

username_entry.bind("<KeyRelease>", update_settings)
version_combobox.bind("<<ComboboxSelected>>", update_settings)
loader_combobox.bind("<<ComboboxSelected>>", update_settings)
loader_version_combobox.bind("<<ComboboxSelected>>", update_settings)

settings_menu = tk.Menu(win, tearoff=0)
settings_menu.add_checkbutton(variable=snapshots_variable, command=update_settings)
settings_menu.add_checkbutton(variable=hide_when_launch_variable, command=update_settings)
settings_menu.add_checkbutton(variable=tooltips_variable, command=update_settings)
settings_menu.add_command(command=select_java)
settings_menu.add_command(command=select_minecraft_directory)
settings_menu.add_command(command=edit_jvm_args)
settings_menu.add_command(command=edit_uuid)

theme_menu = tk.Menu(settings_menu, tearoff=0)
for thm in theme_configuration:
    thmconf = theme_configuration.get(thm)
    theme_menu.add_radiobutton(value=thmconf.get("value"), variable=theme_variable, command=update_settings)

language_menu = tk.Menu(settings_menu, tearoff=0)
for lang in language_configuration:
    langconf = language_configuration.get(lang)
    language_menu.add_radiobutton(label=langconf.get("label"), value=langconf.get("value"), variable=language_variable, command=update_settings)

settings_menu.add_cascade(menu=theme_menu)
settings_menu.add_cascade(menu=language_menu)
settings_menu.add_separator()
settings_menu.add_command(command=lambda:show_about(win, language_data=language_data, theme=theme_variable.get()))

threading.Thread(target=update_settings, daemon=True).start()

if not is_connected():
    messagebox.showwarning(language_data.get("Messagebox.Title.Warning"), language_data.get("Messagebox.Content.NetworkWarning"))

win.mainloop()