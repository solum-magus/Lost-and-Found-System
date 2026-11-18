# claim submission page (can be merged w reporting page or actually we can just create a new frame for all 3)
import ttkbootstrap as ttk


class ClaimPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

        ttk.Label(self, text="Claims", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(self, text="This is the claims page.").pack(anchor="w", pady=10)