import tkinter as tk
from tkinter import ttk
import os, json, sys
from ToolWindow import toolwindow

data_directory = os.path.join(os.path.dirname(__file__), "Data")

with open(os.path.join(data_directory, "Dialogs.json"), "r", encoding="utf-8") as f:
    dialog_dict = json.load(f)

def edit_jvm_arguments(parent, language="english", args=[]):

    try:
        dialogs = dialog_dict[language]
    except:
        dialogs = dialog_dict["english"]

    title, subtitle = dialogs["jvm_args"]

    if hasattr(sys, "_MEIPASS"):
        icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
    else:
        icon_path = os.path.join(os.path.dirname(__file__), "Icon.ico")

    win = tk.Toplevel(parent)
    win.title(title)
    win.resizable(False, False)
    win.lift()
    win.focus()
    win.transient(parent)
    win.focus_force()
    win.grab_set()
    toolwindow(win)

    if os.path.exists(icon_path):
        win.iconbitmap(icon_path)

    style = ttk.Style()
    style.theme_use("default")

    style.configure("TFrame", background="SystemButtonFace")
    style.configure("Out.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.RAISED)
    style.configure("In.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.SUNKEN)

    style.configure("TScrollbar", background="SystemButtonFace", troughcolor="#bfbfbf", arrowsize=14)
    style.map("TScrollbar", background=[("active", "SystemButtonFace"), ("!active", "SystemButtonFace")], relief=[("pressed", "sunken")])

    ttk.Label(win, text=title, font=("Segoe UI", 12, "bold")).pack(padx=20, pady=(20, 0))

    main_frame = ttk.Frame(win, style="Out.TFrame")
    main_frame.pack(padx=20, pady=(20))

    ttk.Label(main_frame, text=subtitle).pack(padx=20, pady=(20, 0))

    editor_frame = ttk.Frame(main_frame, style="Out.TFrame", padding=5)
    editor_frame.pack(padx=10, pady=10)

    text = tk.Text(editor_frame, bd=1, padx=5, pady=5, font=("Consolas", 9), width=60, height=12, wrap="none")

    scroll = ttk.Scrollbar(editor_frame)
    scroll.pack(side="right", fill="y")
    scroll.config(command=text.yview)

    scroll_h = ttk.Scrollbar(editor_frame, orient="horizontal")
    scroll_h.pack(side="bottom", fill="x")
    scroll_h.config(command=text.xview)

    text.config(xscrollcommand=scroll_h.set, yscrollcommand=scroll.set)
    text.pack()

    text.insert("end", "\n".join(args))

    def close():
        win.result = text.get("1.0", "end-1c").splitlines()
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", close)
    win.wait_window()
    return getattr(win, "result", [])
