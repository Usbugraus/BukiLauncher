import traceback, datetime
from tkinter import messagebox
import os, json

data_directory = os.path.join(os.path.dirname(__file__), "Data")

with open(os.path.join(data_directory, "Dialogs.json"), "r", encoding="utf-8") as f:
    dialog_dict = json.load(f)

def error_handler(exc_type, exc_value, exc_traceback, language="english"):

    tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    try:
        dialogs = dialog_dict[language]
    except:
        dialogs = dialog_dict["english"]

    title, subtitle = dialogs["error"]

    messagebox.showerror(title, f"{subtitle}\n\n{tb_text}")

    with open("ErrorLog.txt", "a", encoding="utf-8") as f:
        f.write(f"\nDate: {datetime.datetime.now()}\n\n{tb_text}")