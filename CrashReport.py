import tkinter as tk
from tkinter import ttk
from Functions import set_theme

def crash_report(parent=None, language_data={}, stderr=None, theme="light"):
    window = tk.Toplevel(parent)
    window.title(language_data.get("CrashReport.Title"))
    window.resizable(False, False)
    window.transient(parent)
    window.focus_force()

    style = ttk.Style()
    style.theme_use("default")

    ttk.Label(window, text=language_data.get("CrashReport.Title"), font=("Segoe UI", 12, "bold")).pack(padx=20, pady=20)

    main_frame = ttk.Frame(window, padding=10, style="Out.TFrame")
    main_frame.pack(padx=20, pady=(0, 20))

    ttk.Label(main_frame, text=language_data.get("CrashReport.Content")).pack(padx=0, pady=(0, 10))

    crash_text = tk.Text(main_frame, height=25, width=75, wrap="none", font=("Consolas", 9))
    crash_text.pack()
    crash_text.insert("1.0", stderr)
    crash_text.config(state="disabled")

    set_theme(window=window, theme=theme, style=style, textfield=crash_text)
