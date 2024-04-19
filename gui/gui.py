import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import cv2
import numpy as np
from imagestiching import stitch_images


class App1:
    def __init__(self, root):
        self.root = root
        self.root.title('Python Tkinter App')
        self.root.geometry('640x480')

        self.tab_group = ttk.Notebook(root)
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

        ttk.Label(self.file_tab, text="Contents of File tab").pack(pady=20, padx=20)
        ttk.Label(self.insert_tab, text="Contents of Insert tab").pack(pady=20, padx=20)
        ttk.Label(self.view_tab, text="Contents of View tab").pack(pady=20, padx=20)
        ttk.Label(self.help_tab, text="Contents of Help tab").pack(pady=20, padx=20)
        ttk.Label(self.log_tab, text="Contents of Log tab").pack(pady=20, padx=20)

        # Setup in Insert Tab for stitching images
        ttk.Button(self.insert_tab, text="Select Image 1", command=self.select_image1).pack(pady=10)
        ttk.Button(self.insert_tab, text="Select Image 2", command=self.select_image2).pack(pady=10)
        ttk.Button(self.insert_tab, text="Stitch Images", command=self.stitch_images_wrapper).pack(pady=10)

        self.img1_path = None
        self.img2_path = None

    def select_image1(self):
        self.img1_path = filedialog.askopenfilename()
        print(f"Selected image 1: {self.img1_path}")

    def select_image2(self):
        self.img2_path = filedialog.askopenfilename()
        print(f"Selected image 2: {self.img2_path}")

    def stitch_images_wrapper(self):
        if not self.img1_path or not self.img2_path:
            print("Images not selected properly")
            return

        img1 = cv2.imread(self.img1_path)
        img2 = cv2.imread(self.img2_path)
        if img1 is None or img2 is None:
            print("Error loading images")
            return

        result = stitch_images(img1, img2)
        cv2.imshow("Stitched Image", result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def main():
    root = tk.Tk()
    app = App1(root)
    root.mainloop()

if __name__ == '__main__':
    main()
