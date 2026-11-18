# lost/found items reporting
import ttkbootstrap as ttk


class ItemPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

        ttk.Label(self, text="Items", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(self, text="This is the items page.").pack(anchor="w", pady=10)