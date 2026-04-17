import ctypes

def toolwindow(window):
    try:
        window.update_idletasks()
        hwnd = window.winfo_id()

        GWL_STYLE = -16
        WS_MINIMIZEBOX = 0x00020000
        WS_MAXIMIZEBOX = 0x00010000

        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        style = style & ~WS_MINIMIZEBOX & ~WS_MAXIMIZEBOX

        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)

        ctypes.windll.user32.SetWindowPos(
            hwnd, 0, 0, 0, 0, 0,
            0x0002 | 0x0001 | 0x0004 | 0x0020 | 0x0010
        )
    except:
        pass
