import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import logging
import tryouts.Ahmad.TextHandler as th


def setup_logging(text_widget):
    # Set the logger to handle and format messages
    log_handler = th.TextHandler(text_widget)
    log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(log_handler)
    return logger

def center_window(window):
        window.update_idletasks()  # Updates the window to get an accurate size
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')