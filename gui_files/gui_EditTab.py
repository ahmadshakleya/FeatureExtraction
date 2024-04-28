import tkinter as tk
from tkinter import ttk, colorchooser, font

class EditTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.create_widgets()

    def create_widgets(self):
        # Section for changing window background color
        #ttk.Button(self, text="Change Window Color", command=self.change_window_color).pack(pady=10)

        # Section for changing text color
        ttk.Button(self, text="Change Text Color", command=self.change_text_color).pack(pady=10)

        # Section for changing text font
        self.font_var = tk.StringVar(value="Arial")
        self.font_box = ttk.Combobox(self, textvariable=self.font_var, values=sorted(list(font.families())))
        self.font_box.pack(pady=10)
        self.font_box.bind("<<ComboboxSelected>>", self.change_font)

        # Section for changing text size
        self.size_var = tk.IntVar(value=8)
        self.size_scale = ttk.Scale(self, from_=8, to=30, variable=self.size_var, orient="horizontal", command=self.change_font_size)
        self.size_scale.pack(pady=10)

        # Apply button for all settings
        ttk.Button(self, text="Apply Settings", command=self.apply_settings).pack(pady=20)

    def change_window_color(self):
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code:
            self.master.master.configure(bg=color_code)  # Master's master should refer to the root window

    def change_text_color(self):
        color_code = colorchooser.askcolor(title="Choose color")[1]
        if color_code:
            style = ttk.Style()
            style.configure('TLabel', foreground=color_code)
            style.configure('TButton', foreground=color_code)

    def change_font(self, event=None):
        self.apply_settings()

    def change_font_size(self, value):
        self.apply_settings()

    def apply_settings(self):
        font_name = self.font_var.get()
        font_size = int(self.size_var.get())
        style = ttk.Style()
        style.configure('TLabel', font=(font_name, font_size))
        style.configure('TButton', font=(font_name, font_size))
        style.configure('TEntry', font=(font_name, font_size))
        style.configure('TCombobox', font=(font_name, font_size))
