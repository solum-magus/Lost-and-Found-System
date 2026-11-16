import ttkbootstrap as ttk

def main():
    root = ttk.App(title="PLV Lost and Found")
    root.theme_use("bootstrap-dark")
    
    root.mainloop()

if __name__ == "__main__":
    main()