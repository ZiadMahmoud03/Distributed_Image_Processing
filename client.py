import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk  
import time
import requests
import master_node as master



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
    global task_id, image_path  # Access global task_id and image_path

    # Make sure an image is loaded before proceeding
    if image_path is None:
        tk.messagebox.showerror("Error", "Please select an image first.")
        return

    operation = operation_variable.get()

    task_id = master.process_image_request(image_path, operation)
    print(f"Task added with ID: {task_id}")

    # You can directly call the load_image function from the master node after processing is complete
    master.send_status_update_to_gui(task_id, status='complete', result=master.process_image(image_path, operation)) 




# def send_processing_request():
#     image_path = image_label.image.filename
#     operation = operation_variable.get()

#     api_url = 'http://master_node_ip/process_image' 

#     try:
#         files = {'image': open(image_path, 'rb')}
#         data = {'operation': operation}
#         response = requests.post(api_url, files=files, data=data)

#         if response.status_code == 200:
#             print("Processing successful!")
#             result = response.json()  #
#             tk.messagebox.showinfo("Result", result) 
#         else:
#             print("An error occurred.")
#             tk.messagebox.showerror("Error", "Processing failed.")

#     except requests.exceptions.RequestException as e:
#         print(f"Communication error: {e}")
#         tk.messagebox.showerror("Error", "Connection to server failed.")


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
