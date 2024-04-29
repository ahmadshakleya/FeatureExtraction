import tkinter as tk
from tkinter import ttk
import logging
import tryouts.Ahmad.MultipleImageStitch as mis  # Importing your module
import tryouts.Ahmad.TextHandler as th  # Importing your module
from tryouts.Ken.FeatureDetectionFunction import process_image_with_keypoints

# Importing the required modules
from gui_files.gui_ViewTab import ViewTab
from gui_files.gui_FileTab import FileTab
from gui_files.gui_HelpTab import HelpTab
from gui_files.gui_LogTab import LogTab
from gui_files.gui_utils import center_window
from gui_files.gui_splashscreen import SplashScreen
from gui_files.gui_EditTab import EditTab

class ImageStitchingApp:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()  # Hide main window during splash screen
        self.splash = SplashScreen(self.root, self.initialize_ui)

    def initialize_ui(self): 
        """Initialize the main window UI after the splash screen closes."""
        self.root.deiconify()  # Show the main window
        self.root.title('Image Stitching App')
        self.root.geometry('600x400')
        center_window(self.root)  # Center the main window

        self.tab_group = ttk.Notebook(self.root)
        self.tab_group.pack(expand=1, fill="both")

        self.view_tab = ViewTab(self.tab_group)
        self.insert_tab = FileTab(self.tab_group, self.view_tab)
        self.help_tab = HelpTab(self.tab_group)
        self.log_tab = LogTab(self.tab_group)
        self.edit_tab = EditTab(self.tab_group)

        self.tab_group.add(self.insert_tab, text='File')
        self.tab_group.add(self.edit_tab, text='Edit')
        self.tab_group.add(self.view_tab, text='View')
        self.tab_group.add(self.help_tab, text='Help')
        self.tab_group.add(self.log_tab, text='Log')

        logging.info("Application started")  # Log the start of the application

def main():
    root = tk.Tk()
    app = ImageStitchingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
