import threading
import time
import requests  # For communicating with the GUI
from azure.storage.queue import QueueServiceClient, QueueClient
from azure.storage.blob import BlobServiceClient
from mpi4py import MPI 
import time
import uuid
import worker_thread as wt


# Azure Queue Setup (Both queues)
connect_str = "DefaultEndpointsProtocol=https;AccountName=dipqueue;AccountKey=QGNnCM1lAEqqS0G5k5vhkDo5x1eXxrrZhipISXxtFOnQy2zouzEjdL2I8uG7uUc/eVYI7weKYOBj+AStCp8Vow==;EndpointSuffix=core.windows.net"
queue_name = "task_queue" 
processed_images_queue_name = "processed-image-queue"  

queue_service_client = QueueServiceClient.from_connection_string(conn_str=connect_str)
task_queue = queue_service_client.get_queue_client(queue_name)
processed_images_queue = queue_service_client.get_queue_client(processed_images_queue_name)

# Azure Blob Storage Setup
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
temp_container_name = "blob-storage"  # For worker uploads

# MPI Setup (Initialization moved to the master node)
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Task Tracking & Synchronization
task_lock = threading.Lock()
task_queue = {}  # Example: {task_id: (image_path, operation)}

def generate_task_id():
    return int(time.time() * 1000)

def process_image_request(image_file, operation):
    task_id = generate_task_id()
    task_queue[task_id] = (image_file, operation)  # Track the task

    # Distribute to an available worker
    for i in range(1, size):
        comm.send((task_id, image_file.filename, operation), dest=i)  
    return task_id

def receive_results():
    while True:
        status, task_id, result = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG) 
        if status == 'complete':
            print(f"Received result for task {task_id}: {result}")
        elif status == 'failed':
            print(f"Task {task_id} failed on worker.")
        elif status == 'done':  # Worker finished all tasks
            break

 
def send_status_update_to_gui(task_id, status, image_path, result=None):  # Include image_path
    print(f"Image processing complete: {image_path}")

if rank == 0:
    # Start a thread to receive results
    results_thread = threading.Thread(target=receive_results)
    results_thread.start()

    # ... Logic for your GUI communication (status checking, etc.)

    # Signal the workers to stop after processing all tasks
    for _ in range(1, size):
        comm.send(('done', None, None), dest=i)  # Send 'done' message
    results_thread.join()

# Worker Nodes (Code running on each VM)
if rank != 0:
    worker = wt.WorkerThread()
    worker.start()
