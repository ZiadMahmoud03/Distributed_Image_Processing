import threading
import cv2
import numpy as np
from mpi4py import MPI

class WorkerThread(threading.Thread):
    def __init__(self, result_queue):
        threading.Thread.__init__(self)
        self.result_queue = result_queue
        self.comm = MPI.COMM_WORLD   # Initialize comm here, as an instance variable
        self.rank = self.comm.Get_rank()

    def run(self):
        while True:
            try:
                status, task_id, task_data = self.comm.recv(source=0, tag=MPI.ANY_TAG)
            except Exception as e:
                print(f"Worker {self.rank}: Error receiving task: {e}")
                # Log the error for further analysis
                # Potentially re-attempt communication with the master
                continue 

            if status == 'done':
                print(f"Worker {self.rank} finished.")
                break

            image_path, operation = task_data

            try:
                result = self.process_image(image_path, operation)
                self.comm.send(('complete', task_id, result), dest=0)
            except Exception as e:
                print(f"Worker {self.rank}: Error processing or sending result for task {task_id}: {e}")
                self.comm.send(('failed', task_id, str(e)), dest=0)  # Send error details to master
                
        # Close MPI communication (optional)
        self.comm.Disconnect()

    def process_image(self, image, operation):
        # Load the image
        img = cv2.imread(image, cv2.IMREAD_COLOR)

        # Perform the specified operation
        if operation == 'edge_detection':
            result = cv2.Canny(img, 100, 200)
        elif operation == 'color_inversion':
            result = cv2.bitwise_not(img)
        elif operation == 'gaussian_blur':
            result = cv2.GaussianBlur(img, (5, 5), 0)  # Kernel size (5, 5) is common
        elif operation == 'sharpen':
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            result = cv2.filter2D(img, -1, kernel)
        elif operation == 'grayscale':
            result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif operation == 'brightness_adjust':
            result = cv2.convertScaleAbs(img, alpha=1.0, beta=50)
        else:
            result = "Invalid operation"
        return result
    
    def receive_results():
        while True:
            status, task_id, result = comm.recv(source=MPI.ANY_SOURCE) 
            if status == 'complete':
                # Handle successful image processing (e.g., update GUI)
                send_status_update_to_gui(task_id, status='complete', result=result)
            elif status == 'failed':
                # Handle the case where the image processing failed
                print(f"Image processing for task {task_id} failed")


