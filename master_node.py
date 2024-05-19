from flask import Flask, request, jsonify
import requests
import uuid
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.storage.queue import QueueClient, TextBase64EncodePolicy
from datetime import datetime, timedelta
import os
import json
import logging
import threading

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Azure configuration
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "DefaultEndpointsProtocol=https;AccountName=dipqueue;AccountKey=QGNnCM1lAEqqS0G5k5vhkDo5x1eXxrrZhipISXxtFOnQy2zouzEjdL2I8uG7uUc/eVYI7weKYOBj+AStCp8Vow==;EndpointSuffix=core.windows.net")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
task_queue_client = QueueClient.from_connection_string(connection_string, "task-queue", message_encode_policy=TextBase64EncodePolicy())
processed_queue_client = QueueClient.from_connection_string(connection_string, "processed-image-queue", message_encode_policy=TextBase64EncodePolicy())
container_name = "blob-storage"

# List of worker endpoints
worker_endpoints = [
    "http://10.0.0.7:7000",
    "http://10.0.0.6:7000",
    "http://10.0.0.5:7000"
]
worker_index = 0
worker_lock = threading.Lock()

def get_next_worker_endpoint():
    global worker_index
    with worker_lock:
        endpoint = worker_endpoints[worker_index]
        worker_index = (worker_index + 1) % len(worker_endpoints)
    return endpoint

def generate_sas_token(blob_name):
    sas_token = generate_blob_sas(
        account_name=blob_service_client.account_name,
        container_name=container_name,
        blob_name=blob_name,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    return f"https://{blob_service_client.account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"

@app.route('/process', methods=['POST'])
def process():
    file = request.files['image']
    operation = request.form.get('operation')

    if not file or not operation:
        return jsonify({"error": "Missing image or operation"}), 400

    task_id = str(uuid.uuid4())
    blob_name = f"{task_id}.png"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(file.read(), overwrite=True)
    logging.info(f"Uploaded image to blob storage: {blob_name}")

    task_info = {"task_id": task_id, "blob_name": blob_name, "operation": operation}

    try:
        task_queue_client.send_message(json.dumps(task_info))
        logging.info(f"Task {task_id} added to task queue")

        worker_endpoint = get_next_worker_endpoint()
        response = requests.post(f"{worker_endpoint}/process", json=task_info)
        response.raise_for_status()
        logging.info(f"Task {task_id} sent to worker {worker_endpoint}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send task {task_id} to worker: {e}")
        return jsonify({"error": f"Failed to send task to worker: {e}"}), 500

    return jsonify({"task_id": task_id, "status": "processing"})

@app.route('/result/<task_id>', methods=['GET'])
def get_result(task_id):
    try:
        # Retrieve messages from the processed queue
        messages = processed_queue_client.receive_messages()
        if not messages:
            logging.info(f"No messages found in the processed queue for task {task_id}")
            return jsonify({"task_id": task_id, "status": "not ready"}), 404

        for message in messages:
            message_content = message.content
            logging.debug(f"Received message content: {message_content}")
            try:
                message_data = json.loads(message_content)
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON for task {task_id}: {e}")
                continue

            if message_data['task_id'] == task_id:
                # Delete the message from the queue
                processed_queue_client.delete_message(message)
                result_blob_url = generate_sas_token(message_data['result_blob_name'])
                return jsonify({"task_id": task_id, "result_blob_url": result_blob_url})
        
        logging.info(f"No matching messages found in the processed queue for task {task_id}")
    except Exception as e:
        logging.error(f"Error retrieving result for task {task_id}: {e}")
        return jsonify({"error": "Could not retrieve result"}), 500

    return jsonify({"task_id": task_id, "status": "not ready"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
