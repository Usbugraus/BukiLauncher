from tkinter import messagebox
import traceback, datetime, ctypes, sys

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

try:
    import Main

except Exception as e:
    error = traceback.format_exc()

    messagebox.showerror(
        "Error",
        f"An error occured while starting BukiLauncher:\n{error}"
    )

    with open("ErrorLog.txt", "a", encoding="utf-8") as f:
        f.write(f"\nDate: {datetime.datetime.now()}\n\n{error}")

    sys.exit(1)