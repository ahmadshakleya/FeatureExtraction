import tkinter as tk
from tkinter import Toplevel, ttk
from tkinter import filedialog, Canvas, PhotoImage
from PIL import Image, ImageTk
import logging
import tryouts.Ahmad.MultipleImageStitch as mis
import tryouts.Ahmad.TextHandler as th
import cv2

from tryouts.Ken.FeatureDetectionFunction import process_image_with_keypoints


class InsertTab(ttk.Frame):
    def __init__(self, master, view_tab):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.view_tab = view_tab
        self.image_paths = []
        self.photo_images = []  # Images for display
        self.display_keypoints = False  # Initially, keypoints are not displayed
        self.create_widgets()

    def create_widgets(self):
        ttk.Button(self, text="Select Images", command=self.select_images).pack(pady=10)
        self.stitch_button = ttk.Button(self, text="Stitch Images", command=self.stitch_images_wrapper, state=tk.DISABLED)
        self.stitch_button.pack(pady=10)

        self.image_canvas = Canvas(self, bg='white')
        self.image_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.image_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.image_canvas)
        self.image_scrollable_window = self.image_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.image_canvas.configure(yscrollcommand=self.image_scrollbar.set)
        self.image_scrollbar.pack(side="right", fill="y")
        self.image_canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame.bind("<Configure>", lambda e: self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all")))

        self.status_label = ttk.Label(self, text="Select images to start stitching.")
        self.status_label.pack(pady=20)

        self.delete_button = ttk.Button(self, text="Delete Image", command=self.delete_selected_image)
        self.delete_button.pack(pady=10)
        self.delete_button.pack_forget()  # Initially hide the delete button

        self.toggle_keypoints_button = ttk.Button(self, text="Toggle Keypoints", command=self.toggle_keypoints, state=tk.DISABLED)
        self.toggle_keypoints_button.pack(pady=10)

    def toggle_keypoints(self):
        self.display_keypoints = not self.display_keypoints
        self.display_selected_images()

    def select_images(self):
        image_paths_tuple = filedialog.askopenfilenames(
            title="Select images", filetypes=[("JPEG Files", "*.jpg;*.jpeg"), ("PNG Files", "*.png"), ("All files", "*.*")]
        )
        self.image_paths = list(image_paths_tuple)  # Convert tuple to list right here
        if self.image_paths:
            self.status_label.config(text=f"Selected {len(self.image_paths)} images.")
            logging.info(f"Selected {len(self.image_paths)} images for stitching.")
            self.display_selected_images()  # Refresh display to possibly include keypoints
            self.toggle_keypoints_button['state'] = tk.NORMAL
            self.stitch_button['state'] = tk.NORMAL if len(self.image_paths) > 1 else tk.DISABLED
        else:
            self.stitch_button['state'] = self.toggle_keypoints_button['state'] = tk.DISABLED

    def display_selected_images(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.photo_images = []
        for path in self.image_paths:
            img = Image.open(path)
            if self.display_keypoints:
                img = process_image_with_keypoints(img)
            photo = ImageTk.PhotoImage(img)
            self.photo_images.append(photo)  # Retain a reference
            label = ttk.Label(self.scrollable_frame, image=photo)
            label.image = photo  # Retain another reference
            label.pack(pady=10)
            label.bind("<Button-1>", lambda e, index=self.image_paths.index(path): self.select_image(e, index))

        self.image_canvas.yview_moveto(0)

    def select_image(self, event, index):
        for label in self.scrollable_frame.winfo_children():
            label.configure(relief=tk.FLAT)
        event.widget.configure(relief=tk.RAISED)
        self.selected_image_index = index
        if not self.delete_button.winfo_ismapped():
            self.delete_button.pack(pady=10)

    def delete_selected_image(self):
        if hasattr(self, 'selected_image_index') and self.selected_image_index is not None:
            del self.image_paths[self.selected_image_index]
            del self.photo_images[self.selected_image_index]
            self.display_selected_images()
            self.delete_button.pack_forget()
            self.selected_image_index = None
            self.status_label.config(text=f"Updated selection. {len(self.image_paths)} images remain.")
            logging.info("Image deleted successfully.")

    def stitch_images_wrapper(self):
        if not self.image_paths:
            self.status_label.config(text="No images selected!")
            logging.warning("No images selected for stitching.")
            return

        images = mis.load_images(self.image_paths)
        stitched = mis.stitch_images(images)
        if stitched is not None:
            stitched = cv2.cvtColor(stitched, cv2.COLOR_BGR2RGB)
            self.view_tab.show_image_on_canvas(Image.fromarray(stitched))
            self.status_label.config(text="Stitching completed successfully!")
            logging.info("Stitching completed successfully.")
        else:
            self.status_label.config(text="Failed to stitch images.")
            logging.error("Failed to stitch images.")