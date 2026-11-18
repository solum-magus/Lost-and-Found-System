import ttkbootstrap as ttk


class LoginPage(ttk.Frame):
    def __init__(self, parent, show):
        super().__init__(parent)

        card = ttk.Frame(self, padding=30)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="Login", font=("Segoe UI", 20, "bold")).pack(pady=(0, 20))

        ttk.Label(card, text="Username").pack(anchor="w")
        ttk.Entry(card, width=30).pack(pady=(0, 10))

        ttk.Label(card, text="Password").pack(anchor="w")
        ttk.Entry(card, width=30, show="*").pack(pady=(0, 20))

        # Login button directly navigates to the dashboard for demonstration purposes, add validation later
        # make an if statement to check if the user is an admin or a regular user and navigate accordingly
        #To test, comment out the line linking to the dashboard you dont want to test and uncomment the other one you want

        ttk.Button(card, text="Login", width=28,
                   command=lambda: show("user")).pack()
        #ttk.Button(card, text="Login", width=28,
        #                   command=lambda: show("admin")).pack()

        ttk.Button(card, text="No account? Sign Up", bootstyle="link",
                   command=lambda: show("signup")).pack(pady=(10, 0))