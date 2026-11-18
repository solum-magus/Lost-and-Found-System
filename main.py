import ttkbootstrap as ttk
import database.connection as db
from database.connection import create_tables
from view.sidebar import Sidebar
from view.login_view import LoginPage
from view.signup_view import SignupPage
from view.user.dashboard_view import DashboardPage
from view.user.user_layout import UserLayout
from view.admin.admin_layout import AdminLayout

def show(name):
    frames[name].tkraise()

create_tables() # Initialize database tables if they don't exist

root = ttk.App(title="PLV Lost and Found")
root.geometry("1000x600")
root.theme_use("bootstrap-dark")
root.iconbitmap("assets/PLV.ico")

frames = {
        "signup": SignupPage(root, show),
        "login": LoginPage(root, show),
        "user": UserLayout(root, show),
        "admin": AdminLayout(root, show)
    }

for frame in frames.values():
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

show("signup") # Start with the signup page
root.mainloop()