import ttkbootstrap as ttk

class Sidebar(ttk.Frame):
    def __init__(self, parent, content):
        super().__init__(parent, padding=10, bootstyle="secondary")
        self.content = content
        self.pages = {}

        ttk.Label(self, text="Menu", font=("Segoe UI", 12, "bold"),
                  bootstyle="inverse-secondary").pack(pady=(0, 15))

    def add_page(self, text, page):
        page.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.pages[text] = page
        ttk.Button(self, text=text, width=15, bootstyle="secondary",
                   command=lambda: self.show_page(text)).pack(fill="x", pady=3)

    def show_page(self, text):
        self.pages[text].tkraise()

    def add_item(self, text, command):
        ttk.Button(self, text=text, width=15, bootstyle="secondary",
                   command=command).pack(fill="x", pady=3)