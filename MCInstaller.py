import minecraft_launcher_lib, multiprocessing, os
import tkinter as tk
from tkinter import ttk
from ErrorHandler import error_handler
from Functions import set_theme
import sys

sys.excepthook = error_handler

def install_minecraft(version="", mod_loader="vanilla", loader_version="", finish_callback=None, java_path="", minecraft_directory=""):
    if mod_loader == "vanilla":
        minecraft_launcher_lib.install.install_minecraft_version(version=version, minecraft_directory=minecraft_directory)
    else:
        loader = minecraft_launcher_lib.mod_loader.get_mod_loader(mod_loader)
        loader.install(minecraft_version=version, loader_version=loader_version, minecraft_directory=minecraft_directory, java=java_path)

    if finish_callback:
        finish_callback()

def install(parent=None, language_data={}, theme="light" ,version="", mod_loader="vanilla", loader_version="", java_path="", minecraft_directory=""):
    window = tk.Toplevel(parent)
    window.title(language_data.get("InstallMC.Title"))
    window.resizable(False, False)
    window.transient()
    window.focus_force()

    style = ttk.Style()
    style.theme_use("default")

    set_theme(window=window, theme=theme, style=style)

    main_frame = ttk.Frame(window, style="Out.TFrame", padding=10)
    main_frame.pack(padx=20, pady=20)

    label = ttk.Label(main_frame, text=language_data.get("InstallMC.Content"), wraplength=200, justify="center")
    label.pack(pady=(0, 5))

    progressbar = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, mode="indeterminate", length=300)
    progressbar.pack()
    progressbar.start(10)

    def finish():
        progressbar.stop()
        if download.is_alive():
            download.kill()
            download.join()
        window.destroy()

    download = multiprocessing.Process(
        target=install_minecraft,
        kwargs={
            "version": version,
            "mod_loader": mod_loader,
            "loader_version": loader_version,
            "java_path": java_path,
            "minecraft_directory": minecraft_directory,
        },
    )
    download.start()