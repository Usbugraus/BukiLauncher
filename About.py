import tkinter as tk
from tkinter import ttk
from Constants import icon_path
from PIL import Image, ImageTk
from ErrorHandler import error_handler
from Functions import set_theme
import os, sys

sys.excepthook = error_handler

def show_about(parent, language_data={}, theme="light"):
    window = tk.Toplevel(parent)
    window.resizable(False, False)
    window.title(language_data.get("About.Title"))
    window.transient(parent)
    window.attributes("-topmost", True)
    window.focus_force()

    if os.path.exists(icon_path):
        icon = tk.PhotoImage(file=icon_path)
        window.iconphoto(True, icon)

    style = ttk.Style()
    style.theme_use("default")

    set_theme(window=window, theme=theme, style=style)

    image = Image.open(icon_path)
    image = image.resize((64, 64))
    image_tk = ImageTk.PhotoImage(image)

    header_label = ttk.Label(window, text=language_data.get("About.Title"), font=("Segoe UI", 12, "bold")).pack(padx=20 , pady=20)

    main_frame = ttk.Frame(window, style="Out.TFrame", padding=10)
    main_frame.pack(padx=20, pady=(0, 20))

    image_label = ttk.Label(main_frame, image=image_tk)
    image_label.image = image_tk
    image_label.pack(padx=(0, 5), side="left")

    content_label = ttk.Label(main_frame, text=language_data.get("About.Content"))
    content_label.pack(side="right")
