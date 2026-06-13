import tkinter as tk
from tkinter import ttk
import os, json, sys
from PIL import Image, ImageTk
import webbrowser

data_directory = os.path.join(os.path.dirname(__file__), "Data")

with open(os.path.join(data_directory, "Dialogs.json"), "r", encoding="utf-8") as f:
    dialog_dict = json.load(f)

def about(parent, language="english"):
    try:
        dialogs = dialog_dict[language]
    except:
        dialogs = dialog_dict["english"]

    title, subtitle = dialogs["about"]

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

    if hasattr(sys, "_MEIPASS"):
        icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
    else:
        icon_path = os.path.join(os.path.dirname(__file__), "Icon.ico")

    if os.path.exists(icon_path):
        win.iconbitmap(icon_path)

    image = Image.open(icon_path)
    image = image.resize((64, 64))
    image_tk = ImageTk.PhotoImage(image)

    if os.path.exists(icon_path):
        win.iconbitmap(icon_path)

    style = ttk.Style()
    style.theme_use("default")

    style.configure("TFrame", background="SystemButtonFace")
    style.configure("Out.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.RAISED)
    style.configure("In.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.SUNKEN)
    style.map("TButton", background="SystemButtonFace")
    style.map("TButton", background=[("pressed", "#ffff00"), ("active", "SystemButtonFace"), ("!active", "SystemButtonFace")])
    style.configure("ToolbarButton.TButton", background="SystemButtonFace", relief=tk.FLAT, width=5, padding=(0, 5), font=("Segoe Fluent Icons", 10))
    style.map("ToolbarButton.TButton", background=[("pressed", "#ffff00"), ("active", "SystemButtonFace")], foreground=[("disabled", "#404040")])
    style.configure("LabeledToolbarButton.TButton", background="SystemButtonFace", relief=tk.FLAT, padding=(0, 5))
    style.map("LabeledToolbarButton.TButton", background=[("pressed", "#ffff00"), ("active", "SystemButtonFace")], foreground=[("disabled", "#404040")])

    ttk.Label(win, text=title, font=("Segoe UI", 12, "bold")).pack(padx=20, pady=20)

    main_frame = ttk.Frame(win, padding=10, style="Out.TFrame")
    main_frame.pack(padx=20,pady=(0, 20))

    icon = ttk.Label(main_frame, image=image_tk)
    icon.image = image_tk
    icon.grid(row=0, column=0, padx=(0, 10))

    ttk.Label(main_frame, text=subtitle).grid(row=0, column=1)

    toolbar = ttk.Frame(win, padding=5, style="Out.TFrame")
    toolbar.pack(padx=20, pady=(0, 20), fill="x", expand=True)

    ttk.Button(toolbar, text="Youtube", command=lambda: webbrowser.open("https://www.youtube.com/channel/UCLWr8Z-n-u4hZsa3rVTLTWQ"), style="LabeledToolbarButton.TButton").pack(fill="x")
    ttk.Button(toolbar, text="GitHub", command=lambda: webbrowser.open("https://www.github.com/Usbugraus"), style="LabeledToolbarButton.TButton").pack(fill="x")

