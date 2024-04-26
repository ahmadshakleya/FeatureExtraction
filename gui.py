import tkinter as tk
from tkinter import Toplevel, ttk
from tkinter import filedialog, Canvas, PhotoImage, scrolledtext
from PIL import Image, ImageTk
import logging
import cv2
import tryouts.Ahmad.MultipleImageStitch as mis  # Importing your module
import tryouts.Ahmad.TextHandler as th  # Importing your module
import time
import fitz  # PyMuPDF
from tryouts.Ken.FeatureDetectionFunction import process_image_with_keypoints


class SplashScreen(Toplevel):
    def __init__(self, master, on_close_callback, image_path):
        super().__init__(master)
        self.on_close_callback = on_close_callback
        self.title('Loading...')
        self.geometry('800x600')  # Adjust size to fit your image if needed
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

def setup_logging(text_widget):
    # Set the logger to handle and format messages
    log_handler = th.TextHandler(text_widget)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    return logger

class App1:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide main window during splash screen
        self.splash = SplashScreen(self.root, self.initialize_ui, image_path="image.jpg")

    def initialize_ui(self):
        """Initialize the main window UI after the splash screen closes."""
        self.root.deiconify()  # Show the main window
        self.root.title('CellBlend App')
        self.root.geometry('800x600')

        self.tab_group = ttk.Notebook(self.root)
        self.tab_group.pack(expand=1, fill="both")

        self.file_tab = ttk.Frame(self.tab_group)
        self.insert_tab = ttk.Frame(self.tab_group)
        self.view_tab = ttk.Frame(self.tab_group)
        self.help_tab = ttk.Frame(self.tab_group)
        self.log_tab = ttk.Frame(self.tab_group)

        self.tab_group.add(self.file_tab, text='File')
        self.tab_group.add(self.insert_tab, text='Insert')
        self.tab_group.add(self.view_tab, text='View')
        self.tab_group.add(self.help_tab, text='Help')
        self.tab_group.add(self.log_tab, text='Log')

        # Set up the log tab with export button
        self.log_widget = scrolledtext.ScrolledText(self.log_tab, state='disabled')
        self.log_widget.pack(fill="both", expand=True)

        # Set up logging
        self.logger = setup_logging(self.log_widget)

        self.export_button = ttk.Button(self.log_tab, text="Export Logs", command=self.export_logs)
        self.export_button.pack(pady=10)

        # Create textHandler and configure logging
        text_handler = th.TextHandler(self.log_widget)
        logging.basicConfig(level=logging.INFO, handlers=[text_handler])

        # Image display setup
        self.canvas = Canvas(self.view_tab, bg='black')
        self.canvas.pack(side='top', fill='both', expand=True)
        self.scale = 1.0  # initial zoom scale

        # Add scrollbars to the canvas
        self.hbar = ttk.Scrollbar(self.view_tab, orient='horizontal', command=self.canvas.xview)
        self.hbar.pack(side='bottom', fill='x')
        self.canvas.configure(xscrollcommand=self.hbar.set)

        self.vbar = ttk.Scrollbar(self.view_tab, orient='vertical', command=self.canvas.yview)
        self.vbar.pack(side='right', fill='y')
        self.canvas.configure(yscrollcommand=self.vbar.set)

        # Mouse wheel for zooming
        self.canvas.bind('<MouseWheel>', self.zoom_image)

        # Save image button
        self.save_button = ttk.Button(self.view_tab, text="Save Stitched Image", command=self.save_image)
        self.save_button.pack(pady=10)

        # Setup in Insert Tab for selecting multiple images and stitching
        ttk.Button(self.insert_tab, text="Select Images", command=self.select_images).pack(pady=10)
        ttk.Button(self.insert_tab, text="Stitch Images", command=self.stitch_images_wrapper).pack(pady=10)

        # Scrollable area for displaying images
        self.image_canvas = Canvas(self.insert_tab, bg='white')
        self.image_scrollbar = ttk.Scrollbar(self.insert_tab, orient="vertical", command=self.image_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.image_canvas)

        self.image_scrollable_window = self.image_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.image_canvas.configure(yscrollcommand=self.image_scrollbar.set)
        self.image_scrollbar.pack(side="right", fill="y")
        self.image_canvas.pack(side="left", fill="both", expand=True)

        self.scrollable_frame.bind("<Configure>", lambda e: self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all")))

        self.status_label = ttk.Label(self.insert_tab, text="Select images to start stitching.")
        self.status_label.pack(pady=20)

        # Delete button initialization
        self.delete_button = ttk.Button(self.insert_tab, text="Delete Image", command=self.delete_selected_image)
        self.delete_button.pack(pady=10)
        self.delete_button.pack_forget()  # Hide the button initially

        self.display_keypoints = False  # Track the state of keypoints display
        self.toggle_keypoints_button = ttk.Button(self.insert_tab, text="Toggle Keypoints", command=self.toggle_keypoints)
        self.toggle_keypoints_button.pack(pady=10)

        self.image_paths = []
        self.photo_image = None  # To hold the PhotoImage reference
        self.photo_images = []  # Initialize in the __init__ method
        self.current_image = None  # To hold the current PIL image

        self.setup_help_tab()

        logging.info("Application started")  # Log the start of the application

    def toggle_keypoints(self):
        self.display_keypoints = not self.display_keypoints
        self.display_selected_images()
    
    def select_images(self):
        self.image_paths = filedialog.askopenfilenames(
            title="Select images",
            filetypes=(("JPEG Files", "*.jpg;*.jpeg"), ("PNG Files", "*.png"), ("All files", "*.*"))
        )
        if self.image_paths:
            self.status_label.config(text=f"Selected {len(self.image_paths)} images.")
            logging.info(f"Selected {len(self.image_paths)} images for stitching.")
            self.display_selected_images()  # Display each selected image

    def display_selected_images(self):
        # Clear the frame first
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.photo_images = []  # Reset or initialize the list to store image references

        for i, path in enumerate(self.image_paths):
            img = Image.open(path)
            if self.display_keypoints:
                img = process_image_with_keypoints(img, draw_keypoints=True)
            else:
                img = process_image_with_keypoints(img, draw_keypoints=False)

            photo = ImageTk.PhotoImage(img)
            self.photo_images.append(photo)  # Keep the reference to avoid garbage collection
            label = ttk.Label(self.scrollable_frame, image=photo)
            label.image = photo  # Keep another reference, required by Tkinter to display the image
            label.pack(pady=10)  # Pack each image with some padding
            label.bind("<Button-1>", lambda e, index=i: self.select_image(e, index))  # Bind click event

        self.image_canvas.yview_moveto(0)  # Scrolls back to the top after updating


    def select_image(self, event, index):
        """Highlight the selected image and prepare for possible deletion."""
        # Highlight the selected image
        for label in self.scrollable_frame.winfo_children():
            label.configure(relief=tk.FLAT)  # Reset relief of all images
        event.widget.configure(relief=tk.RAISED)  # Highlight the clicked label
        self.selected_image_index = index  # Save the index of the selected image
        
        # Show the 'Delete' button if not already visible
        if not self.delete_button.winfo_ismapped():
            self.delete_button.pack(pady=10)

    def select_images(self):
        image_paths_tuple = filedialog.askopenfilenames(
            title="Select images",
            filetypes=(("JPEG Files", "*.jpg;*.jpeg"), ("PNG Files", "*.png"), ("All files", "*.*"))
        )
        self.image_paths = list(image_paths_tuple)  # Convert tuple to list
        if self.image_paths:
            self.status_label.config(text=f"Selected {len(self.image_paths)} images.")
            logging.info(f"Selected {len(self.image_paths)} images for stitching.")
            self.display_selected_images()  # Display each selected image

    def delete_selected_image(self):
        if hasattr(self, 'selected_image_index') and self.selected_image_index is not None:
            # Remove the selected image from the list
            del self.image_paths[self.selected_image_index]
            del self.photo_images[self.selected_image_index]
            self.display_selected_images()  # Redisplay the images
            self.delete_button.pack_forget()  # Hide the delete button
            self.selected_image_index = None  # Reset the selected index
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
            self.current_image = Image.fromarray(stitched)  # Ensure this line is correctly updating the current_image
            self.show_image_on_canvas(stitched)
            self.status_label.config(text="Stitching completed successfully!")
            logging.info("Stitching completed successfully.")
        else:
            self.status_label.config(text="Failed to stitch images.")
            logging.error("Failed to stitch images.")

    def export_logs(self):
        """Export logs from the Text widget to a log file."""
        log_content = self.log_widget.get("1.0", tk.END)
        filepath = filedialog.asksaveasfilename(defaultextension=".log",
                                                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")])
        if filepath:
            with open(filepath, "w") as file:
                file.write(log_content)
            logging.info(f"Logs exported successfully to {filepath}")

    def show_image_on_canvas(self, img):
        self.image = Image.fromarray(img)
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.photo_image, anchor='nw')
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def zoom_image(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= factor
        self.image = self.image.resize((int(self.scale * self.image.width), int(self.scale * self.image.height)), Image.ANTIALIAS)
        self.photo_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(x, y, image=self.photo_image, anchor='center')
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

    def setup_help_tab(self):
        # Creating a frame for navigation buttons
        button_frame = ttk.Frame(self.help_tab)
        button_frame.pack(side='top', fill='x', pady=10)  # Pack the button frame at the top

        # Navigation buttons within the button frame
        self.prev_button = ttk.Button(button_frame, text="Previous", command=self.goto_previous_page)
        self.prev_button.pack(side='left', padx=10)

        self.next_button = ttk.Button(button_frame, text="Next", command=self.goto_next_page)
        self.next_button.pack(side='right', padx=10)

        # Creating a frame for the PDF canvas
        pdf_frame = ttk.Frame(self.help_tab)
        pdf_frame.pack(side='top', fill='both', expand=True)  # Ensure PDF frame fills the rest of the space

        # Creating the canvas within the frame
        self.pdf_canvas = Canvas(pdf_frame, bg='white')
        self.pdf_canvas.pack(side='top', fill='both', expand=True)
        self.pdf_canvas.bind("<Configure>", self.on_canvas_resize)

        self.load_pdf("docs_test.pdf")

        # Initial state of navigation buttons
        self.update_buttons()


    def load_pdf(self, file_path):
        self.doc = fitz.open(file_path)
        self.current_page_number = 0
        self.display_page(self.current_page_number)

    def display_page(self, page_number):
        page = self.doc.load_page(page_number)
        self.render_page(page)
        self.update_buttons()  # Update button states each time the page is changed

    def render_page(self, page):
        # Calculate scale factors based on the current canvas size
        canvas_width = self.pdf_canvas.winfo_width()
        canvas_height = self.pdf_canvas.winfo_height()

        # Get page dimensions to calculate the scaling factor
        page_rect = page.rect
        scale_x = canvas_width / page_rect.width
        scale_y = canvas_height / page_rect.height
        scale = min(scale_x, scale_y)

        # Create a matrix for the transformation and render the page
        mat = fitz.Matrix(scale, scale)
        self.page_pix = page.get_pixmap(matrix=mat)

        # Convert to a format suitable for Tkinter
        img = Image.frombytes("RGB", [self.page_pix.width, self.page_pix.height], self.page_pix.samples)
        self.photo_image = ImageTk.PhotoImage(image=img)
        self.pdf_canvas.create_image(0, 0, image=self.photo_image, anchor='nw')
        self.pdf_canvas.config(scrollregion=(0, 0, self.page_pix.width, self.page_pix.height))

    def goto_next_page(self):
        if self.current_page_number < len(self.doc) - 1:
            self.current_page_number += 1
            self.display_page(self.current_page_number)

    def goto_previous_page(self):
        if self.current_page_number > 0:
            self.current_page_number -= 1
            self.display_page(self.current_page_number)

    def update_buttons(self):
        # Enable or disable buttons based on the current page
        self.prev_button['state'] = 'normal' if self.current_page_number > 0 else 'disabled'
        self.next_button['state'] = 'normal' if self.current_page_number < len(self.doc) - 1 else 'disabled'

    def on_canvas_resize(self, event):
        if hasattr(self, 'doc'):
            self.display_page(self.current_page_number)

def main():
    root = tk.Tk()
    app = App1(root)
    root.mainloop()

if __name__ == "__main__":
    main()
