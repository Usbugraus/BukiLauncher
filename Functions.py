import minecraft_launcher_lib
import psutil, subprocess, os, json
from Constants import theme_configuration_file

with open(theme_configuration_file, "r") as f:
    theme_configuration = json.load(f)

def is_connected():
    try:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()

        for interface_name, stat in stats.items():
            if interface_name != 'lo' and stat.isup:
                if interface_name in addrs:
                    for addr in addrs[interface_name]:
                        if addr.family.name in ('AF_INET', 'AF_INET6'):
                            if not addr.address.startswith('127.'):
                                return True
        return False
    except Exception:
        return False

def get_minecraft_versions(mod_loader="vanilla", snapshots=False, version="", minecraft_directory=""):
    minecraft_versions = []
    mod_loader_versions = []

    if is_connected():
        if mod_loader == "vanilla":
            for v in minecraft_launcher_lib.utils.get_version_list():
                if v["type"] == "release":
                    minecraft_versions.append(v["id"])
                elif snapshots and v["type"] in ("snapshot", "old_beta", "old_alpha"):
                    minecraft_versions.append(v["id"])

        else:
            loader = minecraft_launcher_lib.mod_loader.get_mod_loader(mod_loader)

            minecraft_versions = loader.get_minecraft_versions(stable_only=not snapshots)

            if version:
                try:
                    mod_loader_versions = loader.get_loader_versions(version, stable_only=False)
                except Exception:
                    mod_loader_versions = []

    else:
        minecraft_versions = [v["id"] for v in minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory)]

    return minecraft_versions, mod_loader_versions

def is_version_installed(version="", mod_loader="vanilla", loader_version="", minecraft_directory=""):
    target_id = ""

    if mod_loader == "vanilla":
        target_id = version
    else:
        if mod_loader == "fabric":
            target_id = f"fabric-loader-{loader_version}-{version}"
        elif mod_loader == "quilt":
            target_id = f"quilt-loader-{loader_version}-{version}"
        elif mod_loader == "forge":
            target_id = f"{version}-forge-{loader_version}"
        elif mod_loader == "neoforge":
            target_id = f"neoforge-{loader_version}"

    if not target_id in [v["id"] for v in minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory)]:
        return False

    return True

def launch_minecraft(window, username="", version="", mod_loader="vanilla", loader_version="", jvm_arguments=[], java_path="", hide_window=True, minecraft_directory=""):

    target_id = ""
    if mod_loader == "vanilla":
        target_id = version
    else:
        if mod_loader == "fabric":
            target_id = f"fabric-loader-{loader_version}-{version}"
        elif mod_loader == "quilt":
            target_id = f"quilt-loader-{loader_version}-{version}"
        elif mod_loader == "forge":
            target_id = f"{version}-forge-{loader_version}"
        elif mod_loader == "neoforge":
            target_id = f"neoforge-{loader_version}"

    options = {
        "username": username,
        "jvmArguments": jvm_arguments,
        "launcherName": "BukiLauncher",
        "launcherVersion": "2026.5.0",
        "executablePath": java_path
    }

    command = minecraft_launcher_lib.command.get_minecraft_command(target_id, minecraft_directory, options)
    button = window.nametowidget("toolbar").nametowidget("launch_button")

    if hide_window:
        window.withdraw()

    button.config(state="disabled")
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,)
    stdout, stderr = process.communicate()
    button.config(state="normal")

    window.deiconify()

    return stdout, stderr, process.returncode

def update_widgets(widgets=None, tooltips=None, tooltip_shown=True, menus=None, language_data=None, java_selected=False, theme="light"):
    widgets[0].config(text=language_data.get("Options.Username"))
    widgets[1].config(text=language_data.get("Options.MinecraftVersion"))
    widgets[2].config(text=language_data.get("Options.Loader"))
    widgets[3].config(text=language_data.get("Options.LoaderVersion"))

    menus.get("settings").entryconfig(0, label=language_data.get("Settings.Snapshots"))
    menus.get("settings").entryconfig(1, label=language_data.get("Settings.HideWindow"))
    menus.get("settings").entryconfig(2, label=language_data.get("Settings.Tooltips"))

    if theme == "light":
        menus.get("settings").entryconfig(3, label=language_data.get("Settings.JavaSelected") if java_selected else language_data.get("Settings.JavaNotSelected"))
    if theme == "dark":
        menus.get("settings").entryconfig(3, label=language_data.get("Settings.JavaSelected") if java_selected else language_data.get("Settings.JavaNotSelected"))

    menus.get("settings").entryconfig(4, label=language_data.get("Settings.SelectMCDir"))
    menus.get("settings").entryconfig(5, label=language_data.get("Settings.JVMArgs"))
    menus.get("settings").entryconfig(6, label=language_data.get("Settings.UUID"))
    menus.get("settings").entryconfig(7, label=language_data.get("Settings.Theme"))
    menus.get("settings").entryconfig(8, label=language_data.get("Settings.Language"))
    menus.get("settings").entryconfig(10, label=language_data.get("Settings.About"))

    values = list(theme_configuration.values())
    for thm in theme_configuration:
        thmconf = theme_configuration.get(thm)
        menus.get("themes").entryconfig(values.index(thmconf), label=language_data.get(thmconf.get("label")))

    tooltips[0].configure(text=language_data.get("Tooltip.Launch"), shown=tooltip_shown)
    tooltips[1].configure(text=language_data.get("Tooltip.OpenDirectory"), shown=tooltip_shown)
    tooltips[3].configure(text=language_data.get("Tooltip.ModManager"), shown=tooltip_shown)
    tooltips[2].configure(text=language_data.get("Tooltip.Settings"), shown=tooltip_shown),

def open_minecraft_directory(minecraft_directory=""):
    if not os.path.exists(minecraft_directory):
        os.mkdir(minecraft_directory)

    os.startfile(minecraft_directory)

def set_theme(theme="light", window=None, style=None, textfield=None, menus=None, java_selected=False):
    theme_file = theme_configuration.get(theme).get("file")

    with open(os.path.join("Resources", "Themes", theme_file), "r") as f:
        theme_data = json.load(f)

    window_data = theme_data.get("window")
    frame_data = theme_data.get("frame")
    labelframe_data = theme_data.get("labelframe")
    label_data = theme_data.get("label")
    button_data = theme_data.get("button")
    toolbarbutton_data = theme_data.get("toolbarbutton")
    entry_data = theme_data.get("entry")
    combobox_data = theme_data.get("combobox")
    tooltip_data = theme_data.get("tooltip")
    progressbar_data = theme_data.get("progressbar")
    textfield_data = theme_data.get("textfield")
    menu_data = theme_data.get("menu")
    scrollbar_data = theme_data.get("scrollbar")
    tree_data = theme_data.get("tree")

    style.theme_use("default")

    window.configure(
        bg=window_data.get("background")
    )
    style.configure(
        "TFrame",
        background=frame_data.get("flat").get("background"),
        borderwidth = frame_data.get("flat").get("borderwidth"),
        relief = frame_data.get("flat").get("relief")
    )
    style.configure(
        "Out.TFrame",
        background=frame_data.get("outset").get("background"),
        borderwidth=frame_data.get("outset").get("borderwidth"),
        relief=frame_data.get("outset").get("relief")
    )
    style.configure(
        "In.TFrame",
        background=frame_data.get("inset").get("background"),
        borderwidth=frame_data.get("inset").get("borderwidth"),
        relief=frame_data.get("inset").get("relief")
    )

    style.configure(
        "TLabelframe",
        background=labelframe_data.get("flat").get("background"),
        borderwidth=labelframe_data.get("flat").get("borderwidth"),
        relief=labelframe_data.get("flat").get("relief")
    )
    style.configure(
        "Out.TLabelframe",
        background=labelframe_data.get("outset").get("background"),
        borderwidth=labelframe_data.get("outset").get("borderwidth"),
        relief=labelframe_data.get("outset").get("relief")
    )
    style.configure(
        "In.TLabelframe",
        background=labelframe_data.get("inset").get("background"),
        borderwidth=labelframe_data.get("inset").get("borderwidth"),
        relief=labelframe_data.get("inset").get("relief")
    )

    style.configure(
        "TLabelframe.Label",
        background=labelframe_data.get("label").get("background"),
        foreground=labelframe_data.get("label").get("foreground"),
    )

    style.configure(
        "TEntry",
        focuswidth=entry_data.get("focuswidth"),
        focuscolor=entry_data.get("focuscolor"),
        selectbackground=entry_data.get("selectionbackground"),
        selectforeground=entry_data.get("selectionforeground"),
        foreground=entry_data.get("foreground"),
        fieldbackground=entry_data.get("background"),
        relief=entry_data.get("relief"),
        borderwidth=entry_data.get("borderwidth")
    )
    style.map(
        "TEntry",
        fieldbackground=[
            ("readonly", entry_data.get("disabledbackground")),
            ("disabled", entry_data.get("disabledbackground"))
        ],
        foreground = [
            ("readonly", entry_data.get("foreground")),
            ("disabled", entry_data.get("disabledforeground"))
        ]
    )

    style.configure(
        "TCombobox",
        focuswidth=combobox_data.get("focuswidth"),
        focuscolor=combobox_data.get("focuscolor"),
        selectbackground=combobox_data.get("selectionbackground"),
        selectforeground=combobox_data.get("selectionforeground"),
        foreground=combobox_data.get("foreground"),
        fieldbackground=combobox_data.get("background"),
        relief=combobox_data.get("relief"),
        borderwidth=combobox_data.get("borderwidth"),
        arrowcolor=combobox_data.get("arrowcolor"),
        arrowsize=combobox_data.get("arrowsize")
    )
    style.map(
        "TCombobox",
        fieldbackground=[
            ("readonly", combobox_data.get("background")),
            ("disabled", combobox_data.get("disabledbackground"))
        ],
        foreground=[
            ("readonly", combobox_data.get("foreground")),
            ("disabled", combobox_data.get("disabledforeground"))
        ],
        background=[
            ("active", combobox_data.get("arrowbackground")),
            ("!active", combobox_data.get("arrowbackground")),
        ]
    )

    style.configure(
        "TLabel",
        background=label_data.get("background"),
        foreground=label_data.get("foreground"),
        relief=label_data.get("relief"),
        borderwidth=label_data.get("borderwidth"),
    )

    style.configure(
        "TButton",
        background=button_data.get("background"),
        foreground=button_data.get("foreground"),
    )
    style.map(
        "TButton",
        background=[
          ("pressed", button_data.get("pressedbackground")),
          ("active", button_data.get("background")),
          ("!active", button_data.get("background"))
        ],
        foreground=[
            ("pressed", button_data.get("pressedforeground")),
            ("active", button_data.get("foreground")),
            ("!active", button_data.get("foreground"))
        ]
    )
    style.configure(
        "ToolbarButton.TButton",
        background=toolbarbutton_data.get("normal").get("background"),
        foreground=toolbarbutton_data.get("normal").get("foreground"),
        relief=toolbarbutton_data.get("normal").get("relief"),
        width=5,
        padding=(0, 5),
        font=("Segoe Fluent Icons", 9)
    )
    style.map(
        "ToolbarButton.TButton",
        background=[
            ("pressed", toolbarbutton_data.get("normal").get("pressedbackground")),
            ("active", toolbarbutton_data.get("normal").get("background"))
        ],
        foreground=[
            ("disabled", toolbarbutton_data.get("normal").get("disabledforeground")),
            ("pressed", toolbarbutton_data.get("normal").get("pressedforeground"))
        ]
    )
    style.configure(
        "MarkedToolbarButton.TButton",
        background=toolbarbutton_data.get("marked").get("background"),
        foreground=toolbarbutton_data.get("marked").get("foreground"),
        relief=toolbarbutton_data.get("marked").get("relief"),
        width=5,
        padding=(0, 5),
        font=("Segoe Fluent Icons", 9)
    )
    style.map(
        "MarkedToolbarButton.TButton",
        background=[
            ("pressed", toolbarbutton_data.get("marked").get("pressedbackground")),
            ("active", toolbarbutton_data.get("marked").get("background"))
        ],
        foreground=[
            ("pressed", toolbarbutton_data.get("marked").get("pressedforeground")),
            ("active", toolbarbutton_data.get("marked").get("foreground")),
            ("disabled", toolbarbutton_data.get("marked").get("disabledforeground"))
        ]
    )
    style.configure(
        "DangerousToolbarButton.TButton",
        background=toolbarbutton_data.get("dangerous").get("background"),
        foreground=toolbarbutton_data.get("dangerous").get("foreground"),
        relief=toolbarbutton_data.get("dangerous").get("relief"),
        width=5,
        padding=(0, 5),
        font=("Segoe Fluent Icons", 9)
    )
    style.map(
        "DangerousToolbarButton.TButton",
        background=[
            ("pressed", toolbarbutton_data.get("dangerous").get("pressedbackground")),
            ("active", toolbarbutton_data.get("dangerous").get("background"))
        ],
        foreground=[
            ("pressed", toolbarbutton_data.get("dangerous").get("pressedforeground")),
            ("active", toolbarbutton_data.get("dangerous").get("foreground")),
            ("disabled", toolbarbutton_data.get("dangerous").get("disabledforeground"))
        ]
    )

    style.configure(
        "TProgressbar",
        background=progressbar_data.get("background"),
        troughcolor=progressbar_data.get("progresscolor"),
        borderwidth=progressbar_data.get("borderwidth"),
    )

    style.configure(
        "ToolTip.TLabel",
        background=tooltip_data.get("background"),
        foreground=tooltip_data.get("foreground"),
        relief=tooltip_data.get("relief"),
        borderwidth=tooltip_data.get("borderwidth"),
        padding=(5, 2)
    )

    style.configure(
        "TScrollbar",
        background=scrollbar_data.get("background"),
        troughcolor=scrollbar_data.get("troughcolor"),
        arrowsize=scrollbar_data.get("arrowsize"),
        arrowcolor=scrollbar_data.get("arrowcolor"),
        borderwidth=scrollbar_data.get("borderwidth")
    )
    style.map(
        "TScrollbar",
        background=[
            ("active", scrollbar_data.get("background")),
            ("!active", scrollbar_data.get("background"))
        ],
        relief=[
            ("pressed", "sunken")
        ]
    )

    style.configure(
        "Treeview",
        background=tree_data.get("background"),
        foreground=tree_data.get("foreground"),
        borderwidth=tree_data.get("borderwidth"),
        focuscolor=tree_data.get("focuscolor"),
        focuswidth=tree_data.get("focuswidth"),
        fieldbackground=tree_data.get("background"),
    )
    style.map(
        "Treeview",
        background=[
            ("selected", tree_data.get("selectionbackground")),
        ],
        foreground = [
            ("selected", tree_data.get("selectionforeground")),
        ]
    )
    style.map(
        "Treeview.Heading",
        background=[
            ("active", tree_data.get("titlebackground")),
            ("!active", tree_data.get("titlebackground"))
        ],
        foreground=[
            ("active", tree_data.get("titleforeground")),
            ("!active", tree_data.get("titleforeground"))
        ]
    )

    if menus is not None:
        menus.get("settings").config(bg=menu_data.get("background"), fg=menu_data.get("foreground"))
        menus.get("settings").entryconfig(3, foreground=menu_data.get("javaselected") if java_selected else menu_data.get("javanotselected"))
        menus.get("themes").config(bg=menu_data.get("background"), fg=menu_data.get("foreground"))
        menus.get("languages").config(bg=menu_data.get("background"), fg=menu_data.get("foreground"))

        for menu in menus.keys():
            for index in range(menus.get(menu).index("end") + 1):
                if not menus.get(menu).type(index) == "separator":
                    menus.get(menu).entryconfig(index, activebackground=menu_data.get("selectionbackground"), activeforeground=menu_data.get("selectionforeground"))

    if textfield is not None:
        textfield.config(bg=textfield_data.get("background"), fg=textfield_data.get("foreground"), bd=textfield_data.get("borderwidth"), relief=textfield_data.get("relief"))