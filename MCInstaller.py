import minecraft_launcher_lib, threading
import tkinter as tk
from tkinter import ttk
from ErrorHandler import error_handler
from Functions import set_theme
import sys, time

sys.excepthook = error_handler


def install_minecraft(version="", mod_loader="vanilla", loader_version="", finish_callback=None, java_path="",
                      minecraft_directory=""):
    max_retries = 3
    attempt = 0

    while attempt < max_retries:
        try:
            if mod_loader == "vanilla":
                minecraft_launcher_lib.install.install_minecraft_version(version=version,
                                                                         minecraft_directory=minecraft_directory)
            else:
                loader = minecraft_launcher_lib.mod_loader.get_mod_loader(mod_loader)
                loader.install(minecraft_version=version, loader_version=loader_version, minecraft_directory=minecraft_directory, java=java_path)

            if finish_callback:
                finish_callback()
            return True

        except Exception as e:
            attempt += 1
            if attempt >= max_retries:
                if finish_callback:
                    finish_callback()
                return e

            time.sleep(2)

class InstallerFrame():
    def __init__(self, parent=None, language_data=None, theme="light"):
        self.parent = parent
        self.language_data = language_data
        self.theme = theme

        self.style = ttk.Style()
        self.style.theme_use("default")

        set_theme(theme=self.theme, style=self.style)

        self.main_frame = ttk.Frame(self.parent, borderwidth=1, relief="raised", padding=10)

        self.label = ttk.Label(self.main_frame, text=language_data.get("InstallMC.Installing"), wraplength=250, justify="center")
        self.label.pack()

        self.progressbar = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, mode="indeterminate", length=300)
        self.progressbar.pack(fill="x", pady=(5, 0))

    def install(self, version="", mod_loader="vanilla", loader_version="", java_path="", minecraft_directory=""):
        def finish():
            self.progressbar.stop()
            self.main_frame.grid_forget()

        self.main_frame.grid(row=2, sticky="ew", padx=20, pady=(0, 20))
        self.label.config(text=self.language_data.get("InstallMC.Installing"))
        self.progressbar.pack(fill="x", pady=(5, 0))
        self.progressbar.start(10)
        ins = install_minecraft(version=version, mod_loader=mod_loader, loader_version=loader_version, java_path=java_path, minecraft_directory=minecraft_directory, finish_callback=finish)

        if ins is not True:
            print(ins)
            self.label.config(text=self.language_data.get("InstallMC.InstallError"))
            self.progressbar.stop()
            self.progressbar.pack_forget()
            self.main_frame.after(5000, lambda: self.main_frame.grid_forget())
        elif ins is True:
            self.label.config(text=self.language_data.get("InstallMC.Installing"))
            self.progressbar.start(10)

    def configure(self, language_data=None, theme="light"):
        self.language_data = language_data
        self.theme = theme
        self.progressbar.stop()
        self.main_frame.grid_forget()