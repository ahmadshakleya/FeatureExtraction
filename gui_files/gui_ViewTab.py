import tkinter as tk
from tkinter import ttk, filedialog, Canvas
from PIL import Image, ImageTk
import logging


class ViewTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.create_widgets()
        self.current_image = None  # To hold the current PIL image

    def create_widgets(self):
        # Canvas setup
        self.canvas = Canvas(self, bg='black')
        self.canvas.pack(side='top', fill='both', expand=True)

        # Scrollbars for the canvas
        self.hbar = ttk.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        self.hbar.pack(side='bottom', fill='x')
        self.canvas.configure(xscrollcommand=self.hbar.set)

        self.vbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.vbar.pack(side='right', fill='y')
        self.canvas.configure(yscrollcommand=self.vbar.set)

        # Mouse wheel zooming
        self.canvas.bind('<MouseWheel>', self.zoom_image)

        # Save image button
        self.save_button = ttk.Button(self, text="Save Stitched Image", command=self.save_image)
        self.save_button.pack(pady=10)

    def zoom_image(self, event):
        if not self.current_image:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        factor = 1.1 if event.delta > 0 else 0.9
        width, height = int(factor * self.current_image.width()), int(factor * self.current_image.height())
        self.current_image = self.current_image.resize((width, height), Image.ANTIALIAS)
        self.photo_image = ImageTk.PhotoImage(self.current_image)
        self.canvas.create_image(x, y, image=self.photo_image, anchor='center')
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def show_image_on_canvas(self, img):
        """Utility to display image on canvas"""
        self.current_image = img
        self.photo_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=self.photo_image, anchor='nw')
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def save_image(self):
        """Save the currently displayed stitched image."""
        if self.current_image:  # Check if there is an image to save
            filepath = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
                title="Save Image"
            )
            if filepath:  # If a file path was chosen
                self.current_image.save(filepath)  # Save the image under the given path
                logging.info(f"Image successfully saved as {filepath}")
            else:
                logging.info("Save image operation cancelled.")
        else:
            logging.warning("No image to save.")