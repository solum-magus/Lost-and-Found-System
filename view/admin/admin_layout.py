import ttkbootstrap as ttk
from view.sidebar import Sidebar
from view.admin.admin_dashboard_view import AdminDashboardPage
from view.admin.claims_view import ClaimsPage
from view.admin.user_view import UserPage
from view.history_view import HistoryPage
from view.settings_view import SettingsPage


class AdminLayout(ttk.Frame):
    def __init__(self, parent, show):
        super().__init__(parent)

        self.content = ttk.Frame(self)
        self.side = Sidebar(self, self.content)

        self.side.pack(side="left", fill="y")
        self.content.pack(side="right", fill="both", expand=True)

        self.side.add_page("Dashboard", AdminDashboardPage(self.content))
        self.side.add_page("Users", UserPage(self.content))
        self.side.add_page("Claims", ClaimsPage(self.content))
        self.side.add_page("History", HistoryPage(self.content))
        self.side.add_page("Settings", SettingsPage(self.content))
        self.side.add_item("Logout", lambda: show("login"))

        self.side.show_page("Dashboard")