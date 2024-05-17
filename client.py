import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import time
import requests
import threading
import master_node as master

image_path = None
task_id = None
progress_label = None

def process_image(image_path, operation):
    print(f"Processing image: {image_path} with operation: {operation}")
    time.sleep(2)
    print(f"Image processing complete: {image_path}") 


def open_image():
    global image_path
    image_path = filedialog.askopenfilename()
    if image_path:
        load_image(image_path)


def load_image(image_path):
    img = Image.open(image_path)
    img = img.resize((256, 256), Image.Resampling.LANCZOS)  # Resize for display
    photo = ImageTk.PhotoImage(img)
    image_label.configure(image=photo)
    image_label.image = photo

def start_processing():
    selected_operation = operation_variable.get()
    image_path = image_label.image.filename  # Get path from loaded image
    process_image(image_path, selected_operation)


def send_processing_request():
    global task_id, image_path
    if not image_path:
        messagebox.showerror("Error", "Please select an image first.")
        return
    operation = operation_variable.get()
    try:
        task_id = master.process_image_request(image_path, operation)
        progress_label.config(text="Processing...")
        threading.Thread(target=monitor_progress, args=(task_id,)).start()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to communicate with the master node: {e}")


def monitor_progress(task_id):
    while True:
        result = master.get_result(task_id) 
        if result is not None:  # Check if result is available
            load_image(result)  # Update the image_label with the result
            progress_label.config(text="Processing complete!")  # Update the progress label
            break
        time.sleep(1) 


# Main window setup
root = tk.Tk()
root.title("Distributed Image Processing System")

# Image display area
image_label = tk.Label(root)
image_label.pack()

# Operation selection
operation_variable = tk.StringVar(root)
operation_variable.set("edge_detection")  
operation_dropdown = ttk.Combobox(root, textvariable=operation_variable, 
                                  values=["edge_detection", "color_inversion", "grayscale", 
                                          "gaussian_blur", "sharpen", "brightness_adjust"]) 
operation_dropdown.pack()

# Buttons
open_button = tk.Button(root, text="Open Image", command=open_image)
open_button.pack()
process_button = tk.Button(root, text="Process", command=send_processing_request)
process_button.pack()

root.mainloop()
