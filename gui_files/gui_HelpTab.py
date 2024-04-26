import fitz
from tkinter import ttk
from tkinter import Canvas
from PIL import Image, ImageTk


class HelpTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.pdf_path = "docs_test.pdf"
        self.doc = None
        self.current_page_number = 0
        self.setup_ui()

    def setup_ui(self):
        # Navigation buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(side='top', fill='x', pady=10)

        self.prev_button = ttk.Button(button_frame, text="Previous", command=self.goto_previous_page)
        self.prev_button.pack(side='left', padx=10)

        self.next_button = ttk.Button(button_frame, text="Next", command=self.goto_next_page)
        self.next_button.pack(side='right', padx=10)

        # PDF display area
        pdf_frame = ttk.Frame(self)
        pdf_frame.pack(side='top', fill='both', expand=True)

        self.pdf_canvas = Canvas(pdf_frame, bg='white')
        self.pdf_canvas.pack(side='top', fill='both', expand=True)
        self.pdf_canvas.bind("<Configure>", self.on_canvas_resize)

        self.load_pdf(self.pdf_path)
        self.display_page(self.current_page_number)  # Display the first page

    def load_pdf(self, file_path):
        self.doc = fitz.open(file_path)

    def display_page(self, page_number):
        if self.doc:
            page = self.doc.load_page(page_number)
            self.render_page(page)

    def render_page(self, page):
        canvas_width = self.pdf_canvas.winfo_width()
        canvas_height = self.pdf_canvas.winfo_height()

        page_rect = page.rect
        scale_x = canvas_width / page_rect.width
        scale_y = canvas_height / page_rect.height
        scale = min(scale_x, scale_y)

        mat = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=mat)

        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        photo_image = ImageTk.PhotoImage(image=img)
        self.pdf_canvas.create_image(0, 0, image=photo_image, anchor='nw')
        self.pdf_canvas.image = photo_image  # Keep a reference!
        self.pdf_canvas.config(scrollregion=(0, 0, pix.width, pix.height))

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

    def update_buttons(self):
        self.prev_button['state'] = 'normal' if self.current_page_number > 0 else 'disabled'
        self.next_button['state'] = 'normal' if self.current_page_number < len(self.doc) - 1 else 'disabled'