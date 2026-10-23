import tkinter as tk
from tkinter import ttk
from Constants import icon_path
from ErrorHandler import error_handler
from Functions import set_theme
import os, sys

sys.excepthook = error_handler

def set_jvm_arguments(parent, language_data={}, jvm_args=[], theme="light"):
    arguments = []

    window = tk.Toplevel(parent)
    window.title(language_data.get("JVMArgsEdit.Title"))
    window.resizable(False, False)
    window.transient(parent)
    window.focus_force()


    if os.path.exists(icon_path):
        icon = tk.PhotoImage(file=icon_path)
        window.iconphoto(True, icon)

    style = ttk.Style()
    style.theme_use("default")

    set_theme(window=window, theme=theme, style=style)

    ttk.Label(window, text=language_data.get("JVMArgsEdit.Title"), font=("Segoe UI", 12, "bold")).pack(padx=20, pady=20)

    main_frame = ttk.Frame(window, style="Out.TFrame", padding=10)
    main_frame.pack(padx=20, pady=(0, 20))

    ttk.Label(main_frame, text=language_data.get("JVMArgsEdit.Content"), wraplength=380, justify="center").pack(pady=(0, 10))

    jvm_frame = ttk.Frame(main_frame, style="Out.TFrame", padding=10)
    jvm_frame.pack()

    jvm_text = tk.Text(jvm_frame, height=12, width=50, font=("Consolas", 9), wrap="none")
    jvm_text.pack(side="left")

    vertical_scrollbar = ttk.Scrollbar(jvm_frame, command=jvm_text.yview, orient="vertical")
    vertical_scrollbar.pack(side="right", fill="y")

    jvm_text.config(yscrollcommand=vertical_scrollbar.set)

    set_theme(window=window, theme=theme, style=style, textfield=jvm_text)

    args = "\n".join(str(arg) for arg in jvm_args if arg is not None) if jvm_args else ""
    jvm_text.insert("1.0", args)

    def on_exit():
        nonlocal arguments
        content = jvm_text.get("1.0", "end-1c")
        arguments = [line.strip() for line in content.splitlines() if line.strip()]
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_exit)

    window.grab_set()
    parent.wait_window(window)
    return arguments