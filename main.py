import ttkbootstrap as ttk
from database.connection import create_tables

create_tables()

def main():
    create_tables()
    root = ttk.App(title="PLV Lost and Found")
    root.theme_use("bootstrap-dark")
    
    root.mainloop()

if __name__ == "__main__":
    main()