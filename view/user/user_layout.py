import ttkbootstrap as ttk
from view.sidebar import Sidebar
from view.user.dashboard_view import DashboardPage
from view.user.item_view import ItemPage
from view.user.claim_view import ClaimPage
from view.history_view import HistoryPage
from view.settings_view import SettingsPage


class UserLayout(ttk.Frame):
    def __init__(self, parent, show):
        super().__init__(parent)

        self.content = ttk.Frame(self)
        self.side = Sidebar(self, self.content)

        self.side.pack(side="left", fill="y")
        self.content.pack(side="right", fill="both", expand=True)

        self.side.add_page("Dashboard", DashboardPage(self.content))
        self.side.add_page("Items", ItemPage(self.content))
        self.side.add_page("Claims", ClaimPage(self.content))
        self.side.add_page("History", HistoryPage(self.content))
        self.side.add_page("Settings", SettingsPage(self.content))
        self.side.add_item("Logout", lambda: show("login"))

        self.side.show_page("Dashboard")