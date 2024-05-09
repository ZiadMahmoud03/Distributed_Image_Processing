import threading
import time
import requests  # For communicating with the GUI
from azure.storage.queue import QueueServiceClient, QueueClient
from azure.storage.blob import BlobServiceClient
from mpi4py import MPI 
import time
import uuid
# ...  Add any other imports if needed

# Azure Queue Setup (Both queues)
connect_str = "YOUR_AZURE_STORAGE_CONNECTION_STRING"
queue_name = "imagetasks" 
processed_images_queue_name = "processedimages"

queue_service_client = QueueServiceClient.from_connection_string(conn_str=connect_str)
task_queue = queue_service_client.get_queue_client(queue_name)
processed_images_queue = queue_service_client.get_queue_client(processed_images_queue_name)

# Azure Blob Storage Setup
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
temp_container_name = "temp-images"  # For worker uploads

# MPI Setup
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

# Task Tracking (you'll need a suitable mechanism)
task_queue = {}  # Example: {task_id: (image_path, operation)}

def generate_task_id():
    timestamp = int(time.time() * 1000)
    uuid_part = str(uuid.uuid4())[:8]  # Take a few characters from the UUID
    return f"task_{timestamp}_{uuid_part}"

def process_image_request(image_file, operation):  
    # Create a unique task ID
    task_id = generate_task_id() 

    # Enqueue task
    task_queue.send_message(f"{image_file.filename},{operation}")
    task_queue[task_id] = (image_file.filename, operation)

    return task_id

def receive_results():
    while True:
        result = comm.recv(source=MPI.ANY_SOURCE) 
        task_id = result['task_id']  # Assuming the result includes this

        # Update GUI with 'complete' status for task_id
        send_status_update_to_gui(task_id, status='complete')

        # Optionally store processed image in Azure Blob Storage
        # ...

def send_status_update_to_gui(task_id, status):
    # Implementation depends on how your GUI receives updates
    pass

# ... (Rest of your code, including polling functions for GUI communication)

if rank == 0: 
    # Connect to Azure Queue 
    queue_service_client = QueueServiceClient.from_connection_string(conn_str=connect_str)
    task_queue = queue_service_client.get_queue_client(queue_name)

    # Start a thread to receive results
    results_thread = threading.Thread(target=receive_results)
    results_thread.start()

    # ... Logic for your GUI communication (status checking, etc.)

    # Signal the workers to stop (send 'None' tasks)
    for _ in range(MPI.COMM_WORLD.Get_size() - 1):
        task_queue.send_message('None')

    results_thread.join()  
