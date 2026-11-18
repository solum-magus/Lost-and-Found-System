# display recent lost and found items, activity overview(eg. pending claims, report status), etc
import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class HomeView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=20)
        ttk.Label(self, text="Home", font=("Segoe UI", 20, "bold")).pack(anchor=W)
        ttk.Label(self, text="This is the home page.").pack(anchor=W, pady=10)