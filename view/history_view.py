# dedicated page displaying all items
import ttkbootstrap as ttk


class HistoryPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

        ttk.Label(self, text="History", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(self, text="This is the history page.").pack(anchor="w", pady=10)