from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient, TextBase64DecodePolicy, TextBase64EncodePolicy
import cv2
import numpy as np
import json
import logging
from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "DefaultEndpointsProtocol=https;AccountName=dipqueue;AccountKey=QGNnCM1lAEqqS0G5k5vhkDo5x1eXxrrZhipISXxtFOnQy2zouzEjdL2I8uG7uUc/eVYI7weKYOBj+AStCp8Vow==;EndpointSuffix=core.windows.net")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
task_queue_client = QueueClient.from_connection_string(connection_string, "task-queue", message_decode_policy=TextBase64DecodePolicy())
processed_queue_client = QueueClient.from_connection_string(connection_string, "processed-image-queue", message_encode_policy=TextBase64EncodePolicy())
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

def upload_to_blob(blob_data, blob_name):
    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(blob_data, overwrite=True)
        logging.info(f"Uploaded processed image to blob storage: {blob_name}")
        return True
    except Exception as e:
        logging.error(f"Error uploading processed image to blob storage: {e}")
        return False

@app.route('/process', methods=['POST'])
def process_task():
    task_info = request.get_json()
    task_id = task_info['task_id']
    blob_name = task_info['blob_name']
    operation = task_info['operation']

    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_data = blob_client.download_blob().readall()
        logging.debug(f"Downloaded image data for blob: {blob_name}")

        processed_image = process_image(blob_data, operation)
        if processed_image is None:
            logging.error(f"Invalid operation: {operation}")
            return jsonify({"error": "Invalid operation"}), 400

        _, buffer = cv2.imencode('.png', processed_image)
        result_blob_name = f"{task_id}_processed.png"
        success = upload_to_blob(buffer.tobytes(), result_blob_name)
        if success:
            processed_info = {"task_id": task_id, "result_blob_name": result_blob_name}
            processed_queue_client.send_message(json.dumps(processed_info))
            logging.info(f"Processed task {task_id} added to processed queue")
            # Send the URL of the processed image to the client
            return jsonify({"result_blob_url": f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{result_blob_name}"}), 200
        else:
            return jsonify({"error": "Failed to upload processed image to blob storage"}), 500
    except Exception as e:
        logging.error(f"Error processing task {task_id}: {e}")
        return jsonify({"error": f"Error processing task {task_id}: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
