import traceback, datetime
from tkinter import messagebox

def error_handler(exc_type, exc_value, exc_traceback, language="english"):

    tb_text = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    if language == "türkçe":
        title = "Hata"
        subtitle = "Bir hata oluştu: "
    elif language == "english":
        title = "Error"
        subtitle = "An error occured: "
    elif language == "deutsch":
        title = "Fehler"
        subtitle = "Ein Fehler ist aufgetreten: "
    elif language == "русский":
        title = "Ошибка"
        subtitle = "Произошла ошибка: "

    messagebox.showerror(title, f"{subtitle}\n\n{tb_text}")

    with open("ErrorLog.txt", "a", encoding="utf-8") as f:
        f.write(f"\nDate: {datetime.datetime.now()}\n\n{tb_text}")

