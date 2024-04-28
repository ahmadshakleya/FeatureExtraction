import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

def load_images(sizes):
    # Load and resize images dynamically based on the input size
    image_paths = ["images/1.jpg", "authors/2.jpg", "authors/3.jpg"]
    images = []
    for path in image_paths:
        img = Image.open(path)
        img = img.resize((sizes, sizes))  # Resize images dynamically
        images.append(ImageTk.PhotoImage(img))
    return images

def update_progress():
    progress['value'] += 1
    if progress['value'] >= 100:
        root.destroy()  # Close the splash screen when loading is complete
    else:
        root.after(500, update_progress)  # Update the progress bar every 500ms

def resize_images(event):
    # Resize images based on the window size
    new_size = int(min(root.winfo_width(), root.winfo_height()) / 3)
    resized_images = load_images(new_size)
    for i, label in enumerate(image_labels):
        label.configure(image=resized_images[i])
        label.image = resized_images[i]  # Update image reference

root = tk.Tk()
root.title("Splash Screen Example")
root.geometry("600x400")

# Initial load of images with a default size
initial_size = 200
images = load_images(initial_size)

# Use grid layout for better control during resize
image_frame = tk.Frame(root)
image_frame.pack(expand=True, fill=tk.BOTH, pady=1)

image_labels = []
for i, image in enumerate(images):
    frame = tk.Frame(image_frame)
    frame.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
    label_image = tk.Label(frame, image=image)
    label_image.image = image  # Keep a reference to avoid garbage collection
    label_image.pack(expand=True)
    if i == 0:
        label_text = tk.Label(frame, text="Toon Smets")
    elif i == 1:
        label_text = tk.Label(frame, text="Ahmad Shakleya")
    elif i == 2:
        label_text = tk.Label(frame, text="Ken Van Laer")
    label_text.pack()
    image_labels.append(label_image)

# Configure column weights to make frames resizable
image_frame.grid_columnconfigure(0, weight=1)
image_frame.grid_columnconfigure(1, weight=1)
image_frame.grid_columnconfigure(2, weight=1)

# Progress bar below the images
progress = ttk.Progressbar(root, orient='horizontal', mode='determinate')
progress.pack(side=tk.BOTTOM, fill=tk.X, expand=True, pady=20)

# Initialize progress bar update
update_progress()

# Bind the resize event
root.bind('<Configure>', resize_images)

root.mainloop()
