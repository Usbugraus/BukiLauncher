from tkinter import messagebox
import traceback, datetime, os
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

current_time = datetime.datetime.now()
error_log_file = os.path.join("ErrorLogs", f"ErrorLog {current_time.strftime('%d-%m-%Y')} {current_time.strftime('%H.%M.%S')}.txt")

try:
    import Main
except:
    messagebox.showerror("Error", f"An error occured while starting BukiLauncher:\n{traceback.format_exc()}")
    os.makedirs("ErrorLogs", exist_ok=True)

    try:
        with open(error_log_file, "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
    except:
        messagebox.showerror("Error", f"Failed to log error:\n{traceback.format_exc()}")