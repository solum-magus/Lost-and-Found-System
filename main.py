import ttkbootstrap as ttk
import database.connection as db
from database.connection import create_tables
from view.sidebar import Sidebar

create_tables()

def main():
    create_tables()
    root = ttk.App(title="PLV Lost and Found")
    root.theme_use("bootstrap-dark")
    root.iconbitmap("assets/PLV.ico")

    root.sidebar = Sidebar(root)
    root.sidebar.pack(side="left", fill="y")
    
    root.mainloop()

if __name__ == "__main__":
    main()