# toggle light dark?, change font size, see/edit info, optional
import ttkbootstrap as ttk


class SettingsPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

        ttk.Label(self, text="Settings", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(self, text="This is the settings page.").pack(anchor="w", pady=10)