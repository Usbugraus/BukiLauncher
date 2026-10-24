import tkinter as tk
from tkinter import ttk, messagebox
from ErrorHandler import error_handler
from Functions import set_theme
import os, sys

sys.excepthook = error_handler

def set_uuid(parent, language_data={}, uuid="", theme="light"):
    new_uuid = ""

    window = tk.Toplevel(parent)
    window.title(language_data.get("UUIDEdit.Title"))
    window.resizable(False, False)
    window.transient(parent)
    window.focus_force()

    style = ttk.Style()
    style.theme_use("default")

    set_theme(window=window, theme=theme, style=style)

    ttk.Label(window, text=language_data.get("UUIDEdit.Title"), font=("Segoe UI", 12, "bold")).pack(padx=20, pady=20)

    main_frame = ttk.Frame(window, style="Out.TFrame", padding=10)
    main_frame.pack(padx=20, pady=(0, 20))

    ttk.Label(main_frame, text=language_data.get("UUIDEdit.Content"), wraplength=350, justify="center").pack(pady=(0, 10))

    warning_labelframe = ttk.LabelFrame(main_frame, style="Out.TLabelframe", padding=10, text=language_data.get("UUIDEdit.Warning.Title"))
    warning_labelframe.pack(pady=(0, 10))

    ttk.Label(warning_labelframe, text=language_data.get("UUIDEdit.Warning"), wraplength=310).pack()

    uuid_entry = ttk.Entry(main_frame)
    uuid_entry.pack(fill="x")
    uuid_entry.insert(0, uuid)

    def on_exit():
        nonlocal new_uuid
        new_uuid = uuid_entry.get()
        splited = new_uuid.split("-")

        if len(splited) != 5:
            messagebox.showerror(language_data.get("Messagebox.Title.Error"), language_data.get("UUIDEdit.Error"))
            return
        else:
            if len(splited[0]) != 8 or len(splited[1]) != 4 or len(splited[2]) != 4 or len(splited[3]) != 4 or len(splited[4]) != 12:
                messagebox.showerror(language_data.get("Messagebox.Title.Error"), language_data.get("UUIDEdit.Error"))
                return

        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_exit)

    window.grab_set()
    parent.wait_window(window)
    return new_uuid