from mpi4py import MPI
import queue
from google.cloud import pubsub_v1
import json

# Function to distribute tasks to worker threads
def distribute_tasks(task_queue, image_list, operation_list):
    num_workers = MPI.COMM_WORLD.Get_size() - 1

    for i, (image, operation) in enumerate(zip(image_list, operation_list)):
        worker_rank = (i % num_workers) + 1
        task_queue.put((image, operation), worker_rank)

    # Send termination signals to worker threads
    for _ in range(num_workers):
        task_queue.put(None)

# Function to collect results from worker threads
def collect_results(task_queue, num_tasks):
    results = []
    for _ in range(num_tasks):
        result = MPI.COMM_WORLD.recv(source=MPI.ANY_SOURCE)
        results.append(result)
    return results

def callback(message):
    data = json.loads(message.data.decode("utf-8"))
    image = data["image"]
    operation = data["operation"]
    task_queue.put((image, operation))
    message.ack()

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:  # Master node
        # Sample image and operation lists
        image_list = ['image1.jpg', 'image2.jpg', 'image3.jpg']
        operation_list = ['edge_detection', 'color_inversion', 'edge_detection']
        
        # Create a queue for tasks
        task_queue = queue.Queue()

        # Distribute tasks to worker threads
        distribute_tasks(task_queue, image_list, operation_list)

        # Create a Pub/Sub subscriber client
        subscriber = pubsub_v1.SubscriberClient()

        # Define subscription path
        subscription_path = subscriber.subscription_path(
            "<your-project-id>", "<your-subscription-id>"
        )

        # Subscribe to the Pub/Sub topic
        subscriber.subscribe(subscription_path, callback=callback)

        # Collect results from worker threads
        results = collect_results(task_queue, len(image_list))
        
        # Process results as needed
        for result in results:
            # Do something with the results
            pass

    else:  # Worker nodes
        # Create a Pub/Sub publisher client
        publisher = pubsub_v1.PublisherClient()

        # Define topic path
        topic_path = publisher.topic_path(
            "<your-project-id>", "<your-topic-id>"
        )

        # Publish task messages to Pub/Sub topic
        for image, operation in zip(image_list, operation_list):
            data = {"image": image, "operation": operation}
            data = json.dumps(data).encode("utf-8")
            future = publisher.publish(topic_path, data)

        # Run worker thread
        while True:
            task = comm.recv(source=0)
            if task is None:
                break
            image, operation = task
            # Process the task (this should be similar to what the worker thread does)
