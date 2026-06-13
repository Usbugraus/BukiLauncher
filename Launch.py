from tkinter import messagebox
import traceback, datetime, ctypes, sys

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

try:
    import Main

except Exception:
    messagebox.showerror(
        "Error",
        f"An error occured while starting BukiHTML:\n{traceback.format_exc()}"
    )
    try:
        with open("ErrorLog.txt", "a", encoding="utf-8") as f:
            f.write(f"\nDate: {datetime.datetime.now()}\n\n{traceback.format_exc()}")
    except:
        messagebox.showerror(
            "Error",
            "Failed to log error"
        )
    finally:
        sys.exit(1)

