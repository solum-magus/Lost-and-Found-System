import ttkbootstrap as ttk


class SignupPage(ttk.Frame):
    def __init__(self, parent, show):
        super().__init__(parent)

        card = ttk.Frame(self, padding=30)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="Sign Up", font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))

        ttk.Label(card, text="Username").pack(anchor="w")
        ttk.Entry(card, width=30).pack(pady=(0, 10))

        ttk.Label(card, text="Password").pack(anchor="w")
        ttk.Entry(card, width=30, show="*").pack(pady=(0, 20))

        ttk.Button(card, text="Sign Up", width=28,
                   command=lambda: show("login")).pack()

        ttk.Button(card, text="Already have an account? Login", bootstyle="link",
                   command=lambda: show("login")).pack(pady=(10, 0))