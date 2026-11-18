import ttkbootstrap as ttk

class Sidebar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10, bootstyle="secondary")

        ttk.Label(self, text="Menu", font=("Segoe UI", 12, "bold"),
                  bootstyle="inverse-secondary").pack(pady=(0, 15))

    def add_item(self, text, command):
        ttk.Button(self, text=text, width=15, bootstyle="secondary",
                   command=command).pack(fill="x", pady=3)