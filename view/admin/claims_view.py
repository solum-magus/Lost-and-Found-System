# review claims and make decisions to approve/reject
from tkinter import ttk

class ClaimsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

        ttk.Label(self, text="Claims", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(self, text="This is the claims page.").pack(anchor="w", pady=10)