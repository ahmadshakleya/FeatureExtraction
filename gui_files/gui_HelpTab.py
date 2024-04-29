import fitz  # PyMuPDF
from tkinter import ttk, filedialog, Canvas, messagebox, Scrollbar
from PIL import Image, ImageTk
import logging
import shutil
import requests

class HelpTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.pdf_path = "./docs/docs.pdf"
        self.doc = None
        self.current_page_number = 0
        self.zoom_scale = 1.0  # Default scale factor for zoom
        self.setup_ui()

    def setup_ui(self):
        logging.info("HELP - Setting up HelpTab UI components.")
        # Navigation and download buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(side='top', fill='x', pady=10)

        self.prev_button = ttk.Button(button_frame, text="Previous", command=self.goto_previous_page)
        self.prev_button.pack(side='left', padx=10)

        self.next_button = ttk.Button(button_frame, text="Next", command=self.goto_next_page)
        self.next_button.pack(side='right', padx=10)

        self.download_button = ttk.Button(button_frame, text="Save PDF", command=self.download_pdf)
        self.download_button.pack(side='right', padx=10)

        self.zoom_in_button = ttk.Button(button_frame, text="Zoom In", command=lambda: self.adjust_zoom(1.25))
        self.zoom_in_button.pack(side='left', padx=10)

        self.zoom_out_button = ttk.Button(button_frame, text="Zoom Out", command=lambda: self.adjust_zoom(0.8))
        self.zoom_out_button.pack(side='left', padx=10)

        # PDF display area with scrollbars
        pdf_frame = ttk.Frame(self)
        pdf_frame.pack(side='top', fill='both', expand=True)

        self.pdf_canvas = Canvas(pdf_frame, bg='white')
        self.v_scroll = Scrollbar(pdf_frame, orient='vertical', command=self.pdf_canvas.yview)
        self.h_scroll = Scrollbar(pdf_frame, orient='horizontal', command=self.pdf_canvas.xview)
        self.pdf_canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        self.pdf_canvas.pack(side='left', fill='both', expand=True)
        self.v_scroll.pack(side='right', fill='y')
        self.h_scroll.pack(side='bottom', fill='x')

        self.pdf_canvas.bind("<Configure>", self.on_canvas_resize)

        if not self.load_pdf(self.pdf_path):
            if messagebox.askyesno("Download PDF", "PDF not found locally. Download from the internet?"):
                self.download_pdf_from_url("https://github.com/ahmadshakleya/FeatureExtraction/raw/main/docs/docs.pdf")

    def download_pdf_from_url(self, url):
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raises HTTPError for bad responses
            with open(self.pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logging.info("HELP - PDF downloaded from the internet.")
            self.load_pdf(self.pdf_path)
            self.display_page(self.current_page_number)
        except requests.exceptions.HTTPError as e:
            logging.error(f"HELP - Failed to download PDF from {url}: {e}")
            messagebox.showerror("Download Error", "Failed to download the PDF.")
        except requests.exceptions.RequestException as e:
            logging.error(f"HELP - Failed to download PDF from {url}: {e}")
            messagebox.showerror("Download Error", "Failed to download the PDF.")
        except Exception as e:
            logging.error(f"HELP - Failed to download PDF from {url}: {e}")
            messagebox.showerror("Download Error", "Failed to download the PDF.")

    def adjust_zoom(self, factor):
        self.zoom_scale *= factor
        logging.info(f"HELP - Adjusting zoom to {self.zoom_scale}")
        self.display_page(self.current_page_number)

    def download_pdf(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if filepath:
            shutil.copy(self.pdf_path, filepath)
            messagebox.showinfo("Download Successful", f"The PDF has been saved to {filepath}")
            logging.info(f"HELP - PDF successfully downloaded to {filepath}.")
        else:
            logging.info("HELP - PDF download cancelled.")

    def load_pdf(self, file_path):
        try:
            self.doc = fitz.open(file_path)
            return True
        except Exception as e:
            logging.error(f"HELP - Error loading PDF file: {file_path}, {e}")
            return False

    def display_page(self, page_number):
        if self.doc:
            page = self.doc.load_page(page_number)
            self.render_page(page)

    def render_page(self, page):
        canvas_width = self.pdf_canvas.winfo_width()
        canvas_height = self.pdf_canvas.winfo_height()

        page_rect = page.rect
        scale_x = canvas_width / page_rect.width * self.zoom_scale
        scale_y = canvas_height / page_rect.height * self.zoom_scale
        scale = min(scale_x, scale_y)

        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        photo_image = ImageTk.PhotoImage(image=img)
        
        # Clear the previous image
        self.pdf_canvas.delete("all")  # This will remove all items from the canvas including images
        # Create a new image centered properly
        image_id = self.pdf_canvas.create_image(canvas_width // 2, canvas_height // 2, image=photo_image, anchor='center')

        self.pdf_canvas.image = photo_image  # Keep a reference to avoid garbage collection
        # Update scroll region to new image size
        self.pdf_canvas.config(scrollregion=(0, 0, pix.width * self.zoom_scale, pix.height * self.zoom_scale))


    def goto_next_page(self):
        if self.current_page_number < len(self.doc) - 1:
            self.current_page_number += 1
            self.display_page(self.current_page_number)

    def goto_previous_page(self):
        if self.current_page_number > 0:
            self.current_page_number -= 1
            self.display_page(self.current_page_number)

    def on_canvas_resize(self, event):
        if self.doc:
            self.display_page(self.current_page_number)
