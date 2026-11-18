# display recent lost and found items
import ttkbootstrap as ttk


class AdminDashboardPage(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)

        ttk.Label(self, text="Dashboard", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(self, text="Welcome to your admin dashboard!").pack(anchor="w", pady=10)