import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from gui_files.gui_utils import center_window

class SplashScreen:
    def __init__(self, parent, on_close):
        self.parent = parent
        self.on_close = on_close
        self.root = tk.Toplevel(parent)
        self.root.title("Loading...")
        self.root.geometry("600x400")
        center_window(self.root)
        self.image_urls = [
            "https://github.com/ahmadshakleya/FeatureExtraction/blob/main/authors/1.jpg?raw=true",
            "https://github.com/ahmadshakleya/FeatureExtraction/blob/main/authors/2.jpg?raw=true",
            "https://github.com/ahmadshakleya/FeatureExtraction/blob/main/authors/3.jpg?raw=true"
        ]
        self.local_paths = ["images/1.jpg", "authors/2.jpg", "authors/3.jpg"]

        self.ensure_images()  # Ensure images are downloaded and available

        # Initial load of images with a default size
        initial_size = 200
        self.images = self.load_images(initial_size)

        # Configure layout
        self.setup_layout()
        self.update_progress()

        # Bind resize event
        self.root.bind('<Configure>', self.resize_images)

    def ensure_images(self):
        # Check if images exist locally; if not, download them
        for idx, path in enumerate(self.local_paths):
            if not os.path.exists(path):
                self.download_image(self.image_urls[idx], path)

    def download_image(self, url, path):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Download the image from the URL
        response = requests.get(url)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)

    def load_images(self, sizes):
        # Load and resize images dynamically based on the input size
        images = []
        for path in self.local_paths:
            img = Image.open(path)
            img = img.resize((sizes, sizes))
            images.append(ImageTk.PhotoImage(img))
        return images

    def setup_layout(self):
        # Use grid layout for better control during resize
        image_frame = tk.Frame(self.root)
        image_frame.pack(expand=True, fill=tk.BOTH, pady=1)

        self.image_labels = []
        for i, image in enumerate(self.images):
            frame = tk.Frame(image_frame)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            label_image = tk.Label(frame, image=image)
            label_image.image = image  # Keep a reference
            label_image.pack(expand=True)
            if i == 0:
                label_text = tk.Label(frame, text="Toon Smets", font=('Arial', 12, 'bold'))
            elif i == 1:
                label_text = tk.Label(frame, text="Ahmad Shakleya", font=('Arial', 12, 'bold'))
            else:
                label_text = tk.Label(frame, text="Ken Van Laer", font=('Arial', 12, 'bold'))
            label_text.pack()
            self.image_labels.append(label_image)

        # Configure column weights
        for i in range(len(self.images)):
            image_frame.grid_columnconfigure(i, weight=1)

        # Progress bar below the images
        self.progress = ttk.Progressbar(self.root, orient='horizontal', mode='determinate')
        self.progress.pack(side=tk.BOTTOM, fill=tk.X, expand=True, pady=20)

    def update_progress(self):
        self.progress['value'] += 10
        if self.progress['value'] >= 100:
            self.root.destroy()  # Close the splash screen when loading is complete
            self.on_close()  # Callback to initialize the main application UI
        else:
            self.root.after(500, self.update_progress)  # Update the progress bar every 500ms

    def resize_images(self, event):
        new_size = int(min(self.root.winfo_width(), self.root.winfo_height()) / 3)
        resized_images = self.load_images(new_size)
        for i, label in enumerate(self.image_labels):
            label.configure(image=resized_images[i])
            label.image = resized_images[i]  # Update image reference
