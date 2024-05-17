import threading
import cv2
import numpy as np
from mpi4py import MPI

class WorkerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()

    def run(self):
        while True:
            try:
                status, task_id, task_data = self.comm.recv(source=0, tag=MPI.ANY_TAG)
            except Exception as e:
                print(f"Worker {self.rank}: Error receiving task: {e}")
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
                self.comm.send(('failed', task_id, str(e)), dest=0)

        self.comm.Disconnect()
        MPI.Finalize()

    def process_image(self, image_path, operation):
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if operation == 'edge_detection':
            result = cv2.Canny(img, 100, 200)
        elif operation == 'color_inversion':
            result = cv2.bitwise_not(img)
        elif operation == 'gaussian_blur':
            result = cv2.GaussianBlur(img, (5, 5), 0)
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

if __name__ == "__main__":
    worker = WorkerThread()
    worker.start()
    worker.join()
