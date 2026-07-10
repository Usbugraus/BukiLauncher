import tkinter as tk
from tkinter import ttk, filedialog
import requests, hashlib
import os, sys, shutil, json, zipfile
import threading
import minecraft_launcher_lib
import ctypes
from ToolWindow import toolwindow
from ToolTip import ToolTip

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except:
        pass

API_SEARCH = "https://api.modrinth.com/v2/search"
API_VERSION = "https://api.modrinth.com/v2/project/{}/version"
mc_mods_directory = os.path.join(
    minecraft_launcher_lib.utils.get_minecraft_directory(),
    "mods"
)
data_directory = os.path.join(os.path.dirname(__file__), "Data")
configuration_file = "Configuration.json"

with open(os.path.join(data_directory, "Dialogs.json"), "r", encoding="utf-8") as f:
    dialog_dict = json.load(f)

with open(os.path.join(data_directory, "Labels.json"), "r", encoding="utf-8") as f:
    label_dict = json.load(f)

with open(os.path.join(data_directory, "ToolTipLabels.json"), "r", encoding="utf-8") as f:
    tooltip_dict = json.load(f)

def mod_store(parent, version="26.1.2", language="english", loader="fabric", tooltips=True):
    page = 0
    limit = 5
    total_hits = 0
    page_cache = {}
    file_cache = {}
    search_var = tk.StringVar()
    search_after_id = None

    try:
        dialogs = dialog_dict[language]
        labels = label_dict[language]
        tooltip_labels = tooltip_dict[language]
    except:
        dialogs = dialog_dict["english"]
        labels = label_dict["english"]
        tooltip_labels = tooltip_dict["english"]

    if hasattr(sys, "_MEIPASS"):
        icon_path = os.path.join(sys._MEIPASS, "Icon.ico")
    else:
        icon_path = os.path.join(os.path.dirname(__file__), "Icon.ico")

    def open_dir():
        if not os.path.exists(mc_mods_directory):
            os.makedirs(mc_mods_directory, exist_ok=True)

        if sys.platform == "win32":
            os.startfile(os.path.join(mc_mods_directory))
        elif sys.platform == "darwin":
            os.system(f'open "{os.path.join(mc_mods_directory)}"')
        else:
            os.system(f'xdg-open "{os.path.join(mc_mods_directory)}"')

    def import_mod():
        title, subtitle = dialogs["mod"]
        mod = filedialog.askopenfilename(title=title, filetypes=[(subtitle, "*.jar")])
        if mod:
            shutil.move(mod, mc_mods_directory)
            return os.path.basename(mod)

    win = tk.Toplevel(parent)
    win.title(dialogs["store"])
    win.resizable(False, False)
    win.lift()
    win.focus()
    win.transient(parent)
    win.focus_force()
    win.grab_set()
    toolwindow(win)

    if os.path.exists(icon_path):
        win.iconbitmap(icon_path)

    style = ttk.Style()
    style.theme_use("default")

    style.configure("TFrame", background="SystemButtonFace")
    style.configure("Out.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.RAISED)
    style.configure("In.TFrame", background="SystemButtonFace", borderwidth=1, relief=tk.SUNKEN)

    style.configure("TEntry", focuswidth=2, focuscolor="#0040bf", selectbackground="#0040bf")

    style.map("TButton", background="SystemButtonFace")
    style.map("TButton", background=[("pressed", "#ffff00"), ("active", "SystemButtonFace"), ("!active", "SystemButtonFace")])
    style.configure("ToolbarButton.TButton", background="SystemButtonFace", relief=tk.FLAT, width=5, padding=(0, 5), font=("Segoe Fluent Icons", 10))
    style.map("ToolbarButton.TButton", background=[("pressed", "#ffff00"), ("active", "SystemButtonFace")], foreground=[("disabled", "#404040")])
    style.configure("MarkedToolbarButton.TButton", background="SystemButtonFace", foreground="#0040bf", relief=tk.FLAT, width=5, padding=(0, 5), font=("Segoe Fluent Icons", 10))
    style.map("MarkedToolbarButton.TButton", background=[("pressed", "#0040bf"), ("active", "SystemButtonFace")], foreground=[("pressed", "#ffffff"), ("active", "#0040bf"), ("disabled", "#bfbf00")])
    style.configure("DangerToolbarButton.TButton", background="SystemButtonFace", foreground="#bf0000", relief=tk.FLAT, width=5, padding=(0, 5), font=("Segoe Fluent Icons", 10))
    style.map("DangerToolbarButton.TButton", background=[("pressed", "#bf0000"), ("active", "SystemButtonFace")], foreground=[("pressed", "#ffffff"), ("active", "#bf0000"), ("disabled", ("#804040"))])

    search_toolbar = ttk.Frame(win, style="Out.TFrame", padding=5)
    search_toolbar.pack(padx=20, pady=(20, 0))

    container = ttk.Frame(win, width=800, height=500, style="Out.TFrame", padding=(10, 10, 10, 0))
    container.pack(padx=20, pady=(20, 0))
    container.pack_propagate(False)

    toolbar_frame = ttk.Frame(win)
    toolbar_frame.pack()

    navigation_toolbar = ttk.Frame(toolbar_frame, style="Out.TFrame", padding=5)
    navigation_toolbar.grid(row=0, column=0, padx=20, pady=20)

    other_toolbar = ttk.Frame(toolbar_frame, style="Out.TFrame", padding=5)
    other_toolbar.grid(row=0, column=1, padx=(0, 20), pady=20)


    def fetch_mods():
        nonlocal total_hits

        cache_key = (page, version, loader, search_var.get().strip().lower())

        if cache_key in page_cache:
            total_hits = page_cache[cache_key]["total_hits"]
            return page_cache[cache_key]["mods"]

        params = {
            "limit": limit,
            "offset": page * limit,
            "facets": f'[["project_type:mod"],["versions:{version}"],["categories:{loader}"]]'
        }

        query = search_var.get().strip()
        if query:
            params["query"] = query

        r = requests.get(API_SEARCH, params=params)
        data = r.json()

        total_hits = data.get("total_hits", 0)

        page_cache[cache_key] = {
            "mods": data.get("hits", []),
            "total_hits": total_hits
        }

        return data.get("hits", [])

    def fetch_download(slug):
        r = requests.get(API_VERSION.format(slug))
        versions = r.json()

        for version_info in versions:
            if loader not in version_info.get("loaders", []):
                continue

            if version not in version_info.get("game_versions", []):
                continue

            file_info = version_info["files"][0]

            return {
                "version": version_info["version_number"],
                "version_id": version_info["id"],
                "url": file_info["url"],
                "filename": file_info["filename"],
                "sha1": file_info["hashes"]["sha1"]
            }

        return None

    def clear():
        for w in container.winfo_children():
            w.destroy()

    def truncate(text, n=150):
        if not text:
            return labels[10]

        return text if len(text) <= n else text[:n] + "..."

    def download_thread(slug, label):
        try:
            download = fetch_download(slug)

            if download is None:
                parent.after(0, lambda: label.config(text=labels[5]))
                return

            url = download["url"]
            filename = download["filename"]

            if not url:
                parent.after(0, lambda: label.config(text=labels[5]))
                return

            os.makedirs(mc_mods_directory, exist_ok=True)

            path = os.path.join(mc_mods_directory, filename)

            r = requests.get(url, timeout=30)

            with open(path, "wb") as f:
                f.write(r.content)

            file_cache[slug] = filename

            parent.after(0, lambda: label.config(text=labels[6]))

        except Exception:
            parent.after(0, lambda: label.config(text=labels[7]))

    def get_file_sha1(path):
        h = hashlib.sha1()

        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)

        return h.hexdigest()

    def get_mod_file(slug):
        if not os.path.exists(mc_mods_directory):
            return None

        for file in os.listdir(mc_mods_directory):
            if not file.endswith(".jar"):
                continue

            path = os.path.join(mc_mods_directory, file)

            try:
                with zipfile.ZipFile(path) as jar:

                    if "fabric.mod.json" in jar.namelist():
                        data = json.loads(jar.read("fabric.mod.json"))

                        if data.get("id") == slug:
                            return {
                                "path": path,
                                "version": data.get("version", ""),
                                "file": file,
                                "sha1": get_file_sha1(path)
                            }

            except Exception:
                pass

        return None

    def create_mod_frame(mod):
        frame = ttk.Frame(
            container,
            padding=10,
            style="Out.TFrame"
        )

        frame.pack(fill="x", pady=(0, 10))

        left = ttk.Frame(frame)
        left.pack(side="left", fill="both", expand=True)

        title = ttk.Label(
            left,
            text=mod["title"],
            font=("Segoe UI", 9, "bold")
        )

        title.pack(anchor="w")

        desc = ttk.Label(
            left,
            text=truncate(mod.get("description", "")),
            wraplength=600,
            justify="left"
        )

        desc.pack(anchor="w", padx=(0, 10))

        status_label = ttk.Label(
            frame,
            text="",
            width=15
        )

        def refresh_buttons():
            for widget in button_frame.winfo_children():
                widget.destroy()

            installed = get_mod_file(mod["slug"])
            download = fetch_download(mod["slug"])

            update_available = (
                    installed is not None and
                    download is not None and
                    installed["sha1"] != download["sha1"]
            )

            if installed is None:
                download_button = ttk.Button(
                    button_frame,
                    text="\uE118",
                    style="MarkedToolbarButton.TButton",
                    command=start_download_btn
                )

                download_button.pack(side="right")

            elif update_available:
                update_button = ttk.Button(
                    button_frame,
                    text="\uE777",
                    style="ToolbarButton.TButton",
                    command=update_mod
                )

                update_button.pack(side="right")

            else:
                remove_button = ttk.Button(
                    button_frame,
                    text="\uE107",
                    style="DangerToolbarButton.TButton",
                    command=remove_mod
                )

                remove_button.pack(side="right")

            status_label.config(text="")

        def update_mod():
            installed = get_mod_file(mod["slug"])
            download = fetch_download(mod["slug"])

            if installed is None or download is None:
                return

            try:
                os.remove(installed["path"])
            except OSError:
                pass

            status_label.pack(side="right", padx=10)
            status_label.config(text=labels[5])

            threading.Thread(
                target=download_thread,
                args=(mod["slug"], status_label),
                daemon=True
            ).start()

            check_download()

        def start_download_btn():
            status_label.pack(side="right", padx=10)
            status_label.config(text=labels[5])

            threading.Thread(
                target=download_thread,
                args=(mod["slug"], status_label),
                daemon=True
            ).start()

            check_download()

        def check_download():
            if mod["slug"] in file_cache:
                mod_path = os.path.join(
                    mc_mods_directory,
                    file_cache[mod["slug"]]
                )

                if os.path.exists(mod_path):
                    refresh_buttons()
                    return

            frame.after(500, check_download)

        def remove_mod():
            try:
                installed = get_mod_file(mod["slug"])

                if installed is None:
                    return

                os.remove(installed["path"])

                status_label.pack(side="right", padx=10)
                status_label.config(text=labels[8])

                refresh_buttons()

            except Exception:
                status_label.pack(side="right", padx=10)
                status_label.config(text=labels[9])

        button_frame = ttk.Frame(frame)
        button_frame.pack(side="right")

        refresh_buttons()

    def load_page():
        clear()

        loading_label = ttk.Label(container, text=labels[11])
        loading_label.pack(pady=20)

        previous_button.config(state="disabled")
        next_button.config(state="disabled")

        def worker():
            try:
                mods = fetch_mods()

                def update_ui():
                    clear()

                    for mod in mods:
                        create_mod_frame(mod)

                    total_pages = max(
                        1,
                        (total_hits + limit - 1) // limit
                    )

                    page_label.config(
                        text=f"{page + 1} / {total_pages}"
                    )

                    previous_button.config(
                        state="normal" if page > 0 else "disabled"
                    )

                    next_button.config(
                        state=(
                            "normal"
                            if (page + 1) * limit < total_hits
                            else "disabled"
                        )
                    )

                win.after(0, update_ui)

            except Exception:
                def show_error():
                    clear()

                    ttk.Label(
                        container,
                        text=labels[12]
                    ).pack(pady=20)

                win.after(0, show_error)

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def refresh():
        page_cache.clear()
        load_page()

    def search():
        nonlocal page

        page = 0
        page_cache.clear()
        load_page()

    def on_search_changed(*args):
        nonlocal search_after_id

        if search_after_id is not None:
            win.after_cancel(search_after_id)

        search_after_id = win.after(300, search)

    def next_page():
        nonlocal page

        page += 1
        load_page()

    def prev_page():
        nonlocal page

        if page > 0:
            page -= 1
            load_page()

    search_var.trace_add("write", on_search_changed)

    search_entry = ttk.Entry(search_toolbar, textvariable=search_var, width=50)
    search_entry.pack(ipady=3)

    previous_button = ttk.Button(navigation_toolbar, text="\uE00E", command=prev_page, style="ToolbarButton.TButton")
    previous_button.grid(row=0, column=0)

    page_label = ttk.Label(navigation_toolbar, text="")
    page_label.grid(row=0, column=1, padx=10)

    next_button = ttk.Button(navigation_toolbar, text="\uE00F", command=next_page, style="ToolbarButton.TButton")
    next_button.grid(row=0, column=2)

    refresh_button = ttk.Button(other_toolbar, text="\uE149", style="ToolbarButton.TButton", command=refresh)
    refresh_button.grid(row=0, column=0)

    import_button = ttk.Button(other_toolbar, text="\uE109", style="ToolbarButton.TButton", command=import_mod)
    import_button.grid(row=0, column=1)

    open_dir_button = ttk.Button(other_toolbar, text="\uE19C", style="ToolbarButton.TButton", command=open_dir)
    open_dir_button.grid(row=0, column=2)

    if tooltips:
        ToolTip(open_dir_button, tooltip_labels[6])
        ToolTip(import_button, tooltip_labels[7])
        ToolTip(previous_button, tooltip_labels[4])
        ToolTip(next_button, tooltip_labels[5])
        ToolTip(refresh_button, tooltip_labels[9])

    load_page()