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

        # Buttons for zooming
        self.zoom_in_button = ttk.Button(self, text="Zoom In", command=lambda: self.zoom_image(1.1))
        self.zoom_in_button.pack(pady=(5, 2))

        self.zoom_out_button = ttk.Button(self, text="Zoom Out", command=lambda: self.zoom_image(0.9))
        self.zoom_out_button.pack(pady=(2, 5))

        # Dragging functionality
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.dragging)

        # Save image button
        self.save_button = ttk.Button(self, text="Save Stitched Image", command=self.save_image)
        self.save_button.pack(pady=10)

    def start_drag(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def dragging(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom_image(self, zoom_factor):
        if not self.current_image:
            return
        width, height = int(zoom_factor * self.current_image.width), int(zoom_factor * self.current_image.height)
        self.current_image = self.current_image.resize((width, height))
        self.photo_image = ImageTk.PhotoImage(self.current_image)
        self.canvas.create_image(0, 0, image=self.photo_image, anchor='nw')
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
                logging.info(f"VIEW - Image successfully saved as {filepath}")
            else:
                logging.info("VIEW - Save image operation cancelled.")
        else:
            logging.warning("VIEW - No image to save.")
