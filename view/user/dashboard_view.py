import ttkbootstrap as ttk
from view.sidebar import Sidebar


class DashboardPage(ttk.Frame):
    def __init__(self, parent, show):
        super().__init__(parent)

        sidebar = Sidebar(self)
        sidebar.pack(side="left", fill="y")
        sidebar.add_item("Dashboard", lambda: None)
        sidebar.add_item("Logout", lambda: show("login"))

        content = ttk.Frame(self, padding=20)
        content.pack(side="right", fill="both", expand=True)

        ttk.Label(content, text="Dashboard", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(content, text="Welcome!").pack(anchor="w", pady=10)