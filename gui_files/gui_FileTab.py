import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, Canvas
from PIL import Image, ImageTk
import logging

import numpy as np
import tryouts.Ahmad.MultipleImageStitch as mis
import cv2
from stitching.feature_detector import FeatureDetector

from tryouts.Ken.FeatureDetectionFunction import process_image_with_keypoints
from tryouts.Toon.featureMatcher import process_and_display_matches


class FileTab(ttk.Frame):
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

        # Matcher settings tab
        self.matcher_settings_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.matcher_settings_tab, text='Matcher')
        self.setup_matcher_settings_tab(self.matcher_settings_tab)

        
        self.tab_control.pack(expand=1, fill="both")

    def setup_matcher_settings_tab(self, tab):
        ttk.Label(tab, text="Select Two Images for Matching").pack(pady=10, fill='x')

        self.image_selector_1 = ttk.Combobox(tab, values=self.image_paths, state="readonly")
        self.image_selector_1.pack(pady=5, fill='x', expand=True)
        self.image_selector_2 = ttk.Combobox(tab, values=self.image_paths, state="readonly")
        self.image_selector_2.pack(pady=5, fill='x', expand=True)

        ttk.Label(tab, text="Matcher Type:").pack(pady=5, fill='x')
        self.matcher_type_combobox = ttk.Combobox(tab, values=["homography", "affine"], state="readonly")
        self.matcher_type_combobox.pack(pady=5, fill='x', expand=True)
        self.matcher_type_combobox.set("homography")

        ttk.Label(tab, text="Confidence Threshold:").pack(pady=5, fill='x')
        slider_frame = ttk.Frame(tab)
        slider_frame.pack(pady=10, fill='x', expand=True)
        self.confidence_threshold_scale = ttk.Scale(slider_frame, from_=0.0, to=1.0, orient="horizontal")
        self.confidence_threshold_scale.set(0.3)
        self.confidence_threshold_scale.pack(side='left', fill='x', expand=True)
        self.confidence_label = ttk.Label(slider_frame, text=f"{self.confidence_threshold_scale.get():.2f}")
        self.confidence_label.pack(side='left', padx=10)

        # Set the command for the slider after all other GUI elements are initialized
        self.confidence_threshold_scale['command'] = self.update_confidence_label

        # Button frame for side-by-side buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(pady=10, fill='x')

        self.match_button = ttk.Button(button_frame, text="Match Features", command=self.match_features, state="disabled")
        self.match_button.pack(side='left', fill='x', expand=True)

        self.save_matched_image_button = ttk.Button(button_frame, text="Save Matched Image", command=self.save_matched_image)
        self.save_matched_image_button.pack(side='left', fill='x', expand=True)
        self.save_matched_image_button['state'] = tk.DISABLED  # Initially disabled

        self.match_canvas = Canvas(tab, bg='white')
        self.match_scrollbar_v = ttk.Scrollbar(tab, orient="vertical", command=self.match_canvas.yview)
        self.match_scrollbar_h = ttk.Scrollbar(tab, orient="horizontal", command=self.match_canvas.xview)
        self.match_canvas.configure(yscrollcommand=self.match_scrollbar_v.set, xscrollcommand=self.match_scrollbar_h)
        self.match_scrollbar_v.pack(side="right", fill="y")
        self.match_scrollbar_h.pack(side="bottom", fill="x")
        self.match_canvas.pack(side="left", fill="both", expand=True)

        self.image_selector_1.bind("<<ComboboxSelected>>", self.update_match_button_state)
        self.image_selector_2.bind("<<ComboboxSelected>>", self.update_match_button_state)



    def update_confidence_label(self, value):
        """ Update the label next to the confidence threshold slider to show its current value. """
        self.confidence_label.config(text=f"{float(value):.2f}")





    def update_match_button_state(self, event=None):
        selected_1 = self.image_selector_1.get()
        selected_2 = self.image_selector_2.get()
        if selected_1 and selected_2 and selected_1 != selected_2:
            self.match_button['state'] = 'normal'
        else:
            self.match_button['state'] = 'disabled'

    def save_matched_image(self):
        if hasattr(self, 'matched_images') and self.matched_images:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if save_path:
                cv2.imwrite(save_path, self.matched_images[0])  # Assuming the first in list is the one to save
                self.status_label.config(text="Matched image saved successfully.")
                logging.info(f"FILE - MATCHER - Matched image saved to {save_path}")
            else:
                self.status_label.config(text="Matched image not saved.")
                logging.info("FILE - MATCHER - Matched image not saved.")

    def match_features(self):
        selected_path_1 = self.image_selector_1.get()
        selected_path_2 = self.image_selector_2.get()
        if not selected_path_1 or not selected_path_2:
            logging.error("FILE - MATCH - Attempt to match features without selecting both images.")
            self.update_status("Select two different images to match features.")
            return

        try:
            img1 = Image.open(selected_path_1).convert('RGB')
            img2 = Image.open(selected_path_2).convert('RGB')
            cv_images = [cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR) for img in [img1, img2]]
            feature_detector = FeatureDetector(detector=self.stitcher_settings['detector'], nfeatures=self.stitcher_settings['nfeatures'])
            feature_sets = [feature_detector.detect_features(img) for img in cv_images]

            matcher_type = self.matcher_type_combobox.get()
            confidence_threshold = self.confidence_threshold_scale.get()
            matched_images = process_and_display_matches(cv_images, feature_sets, matcher_type, confidence_threshold)
            if matched_images:
                self.display_matched_images(matched_images)
                logging.info("FILE - MATCHER - Feature matching completed successfully.")
            else:
                logging.warning("FILE - MATCHER - Feature matching did not return any results.")
                self.update_status("No matches found.")
        except Exception as e:
            logging.error(f"FILE - MATCHER - Failed to match features between selected images: {str(e)}")
            self.update_status("Error during feature matching.")



    def display_matched_images(self, matched_images):
        # Clear existing images
        self.match_canvas.delete("all")

        y_position = 0
        for img in matched_images:
            tk_img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
            self.match_canvas.create_image(0, y_position, image=tk_img, anchor='nw')
            y_position += tk_img.height() + 10  # Adjust spacing between images
            self.match_canvas.image = tk_img  # Retain a reference

        self.match_canvas.config(scrollregion=self.match_canvas.bbox("all"))
        self.matched_images = matched_images  # Store matched images
        self.save_matched_image_button['state'] = tk.NORMAL if matched_images else tk.DISABLED


    def setup_existing_code_tab(self, tab):
        ttk.Button(tab, text="Select Images", command=self.select_images).pack(pady=10)
        self.stitch_button = ttk.Button(tab, text="Stitch Images", command=self.stitch_images_wrapper, state=tk.DISABLED)
        self.stitch_button.pack(pady=10)

        self.image_canvas = Canvas(tab, bg='white')
        self.image_scrollbar_vertical = ttk.Scrollbar(tab, orient="vertical", command=self.image_canvas.yview)
        self.image_scrollbar_horizontal = ttk.Scrollbar(tab, orient="horizontal", command=self.image_canvas.xview)

        self.scrollable_frame = ttk.Frame(self.image_canvas)
        self.image_scrollable_window = self.image_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.image_canvas.configure(yscrollcommand=self.image_scrollbar_vertical.set, xscrollcommand=self.image_scrollbar_horizontal.set)
        # Pack the scrollbars
        self.image_scrollbar_vertical.pack(side="right", fill="y")
        self.image_scrollbar_horizontal.pack(side="bottom", fill="x")

        # Pack the canvas
        self.image_canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame.bind("<Configure>", lambda e: self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all")))

        self.status_label = ttk.Label(tab, text="Select images to start stitching.")
        self.status_label.pack(pady=20)

        self.delete_button = ttk.Button(tab, text="Delete Image", command=self.delete_selected_image)
        self.delete_button.pack(pady=10)
        self.delete_button.pack_forget()

        self.save_button = ttk.Button(tab, text="Save Image with Keypoints", command=self.save_image_with_keypoints)
        self.save_button.pack(pady=10)
        self.save_button['state'] = tk.DISABLED  # Initially disabled


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

        # Dictionary to hold variables for each radiobutton group
        self.stitcher_settings_vars = {key: tk.StringVar() for key in settings if isinstance(settings[key], list) and key in ["detector", "matcher_type", "try_use_gpu", "crop"]}

        # Scrollable frame setup
        settings_canvas = Canvas(tab, highlightthickness=0)  # Remove any border highlight
        settings_scrollbar = ttk.Scrollbar(tab, orient="vertical", command=settings_canvas.yview)
        scrollable_settings_frame = ttk.Frame(settings_canvas)

        settings_canvas.create_window((0, 0), window=scrollable_settings_frame, anchor="center", width=settings_canvas.winfo_reqwidth())  # Centered window
        settings_canvas.configure(yscrollcommand=settings_scrollbar.set)
        settings_scrollbar.pack(side="right", fill="y")
        settings_canvas.pack(side="left", fill="both", expand=True)

        scrollable_settings_frame.bind("<Configure>", lambda e: settings_canvas.configure(scrollregion=settings_canvas.bbox("all")))

        # Create and pack widgets dynamically
        for setting, value in settings.items():
            container = ttk.Frame(scrollable_settings_frame)
            container.pack(fill='x', padx=10, pady=2, expand=True)

            ttk.Label(container, text=f"{setting.replace('_', ' ').capitalize()}:", anchor='center').pack(side='left', padx=10)

            if isinstance(value, list) and setting in ["detector", "matcher_type", "try_use_gpu", "crop"]:
                frame = ttk.Frame(container)
                frame.pack(fill='x', padx=10, pady=2)
                for option in value:
                    rb = ttk.Radiobutton(frame, text=str(option), value=option, variable=self.stitcher_settings_vars[setting], command=lambda s=setting, v=option: self.update_stitcher_setting(s, v))
                    rb.pack(side='left')
                    if value.index(option) == 0:
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
        logging.info(f"FILE - STITCHER - Updated setting {setting} to {round(value, 2)}")
        self.progress_bar['value'] = 0
        self.update_status("Ready to stitch!")
        if hasattr(self, 'match_canvas'):
            self.clear_match_results()  # Clear matcher tab when new images are selected


    def update_stitcher_setting(self, setting, value):
        self.stitcher_settings[setting] = value
        logging.info(f"FILE - STITCHER - Updated setting {setting} to {value}")
        self.progress_bar['value'] = 0
        self.update_status("Ready to stitch!")
        if hasattr(self, 'match_canvas'):
            self.clear_match_results()  # Clear matcher tab when new images are selected

    def toggle_keypoints(self):
        self.display_keypoints = not self.display_keypoints
        self.display_selected_images()
        self.check_keypoints_and_toggle_save_button()


    def select_images(self):
        self.progress_bar['value'] = 0
        try:
            image_paths_tuple = filedialog.askopenfilenames(
                title="Select images", filetypes=[("JPEG Files", "*.jpg;*.jpeg"), ("PNG Files", "*.png"), ("All files", "*.*")]
            )
            self.image_paths = list(image_paths_tuple)
            if self.image_paths:
                self.status_label.config(text=f"Selected {len(self.image_paths)} images.")
                logging.info(f"FILE - IMAGES - Selected {len(self.image_paths)} images for stitching.")
                self.display_selected_images()
                self.toggle_keypoints_button['state'] = tk.NORMAL
                self.stitch_button['state'] = tk.NORMAL if len(self.image_paths) > 1 else tk.DISABLED
                self.update_comboboxes()
                self.clear_match_results()  # Clear matcher tab when new images are selected
            else:
                self.stitch_button['state'] = self.toggle_keypoints_button['state'] = tk.DISABLED
                logging.info("FILE - IMAGES - No images were selected.")
        except Exception as e:
            logging.error(f"FILE - IMAGES - Failed to select images: {str(e)}")
            self.status_label.config(text="Error selecting images.")



    def update_comboboxes(self):
        # Update the combobox list when new images are selected
        self.image_selector_1['values'] = self.image_paths
        self.image_selector_2['values'] = self.image_paths
        self.image_selector_1.set('')
        self.image_selector_2.set('')


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
            logging.info("FILE - IMAGES - Image deleted successfully.")

    def stitch_images_wrapper(self):
        if not self.image_paths:
            self.status_label.config(text="No images selected!")
            logging.warning("FILE - IMAGES - Attempted to stitch with no images selected.")
            return

        try:
            images = mis.load_images(self.image_paths)
            total_images = len(images)
            for i, img in enumerate(images):
                progress = ((i + 1) / total_images) * 100
                self.update_progress(progress)

            stitched = mis.stitch_images(images, self.stitcher_settings)
            if stitched is not None:
                stitched = cv2.cvtColor(stitched, cv2.COLOR_BGR2RGB)
                self.view_tab.show_image_on_canvas(Image.fromarray(stitched))
                self.status_label.config(text="Stitching completed successfully!")
            else:
                self.status_label.config(text="Failed to stitch images.")
                logging.error("FILE - IMAGES - Stitching process failed.")
        except Exception as e:
            logging.error(f"FILE - IMAGES - Stitching error: {str(e)}")
            self.status_label.config(text="Error during stitching process.")


    def update_progress(self, progress):
        self.progress_bar['value'] = progress
        self.update_idletasks()

    def update_status(self, message):
        self.status_label.config(text=message)
        self.update_idletasks()

    def clear_match_results(self):
        """ Clears the match results and resets the matcher tab state. """
        self.match_canvas.delete("all")  # Clear the canvas
        self.image_selector_1.set('')
        self.image_selector_2.set('')
        self.match_button['state'] = 'disabled'  # Disable the match button until new images are selected
        logging.info("FILE - MATCHER - Matcher tab results and selections have been cleared.")

    def check_keypoints_and_toggle_save_button(self):
        if self.display_keypoints and hasattr(self, 'selected_image_index'):
            self.save_button['state'] = tk.NORMAL
        else:
            self.save_button['state'] = tk.DISABLED

    def save_image_with_keypoints(self):
        if hasattr(self, 'selected_image_index') and self.photo_images[self.selected_image_index]:
            image_path = self.image_paths[self.selected_image_index]
            img = Image.open(image_path)
            img_with_keypoints = process_image_with_keypoints(img, self.stitcher_settings["detector"], draw_keypoints=True, nfeatures=self.stitcher_settings["nfeatures"])
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
            if save_path:
                img_with_keypoints.save(save_path)
                self.status_label.config(text="Image saved with keypoints.")
                logging.info(f"FILE - IMAGES - Image with keypoints saved to {save_path}")
            else:
                self.status_label.config(text="Image not saved.")
                logging.info("FILE - IMAGES - Image not saved.")

