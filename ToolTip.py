import tkinter as tk

class ToolTip:
    def __init__(self, widget, text, offset_x=10, offset_y=10, shown=True):
        self.widget = widget
        self.text = text
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.shown = shown
        self.label = tk.Label(widget.winfo_toplevel(), text=text, bg="#ffffbf", relief="raised", bd=1)
        self.label.place_forget()
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.shown:
            root = self.widget.winfo_toplevel()
            root_width = root.winfo_width()
            root_height = root.winfo_height()
            
            self.label.update_idletasks()
            tooltip_width = self.label.winfo_width()
            tooltip_height = self.label.winfo_height()
            
            x = event.x_root - root.winfo_rootx() + self.offset_x
            y = event.y_root - root.winfo_rooty() + self.offset_y
            
            if x + tooltip_width > root_width:
                x = event.x_root - root.winfo_rootx() - tooltip_width - self.offset_x
            if y + tooltip_height > root_height:
                y = event.y_root - root.winfo_rooty() - tooltip_height - self.offset_y
            
            self.label.place(x=x, y=y)

    def hide_tooltip(self, event=None):
        self.label.place_forget()
