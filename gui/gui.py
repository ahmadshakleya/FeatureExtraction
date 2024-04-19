import tkinter as tk
from tkinter import ttk

class App1:
    def __init__(self, root):
        # Set up the main window
        self.root = root
        self.root.title('Python Tkinter App')
        self.root.geometry('640x480')
        
        # Create a Notebook (Tab Group)
        self.tab_group = ttk.Notebook(root)
        self.tab_group.pack(expand=1, fill="both")
        
        # Create Tabs
        self.file_tab = ttk.Frame(self.tab_group)
        self.insert_tab = ttk.Frame(self.tab_group)
        self.view_tab = ttk.Frame(self.tab_group)
        self.help_tab = ttk.Frame(self.tab_group)
        self.log_tab = ttk.Frame(self.tab_group)
        
        # Add tabs to the notebook
        self.tab_group.add(self.file_tab, text='File')
        self.tab_group.add(self.insert_tab, text='Insert')
        self.tab_group.add(self.view_tab, text='View')
        self.tab_group.add(self.help_tab, text='Help')
        self.tab_group.add(self.log_tab, text='Log')
        
        # You can add more widgets to each tab as needed
        # For example, adding a simple label to each tab
        ttk.Label(self.file_tab, text="Contents of File tab").pack(pady=20, padx=20)
        ttk.Label(self.insert_tab, text="Contents of Insert tab").pack(pady=20, padx=20)
        ttk.Label(self.view_tab, text="Contents of View tab").pack(pady=20, padx=20)
        ttk.Label(self.help_tab, text="Contents of Help tab").pack(pady=20, padx=20)
        ttk.Label(self.log_tab, text="Contents of Log tab").pack(pady=20, padx=20)

def main():
    root = tk.Tk()
    app = App1(root)
    root.mainloop()

if __name__ == '__main__':
    main()
