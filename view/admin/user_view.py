# view user info and their claims/reports, authenticate/ban accounts (ts optional)
import ttkbootstrap as ttk


class UserPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

        ttk.Label(self, text="Users", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(self, text="This is the user management page.").pack(anchor="w", pady=10)