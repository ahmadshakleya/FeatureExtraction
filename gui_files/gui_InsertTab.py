import tkinter as tk
from tkinter import Toplevel, ttk
from tkinter import filedialog, Canvas, PhotoImage
from PIL import Image, ImageTk
import logging
import tryouts.Ahmad.MultipleImageStitch as mis
import tryouts.Ahmad.TextHandler as th
import cv2
import threading

from tryouts.Ken.FeatureDetectionFunction import process_image_with_keypoints


class InsertTab(ttk.Frame):
    def __init__(self, master, view_tab):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.view_tab = view_tab
        self.image_paths = []
        self.photo_images = []  # Images for display
        self.display_keypoints = False  # Initially, keypoints are not displayed
        self.progress_bar = None
        self.status_label = None
        self.stitcher_settings = {
            "detector": "sift",
            "nfeatures": 1000,
            "matcher_type": "homography",
            "try_use_gpu": False,
            "confidence_threshold": 0.1,
            "warper_type": "plane",
            "crop": False,
        }  # Dictionary to hold the current settings
        self.create_widgets()

    def create_widgets(self):
        self.tab_control = ttk.Notebook(self)
        
        # Existing code tab
        self.existing_code_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.existing_code_tab, text='Images')
        self.setup_existing_code_tab(self.existing_code_tab)
        
        # Stitcher settings tab
        self.stitcher_settings_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.stitcher_settings_tab, text='Stitcher')
        self.setup_stitcher_settings_tab(self.stitcher_settings_tab)
        
        self.tab_control.pack(expand=1, fill="both")

    def setup_existing_code_tab(self, tab):
        ttk.Button(tab, text="Select Images", command=self.select_images).pack(pady=10)
        self.stitch_button = ttk.Button(tab, text="Stitch Images", command=self.stitch_images_wrapper, state=tk.DISABLED)
        self.stitch_button.pack(pady=10)

        self.image_canvas = Canvas(tab, bg='white')
        self.image_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=self.image_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.image_canvas)
        self.image_scrollable_window = self.image_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.image_canvas.configure(yscrollcommand=self.image_scrollbar.set)
        self.image_scrollbar.pack(side="right", fill="y")
        self.image_canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame.bind("<Configure>", lambda e: self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all")))

        self.status_label = ttk.Label(tab, text="Select images to start stitching.")
        self.status_label.pack(pady=20)

        self.delete_button = ttk.Button(tab, text="Delete Image", command=self.delete_selected_image)
        self.delete_button.pack(pady=10)
        self.delete_button.pack_forget()

        self.toggle_keypoints_button = ttk.Button(tab, text="Toggle Keypoints", command=self.toggle_keypoints, state=tk.DISABLED)
        self.toggle_keypoints_button.pack(pady=10)

        # Adding a progress bar
        self.progress_bar = ttk.Progressbar(tab, orient="horizontal", mode="determinate")
        self.progress_bar.pack(pady=20, fill='x')
        self.progress_bar['maximum'] = 100

    def setup_stitcher_settings_tab(self, tab):
        settings = {
            "detector": ["sift", "orb", "brisk", "akaze"],
            "nfeatures": 1000,
            "matcher_type": ["homography", "affine"],
            "try_use_gpu": [False, True],
            "confidence_threshold": 0.2,  # This will be handled by a slider
            "warper_type": ["plane", "cylindrical", "spherical", "fisheye", "stereographic", "compressedPlaneA2B1", "compressedPlaneA1.5B1", "compressedPlanePortraitA2B1", "compressedPlanePortraitA1.5B1", "paniniA2B1", "paniniA1.5B1", "paniniPortraitA2B1", "paniniPortraitA1.5B1", "mercator", "transverseMercator"],
            "crop": [False, True]
        }

        # Scrollable frame setup
        settings_canvas = Canvas(tab, highlightthickness=0)  # Remove any border highlight
        settings_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=settings_canvas.yview)
        scrollable_settings_frame = ttk.Frame(settings_canvas)

        settings_canvas.create_window((0, 0), window=scrollable_settings_frame, anchor="center", width=400)  # Centered window
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
        settings_scrollbar.pack(side="right", fill="y")
        settings_canvas.pack(side="left", fill="both", expand=True)

        scrollable_settings_frame.bind("<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))

        # Create and pack widgets dynamically
        for setting, value in settings.items():
            container = ttk.Frame(scrollable_settings_frame)
            container.pack(fill='x', padx=10, pady=2, expand=True)
            if setting == "nfeatures":
                ttk.Label(container, text="Amount of features to be detected:", anchor='center').pack(side='left', padx=10)
            elif setting == "crop":
                ttk.Label(container, text="Crop the result:", anchor='center').pack(side='left', padx=10)
            else:
                ttk.Label(container, text=f"{setting.replace('_', ' ').capitalize()}:", anchor='center').pack(side='left', padx=10)

            if isinstance(value, list) and setting in ["detector", "matcher_type", "try_use_gpu", "crop"]:
                frame = ttk.Frame(container)
                frame.pack(fill='x', padx=10, pady=2)
                for option in value:
                    rb = ttk.Radiobutton(frame, text=str(option), value=option, variable=self.stitcher_settings[setting], command=lambda s=setting, v=option: self.update_stitcher_setting(s, v))
                    rb.pack(side='left')
                    if value.index(option) == 0 and setting != "crop":
                        rb.invoke()
            elif isinstance(value, list):
                # Create a combobox for other list type settings
                combo = ttk.Combobox(container, values=value)
                combo.pack(fill='x', padx=10, pady=2)
                combo.set(value[0])  # Set the first item as default
                combo.bind("<<ComboboxSelected>>", lambda e, s=setting, c=combo: self.update_stitcher_setting(s, c.get()))
            elif setting == "confidence_threshold":
                # Create a slider for confidence threshold and label to display the value
                slider_frame = ttk.Frame(container)
                slider_frame.pack(fill='x', expand=True, padx=10, pady=2)
                slider_label = ttk.Label(slider_frame, text=f"{value:.2f}")
                slider_label.pack(side='right')
                slider = ttk.Scale(slider_frame, from_=0.0, to=1.0, orient='horizontal', command=lambda v, sl=slider_label, s=setting: self.update_slider(s, float(v), sl))
                slider.set(value)  # Set the initial value
                slider.pack(fill='x', expand=True)
            else:
                # Create an entry for string type settings
                entry = ttk.Entry(container)
                entry.pack(fill='x', padx=10, pady=2)
                entry.insert(0, value)  # Set the value as default
                entry.bind("<FocusOut>", lambda e, s=setting, en=entry: self.update_stitcher_setting(s, int(en.get())))

    def update_slider(self, setting, value, label):
        self.stitcher_settings[setting] = round(value, 2)
        label.config(text=f"{round(value, 2):.2f}")
        logging.info(f"Updated setting {setting} to {round(value, 2)}")
        self.progress_bar['value'] = 0
        self.update_status("Ready to stitch!")


    def update_stitcher_setting(self, setting, value):
        self.stitcher_settings[setting] = value
        logging.info(f"Updated setting {setting} to {value}")
        self.progress_bar['value'] = 0
        self.update_status("Ready to stitch!")

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
                img = process_image_with_keypoints(img, self.stitcher_settings["detector"], draw_keypoints=True, nfeatures=self.stitcher_settings["nfeatures"])
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
        total_images = len(images)
        for i, img in enumerate(images):
            progress = ((i + 1) / total_images) * 100
            self.update_progress(progress)

        stitched = mis.stitch_images(images, self.stitcher_settings)  # Use the updated settings
        if stitched is not None:
            stitched = cv2.cvtColor(stitched, cv2.COLOR_BGR2RGB)
            self.view_tab.show_image_on_canvas(Image.fromarray(stitched))
            if self.progress_bar['value'] != 0:
                self.status_label.config(text="Stitching completed successfully!")
            else:
                self.status_label.config(text="Ready to stitch!")
            logging.info("Stitching completed successfully.")
        else:
            self.status_label.config(text="Failed to stitch images.")
            logging.error("Failed to stitch images.")

    def update_progress(self, progress):
        self.progress_bar['value'] = progress
        self.update_idletasks()

    def update_status(self, message):
        self.status_label.config(text=message)
        self.update_idletasks()
