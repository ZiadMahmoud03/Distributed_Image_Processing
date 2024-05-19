from flask import Flask, request, jsonify, render_template, send_file
import requests
import os
import threading
import queue

app = Flask(__name__)
master_url = "http://98.71.41.4:8000"
local_queue = queue.Queue()
processing_thread = None

def process_queue():
    while True:
        task_info = local_queue.get()
        if task_info is None:
            break
        files = {'image': (task_info['filename'], task_info['file'], task_info['content_type'])}
        data = {'operation': task_info['operation']}
        try:
            response = requests.post(f"{master_url}/process", files=files, data=data)
            response_data = response.json()
            print(f"Task processed: {response_data}")
        except Exception as e:
            print(f"Error processing task: {str(e)}")
        local_queue.task_done()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({"error": "No image file"}), 400
    files = request.files.getlist('image')
    operation = request.form.get('operation')

    if not files or not operation:
        return jsonify({"error": "Missing image or operation"}), 400

    for file in files:
        task_info = {
            'filename': file.filename,
            'file': file.stream.read(),
            'content_type': file.content_type,
            'operation': operation
        }
        local_queue.put(task_info)
    
    global processing_thread
    if processing_thread is None or not processing_thread.is_alive():
        processing_thread = threading.Thread(target=process_queue)
        processing_thread.start()
    
    return jsonify({"status": "Images uploaded and being processed"}), 202

@app.route('/status/<task_id>', methods=['GET'])
def status(task_id):
    try:
        response = requests.get(f"{master_url}/result/{task_id}")
        response_data = response.json()
        if response_data.get('result_blob_url'):
            download_url = response_data['result_blob_url']
            return send_file(download_url, as_attachment=True)
        elif response_data['status'] == 'not ready':
            return jsonify({"status": "not ready"}), 200
        else:
            return jsonify({"error": response_data['error']}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
