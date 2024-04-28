import tryouts.Ahmad.TextHandler as th
import logging
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, scrolledtext


class LogTab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.pack(fill='both', expand=True)
        self.create_widgets()
        self.setup_logging()

    def create_widgets(self):
        # Text widget for log messages
        self.log_widget = scrolledtext.ScrolledText(self, state='disabled')
        self.log_widget.pack(fill="both", expand=True)

        # Button to export log content
        self.export_button = ttk.Button(self, text="Export Logs", command=self.export_logs)
        self.export_button.pack(pady=10)

    def setup_logging(self):
        text_handler = th.TextHandler(self.log_widget)
        text_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(text_handler)  # This ensures your handler is added directly to the root logger

    def export_logs(self):
        """Export logs from the Text widget to a log file."""
        log_content = self.log_widget.get("1.0", tk.END)
        filepath = filedialog.asksaveasfilename(defaultextension=".log",
                                                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")])
        if filepath:
            with open(filepath, "w") as file:
                file.write(log_content)
            logging.info(f"Logs exported successfully to {filepath}")