from tkinter import messagebox
import traceback, datetime, os

current_time = datetime.datetime.now()
error_log_file = os.path.join("ErrorLogs", f"ErrorLog {current_time.strftime('%d-%m-%Y')} {current_time.strftime('%H.%M.%S')}.txt")

def error_handler(exctype, value, tb):
    error = traceback.format_exception(exctype, value, tb)
    error_text = "".join(error)

    messagebox.showerror("Error", f"An error occurred:\n\n{error_text}")
    try:
        with open(error_log_file, "a", encoding="utf-8") as f:
            f.write(error_text)
    except:
        messagebox.showerror("Error", f"Failed to log error:\n{traceback.format_exc()}")