from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient, TextBase64DecodePolicy, TextBase64EncodePolicy
import cv2
import numpy as np
import json
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Azure configurations
connection_string = "DefaultEndpointsProtocol=https;AccountName=dipqueue;AccountKey=QGNnCM1lAEqqS0G5k5vhkDo5x1eXxrrZhipISXxtFOnQy2zouzEjdL2I8uG7uUc/eVYI7weKYOBj+AStCp8Vow==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
task_queue_client = QueueClient.from_connection_string(connection_string, "task-queue", message_decode_policy=TextBase64DecodePolicy())
container_name = "blob-storage"

def process_image(image_data, operation):
    img = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    if operation == 'edge_detection':
        result = cv2.Canny(img, 100, 200)
    elif operation == 'color_inversion':
        result = cv2.bitwise_not(img)
    elif operation == 'gaussian_blur':
        result = cv2.GaussianBlur(img, (5, 5), 0)
    elif operation == 'sharpen':
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        result = cv2.filter2D(img, -1, kernel)
    elif operation == 'grayscale':
        result = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif operation == 'brightness_adjust':
        result = cv2.convertScaleAbs(img, alpha=1.0, beta=50)
    else:
        return None
    return result

@app.route('/process', methods=['POST'])
def process():
    task_info = request.json
    task_id = task_info["task_id"]
    blob_name = task_info["blob_name"]
    operation = task_info["operation"]

    logging.debug(f"Received task: {task_info}")

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    image_data = blob_client.download_blob().readall()
    logging.debug(f"Downloaded image from blob storage: {blob_name}")

    result = process_image(image_data, operation)
    if result is None:
        return jsonify({"error": "Invalid operation"}), 400

    _, buffer = cv2.imencode('.png', result)
    result_blob_name = f"processed_{task_id}.png"
    result_blob_client = blob_service_client.get_blob_client(container=container_name, blob=result_blob_name)
    result_blob_client.upload_blob(buffer.tobytes(), overwrite=True)
    logging.debug(f"Uploaded processed image to blob storage: {result_blob_name}")

    finished_message = {"task_id": task_id, "processed_blob_name": result_blob_name}
    master_node_url = "http://98.71.41.4:8000/status_update"  # Update with actual master node IP
    try:
        response = requests.post(master_node_url, json=finished_message)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to notify master node: {e}")
        return jsonify({"error": "Failed to notify master node"}), 500

    return jsonify({"status": "complete"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)

def poll_task_queue():
    while True:
        messages = task_queue_client.receive_messages()
        for msg in messages:
            task_info = json.loads(msg.content)
            task_queue_client.delete_message(msg)
            response = requests.post('http://localhost:7000/process', json=task_info)
            if response.status_code != 200:
                logging.error(f"Failed to process task: {task_info}")
        time.sleep(5)

if __name__ == '__main__':
    import threading
    threading.Thread(target=poll_task_queue, daemon=True).start()
    app.run(debug=True, host='0.0.0.0', port=7000)
