from tkinter import messagebox, filedialog
import winshell, shutil, os, sys, json
import minecraft_launcher_lib
import webbrowser

mc_dir = minecraft_launcher_lib.utils.get_minecraft_directory()
mod_dir = os.path.join(mc_dir, "mods")
data_directory = os.path.join(os.path.dirname(__file__), "Data")

with open(os.path.join(data_directory, "Dialogs.json"), "r", encoding="utf-8") as f:
    dialog_dict = json.load(f)

def open_mod_dir():
    global mc_dir
    if not os.path.exists(mc_dir):
        os.makedirs(mc_dir, exist_ok=True)

    if sys.platform == "win32":
        os.startfile(mod_dir)
    elif sys.platform == "darwin":
        os.system(f'open "{mod_dir}"')
    else:
        os.system(f'xdg-open "{mod_dir}"')

def open_modrinth():
    webbrowser.open("https://modrinth.com/discover/mods?g=categories:fabric")

def delete_mod(mod_path, language="english"):
    try:
        dialogs = dialog_dict[language]
    except:
        dialogs = dialog_dict["english"]

    title, subtitle = dialogs["del_mod"]
    confirm = messagebox.askyesno(title, subtitle, icon="warning")
    if confirm:
        os.remove(mod_path)
        return os.path.basename(mod_path)

def add_mod(language="english"):
    try:
        dialogs = dialog_dict[language]
    except:
        dialogs = dialog_dict["english"]

    title, subtitle = dialogs["mod"]
    mod = filedialog.askopenfilename(title=title, filetypes=[(subtitle, "*.jar")])
    if mod:
        shutil.move(mod, mod_dir)
        return os.path.basename(mod)