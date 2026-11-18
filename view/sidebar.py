import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class Sidebar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10, bootstyle=SECONDARY)
        ttk.Label(self, text="MENU", font=("Segoe UI", 12, "bold"),
                  bootstyle="inverse-secondary").pack(pady=(0, 15))
        self.buttons = {}

    def add_item(self, name, command):
        btn = ttk.Button(self, text=name, width=15,
                         bootstyle="secondary", command=command)
        btn.pack(fill=X, pady=3)
        self.buttons[name] = btn

    def set_active(self, name):
        for n, btn in self.buttons.items():
            btn.configure(bootstyle="primary" if n == name else "secondary")