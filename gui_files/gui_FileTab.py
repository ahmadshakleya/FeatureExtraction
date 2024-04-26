import logging
import tkinter as tk
from tkinter import ttk, filedialog


class FileTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.create_widgets()

    def create_widgets(self):
        ttk.Button(self, text="Open Image", command=self.open_image).pack(pady=10)
        ttk.Button(self, text="Save Image As...", command=self.save_image_as).pack(pady=10)
        ttk.Label(self, text="File operations for images.").pack(pady=20)

    def open_image(self):
        filepath = filedialog.askopenfilename(
            title="Open Image",
            filetypes=(("JPEG Files", "*.jpg;*.jpeg"), ("PNG Files", "*.png"), ("All Files", "*.*"))
        )
        if filepath:
            # Assuming you want to do something with the opened file
            logging.info(f"Opened image: {filepath}")
            # Here you might update an image display or other elements

    def save_image_as(self):
        filepath = filedialog.asksaveasfilename(
            title="Save Image As",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if filepath:
            # Assuming you have an image in your application to save
            logging.info(f"Image saved as: {filepath}")
            # Here you would actually save the file using PIL or similar
