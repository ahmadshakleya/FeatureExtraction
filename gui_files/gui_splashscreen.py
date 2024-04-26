from tkinter import Toplevel, ttk
from PIL import Image, ImageTk
from gui_files.gui_utils import center_window


class SplashScreen(Toplevel):
    def __init__(self, master, on_close_callback, image_path):
        super().__init__(master)
        self.on_close_callback = on_close_callback
        self.title('Loading...')
        self.geometry('800x600')  # Adjust size to fit your image if needed
        center_window(self)  # Center the splash screen
        self.configure(bg='white')

        # Load the image
        self.image = Image.open(image_path)
        self.photo_image = ImageTk.PhotoImage(self.image)

        # Display the image in a label
        self.label_image = ttk.Label(self, image=self.photo_image)
        self.label_image.pack(pady=20)

        # Optional: Add a text label below the image
        self.label_text = ttk.Label(self, text="Loading, please wait...", background='white')
        self.label_text.pack(expand=True)

        # Progress bar at the bottom
        self.progress = ttk.Progressbar(self, orient="horizontal", length=100, mode='determinate')
        self.progress.pack(expand=True, padx=20, pady=20)

        # Start updating the progress bar
        self.after(10, self.update_progress, 0)

    def update_progress(self, value):
        if value <= 10:
            self.progress['value'] = value
            self.after(10, self.update_progress, value+1)
        else:
            self.destroy()  # Close the splash screen
            self.on_close_callback()  # Call the callback function