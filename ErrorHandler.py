import tkinter as tk
import traceback
from ToolWindow import toolwindow
import os, sys

def error_handler(exc_type, exc_value, exc_traceback, parent):
    tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    errorwin = tk.Toplevel(parent)
    errorwin.title("Hata")
    
    if hasattr(sys, "_MEIPASS"):
        icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
    else:
        icon_path = os.path.join(os.path.dirname(__file__), "Icon.ico")

    if os.path.exists(icon_path):
        errorwin.iconbitmap(icon_path)
        
    errorwin.resizable(False, False)
    errorwin.transient(parent)
    errorwin.lift()
    errorwin.focus_force()
    toolwindow(errorwin)
    errorwin.grab_set()
    
    frame = tk.Frame(errorwin, bd=1, relief="raised")
    frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    tk.Label(frame, text="Bir hata oluştu: ").pack(anchor="nw", padx=5, pady=(5, 0))
    
    error = tk.Text(frame, bd=1, font=("Consolas", 9), width=50, height=20, wrap="none", padx=5, pady=5)
    error.insert(1.0, traceback.format_exc())
    error.config(state="disabled")
    
    scroll = tk.Scrollbar(frame, orient="vertical")
    scroll.pack(padx=(0, 5), pady=5, fill="y", side='right')
    scroll.config(command=error.yview)
    
    scroll2 = tk.Scrollbar(frame, orient="horizontal")
    scroll2.pack(padx=5, pady=(0, 5), fill="x", side='bottom')
    scroll2.config(command=error.xview)
    
    error.config(yscrollcommand=scroll.set)
    error.config(xscrollcommand=scroll2.set)
    error.pack(padx=(5, 0), pady=(5, 0), fill="both", expand=True)
    
    frame2 = tk.Frame(errorwin, bd=1, relief="raised")
    frame2.pack(padx=20, pady=(0, 20))
    
    def copy_error():
         error_content = error.get("1.0", "end-1c")
         error.clipboard_clear()
         error.clipboard_append(error_content)
         cp.config(state="disabled")
    
    ok = tk.Button(frame2, text="Tamam", bd=0, command=lambda: errorwin.destroy(), width=10, activebackground="#ffff00")
    ok.grid(padx=(3, 0), pady=3, row=0, column=0)
    cp = tk.Button(frame2, text="Kopyala", bd=0, command=copy_error, width=10, activebackground="#ffff00")
    cp.grid(padx=3, pady=3, row=0, column=1)
