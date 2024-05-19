from flask import Flask, request, jsonify
import requests
import uuid
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from azure.storage.queue import QueueClient, TextBase64EncodePolicy
from datetime import datetime, timedelta
import os
import json
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

connection_string = "DefaultEndpointsProtocol=https;AccountName=dipqueue;AccountKey=QGNnCM1lAEqqS0G5k5vhkDo5x1eXxrrZhipISXxtFOnQy2zouzEjdL2I8uG7uUc/eVYI7weKYOBj+AStCp8Vow==;EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
task_queue_client = QueueClient.from_connection_string(connection_string, "task-queue", message_encode_policy=TextBase64EncodePolicy())
processed_queue_client = QueueClient.from_connection_string(connection_string, "processed-image-queue", message_encode_policy=TextBase64EncodePolicy())
container_name = "blob-storage"

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

    task_info = {"task_id": task_id, "blob_name": blob_name, "operation": operation}
    
    task_queue_client.send_message(json.dumps(task_info))
    logging.info(f"Sent task {task_id} to task queue")

    return jsonify({"task_id": task_id})

@app.route('/status/<task_id>', methods=['GET'])
def status(task_id):
    messages = processed_queue_client.receive_messages()
    for msg in messages:
        message = json.loads(msg.content)
        if message["task_id"] == task_id:
            processed_queue_client.delete_message(msg)
            sas_url = generate_sas_token(message["processed_blob_name"])
            return jsonify({"status": "complete", "result_blob_url": sas_url})
    return jsonify({"status": "processing"})

@app.route('/status_update', methods=['POST'])
def status_update():
    data = request.json
    processed_queue_client.send_message(json.dumps(data))
    logging.info(f"Received status update: {data}")
    return jsonify({"status": "acknowledged"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
