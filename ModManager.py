import os, sys, requests, threading
import tkinter as tk
from tkinter import ttk
from Functions import set_theme, is_connected
from ErrorHandler import error_handler
from Tooltips import Tooltip
from PIL import Image, ImageTk
from io import BytesIO

sys.excepthook = error_handler

def fetch_mods(version, loader, query="", limit=30, offset=0):
    if is_connected():
        api_url = "https://api.modrinth.com/v2/search"

        facets = f'[["project_type:mod"],["versions:{version}"],["categories:{loader.lower()}"]]'

        params = {
            "limit": limit,
            "offset": offset,
            "facets": facets
        }

        if query:
            params["query"] = query

        try:
            response = requests.get(api_url, params=params, timeout=1)
            if response.status_code == 200:
                data = response.json()
                return data.get("hits", []), data.get("total_hits", 0)
        except Exception:
            return None
    else:
        return None

    return None

def shorten_number(number):
    length = len(str(number))

    if 4 <= length < 7:
        return f"{number // 1000} K"
    elif length >= 7:
        return f"{number // 1000000} M"

    return None

def mod_manager(parent, version="", loader="vanilla", language_data=None, tooltips=True, theme="light", minecraft_directory=""):
    current_page = 0
    mods = None
    search = ""
    current_mod_files = []
    search_timer = None

    window = tk.Toplevel(parent)
    window.title(language_data.get("ModManager.Title"))
    window.resizable(False, False)
    window.transient(parent)
    window.focus_force()

    style = ttk.Style()
    style.theme_use("default")

    set_theme(theme=theme, window=window, style=style)

    ttk.Label(window, text=language_data.get("ModManager.Title"), font=("Segoe UI", 12, "bold")).pack(padx=20, pady=(20, 0))

    main_frame = ttk.Frame(window, style="Out.TFrame", padding=10)
    main_frame.pack(padx=20, pady=20)

    action_frame = ttk.Frame(main_frame, style="Out.TFrame", padding=10)
    action_frame.pack(side="top", fill="x", pady=(0, 10))

    action_toolbar = ttk.Frame(action_frame)
    action_toolbar.grid(row=0, column=0, padx=(0, 10))

    navigation_toolbar = ttk.Frame(action_frame)
    navigation_toolbar.grid(row=0, column=1, padx=(0, 10))

    search_entry = ttk.Entry(action_frame, width=90)
    search_entry.grid(row=0, column=2, sticky="ew")

    mods_frame = ttk.Frame(main_frame, style="Out.TFrame", padding=10)
    mods_frame.pack(side="left", padx=(0, 10))

    details_frame = ttk.Frame(main_frame, style="Out.TFrame", padding=10, width=400)
    details_frame.pack(side="right", fill="y")
    details_frame.grid_propagate(False)

    mod_icon = ttk.Label(details_frame, borderwidth=1, relief="raised")
    mod_icon.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nw")

    mod_title = ttk.Label(details_frame, font=("Segoe UI", 12, "bold"), wraplength=200, anchor="w")
    mod_title.grid(row=0, column=1, pady=(0, 10), sticky="nw")

    mod_description = ttk.Label(details_frame, wraplength=275, anchor="w")
    mod_description.grid(row=1, column=1, sticky="nw")

    mod_toolbar = ttk.Frame(details_frame)
    mod_toolbar.grid(row=1, column=0, sticky="nw")

    status_label = ttk.Label(mods_frame, anchor="w")
    status_label.pack(side="top", fill="x", pady=(0, 10))

    mods_tree = ttk.Treeview(mods_frame, columns=("mod", "author", "downloads", "follows"), show="headings", height="15")
    mods_tree.pack(side="left")
    mods_tree.heading("mod", text=language_data.get("ModManager.ModsTree.Mod"))
    mods_tree.heading("author", text=language_data.get("ModManager.ModsTree.Author"))
    mods_tree.heading("downloads", text=language_data.get("ModManager.ModsTree.Downloads"))
    mods_tree.heading("follows", text=language_data.get("ModManager.ModsTree.Follows"))
    mods_tree.column("mod", width=200, minwidth=200)
    mods_tree.column("author", width=100, minwidth=100)
    mods_tree.column("downloads", width=100, minwidth=100)
    mods_tree.column("follows", width=75, minwidth=75)

    scrollbar = ttk.Scrollbar(mods_frame, orient="vertical", command=mods_tree.yview)
    scrollbar.pack(side="right", fill="both")

    mods_tree.configure(yscrollcommand=scrollbar.set)

    def check_mod_updates(slug, current_version_id):
        versions_url = f"https://api.modrinth.com/v2/project/{slug}/version"
        try:
            response = requests.get(versions_url, timeout=10)
            if response.status_code == 200:
                versions_data = response.json()
                for v_info in versions_data:
                    if v_info["id"] == current_version_id:
                        break

                    if loader.lower() in v_info.get("loaders", []) and version in v_info.get("game_versions", []):
                        return True, v_info
        except:
            return False, None

        return False, None

    def is_mod_installed(slug):
        current_mod_files.clear()

        mods_directory = os.path.join(minecraft_directory, "mods")
        if not os.path.exists(mods_directory):
            return False

        versions_url = f"https://api.modrinth.com/v2/project/{slug}/version"
        try:
            response = requests.get(versions_url, timeout=5)
            if response.status_code == 200:
                versions_data = response.json()
                for v_info in versions_data:
                    files = v_info.get("files", [])
                    for file_info in files:
                        file_name = file_info.get("filename")
                        file_path = os.path.join(mods_directory, file_name)
                        current_mod_files.append(file_path)
                        if os.path.exists(file_path):
                            return True, v_info["id"]
        except Exception:
            pass

        return False, None

    def download_mod(slug):

        mods_directory = os.path.join(minecraft_directory, "mods")

        if is_connected():
            download_button.config(state="disabled")
            status_label.config(text=language_data.get("ModManager.Downloading"))

            versions_url = f"https://api.modrinth.com/v2/project/{slug}/version"

            try:
                response = requests.get(versions_url, timeout=10)
                if response.status_code != 200:
                    status_label.config(text=language_data.get("ModManager.DownloadError"))
                    return

                versions_data = response.json()

                target_file = None
                for v_info in versions_data:
                    if loader.lower() not in v_info.get("loaders", []):
                        continue
                    if version not in v_info.get("game_versions", []):
                        continue

                    files = v_info.get("files", [])

                    if files:
                        target_file = files[0]
                        break

                if not target_file:
                    status_label.config(text=language_data.get("ModManager.DownloadError"))
                    return

                file_url = target_file["url"]
                file_name = target_file["filename"]

                os.makedirs(mods_directory, exist_ok=True)
                file_path = os.path.join(mods_directory, file_name)

                file_res = requests.get(file_url, timeout=30)
                if file_res.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(file_res.content)

            except:
                status_label.config(text=language_data.get("ModManager.DownloadError"))
                return
        else:
            status_label.config(text=language_data.get("ModManager.DownloadError"))
            return

        status_label.config(text=f"{current_page + 1} / {mods[1]}")
        update_button.config(state="disabled")
        update_details()

    def delete_mod():
        mods_directory = os.path.join(minecraft_directory, "mods")
        file_path = ""

        status_label.config(text=language_data.get("ModManager.Delete"))

        for f in current_mod_files:
            if os.path.exists(os.path.join(mods_directory, f)):
                file_path = os.path.join(mods_directory, f)
                break

        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                status_label.config(text=f"{current_page + 1} / {mods[1]}")
        except:
            status_label.config(text=language_data.get("ModManager.DeleteError"))
            return

        status_label.config(text=f"{current_page + 1} / {mods[1]}")
        update_details()

    def refresh(page):
        nonlocal mods, current_page

        current_page = page

        status_label.config(text=language_data.get("ModManager.Loading"))
        mods_tree.selection_remove(mods_tree.selection())
        mods_tree.delete(*mods_tree.get_children())
        mod_icon.grid_forget()
        mod_title.grid_forget()
        mod_description.grid_forget()
        mod_toolbar.grid_forget()

        if search.strip() != "":
            mods = fetch_mods(version=version, loader=loader, offset=page * 30, query=search)
        else:
            mods = fetch_mods(version=version, loader=loader, offset=page * 30)

        if mods is not None:
            for mod in mods[0]:
                mods_tree.insert("", tk.END, values=(mod.get("title"), mod.get("author"), shorten_number(mod.get("downloads")), shorten_number(mod.get("follows"))))

            total_pages = max(1, (mods[1] + 29) // 30)
            status_label.config(text=f"{current_page + 1} / {total_pages}")
        else:
            status_label.config(text=language_data.get("ModManager.LoadError"))

        if mods is not None:
            if current_page == 0:
                previous_button.config(state="disabled")
            else:
                previous_button.config(state="normal")

            if current_page == (mods[1] - 1):
                next_button.config(state="disabled")
            else:
                next_button.config(state="normal")

    def update_details(event=None):
        if mods is None or not mods[0]:
            return

        mod_icon.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nw")
        mod_title.grid(row=0, column=1, pady=(0, 10), sticky="nw")
        mod_description.grid(row=1, column=1, sticky="nw")
        mod_toolbar.grid(row=1, column=0, sticky="nw")

        selected_mod = mods_tree.selection()

        if selected_mod:
            selected_index = mods_tree.index(selected_mod[0])
        else:
            selected_index = 0

        if selected_index >= len(mods[0]):
            return

        def update_icon(image):
            mod_icon.config(image=image)
            mod_icon.image = image

        def download_icon():
            try:
                res = requests.get(mods[0][selected_index].get("icon_url"), timeout=10)
                image_data = BytesIO(res.content)
                image = ImageTk.PhotoImage(image=Image.open(image_data).resize((100, 100)))
                update_icon(image)
            except:
                return

        threading.Thread(target=download_icon).start()
        print(len(mods))
        if mods is not None:
            mod_title.config(text=mods[0][selected_index].get("title"))
            mod_description.config(text=mods[0][selected_index].get("description"))
        else:
            mod_title.grid_forget()
            mod_description.grid_forget()

        installed = is_mod_installed(mods[0][selected_index].get("slug"))
        has_update, latest_version = check_mod_updates(mods[0][selected_index].get("slug"), installed[1])


        if installed[0]:
            download_button.config(state="disabled")
            delete_button.config(state="normal")
            if has_update:
                update_button.config(state="normal")
            else:
                update_button.config(state="disabled")
        else:
            download_button.config(state="normal")
            delete_button.config(state="disabled")
            update_button.config(state="disabled")

    def previous():
        if current_page > 0:
            threading.Thread(target=lambda: refresh(current_page - 1), daemon=True).start()

    def next():
        if mods:
            total_pages = max(1, (mods[1] + 29) // 30)
            if current_page < total_pages - 1:
                threading.Thread(target=lambda: refresh(current_page + 1), daemon=True).start()

    def search_mods(event=None):
        nonlocal search, search_timer
        new_search = search_entry.get()

        if new_search != search:
            search = new_search

            if search_timer is not None:
                window.after_cancel(search_timer)

            search_timer = window.after(300, lambda: threading.Thread(target=lambda: refresh(0), daemon=True).start())

    def download():
        selected_mod = mods_tree.selection()

        if selected_mod:
            selected_index = mods_tree.index(selected_mod[0])
        else:
            selected_index = 0

        threading.Thread(target=lambda: download_mod(mods[0][selected_index].get("slug")), daemon=True).start()

    def update():
        selected_mod = mods_tree.selection()

        if selected_mod:
            selected_index = mods_tree.index(selected_mod[0])
        else:
            selected_index = 0

        delete_mod()
        threading.Thread(target=lambda: download_mod(mods[0][selected_index].get("slug")), daemon=True).start()

    open_dir_button = ttk.Button(action_toolbar, text="\ue197", command=lambda: os.startfile(os.path.join(minecraft_directory, "mods")), style="ToolbarButton.TButton")
    open_dir_button.grid(row=0, column=0)
    Tooltip(open_dir_button, text=language_data.get("Tooltip.ModManager.OpenDirectory"), shown=tooltips)

    refresh_button = ttk.Button(action_toolbar, text="\ue117", style="ToolbarButton.TButton", command=lambda: threading.Thread(target=lambda: refresh(current_page), daemon=True).start())
    refresh_button.grid(row=0, column=1)
    Tooltip(refresh_button, text=language_data.get("Tooltip.ModManager.Refresh"), shown=tooltips)

    previous_button = ttk.Button(navigation_toolbar, text="\ue00e", command=previous, style="ToolbarButton.TButton")
    previous_button.grid(row=0, column=0)
    Tooltip(previous_button, text=language_data.get("Tooltip.ModManager.Previous"), shown=tooltips)

    next_button = ttk.Button(navigation_toolbar, text="\ue00f", command=next, style="ToolbarButton.TButton")
    next_button.grid(row=0, column=1)
    Tooltip(next_button, text=language_data.get("Tooltip.ModManager.Next"), shown=tooltips)

    download_button = ttk.Button(mod_toolbar, text="\ue896", command=download, style="MarkedToolbarButton.TButton")
    download_button.grid(row=0, column=0)
    Tooltip(download_button, text=language_data.get("Tooltip.ModManager.Download"), shown=tooltips)

    update_button = ttk.Button(mod_toolbar, text="\ue149", command=download, style="ToolbarButton.TButton")
    update_button.grid(row=0, column=1)
    Tooltip(update_button, text=language_data.get("Tooltip.ModManager.Update"), shown=tooltips)

    delete_button = ttk.Button(mod_toolbar, text="\ue107", command=delete_mod, style="DangerousToolbarButton.TButton")
    delete_button.grid(row=0, column=2)
    Tooltip(delete_button, text=language_data.get("Tooltip.ModManager.Delete"), shown=tooltips)

    mods_tree.bind("<<TreeviewSelect>>", lambda e: threading.Thread(target=update_details, daemon=True).start())
    search_entry.bind("<KeyRelease>", search_mods)

    refresh(0)