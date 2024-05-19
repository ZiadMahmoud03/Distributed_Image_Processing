from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)
master_url = "http://98.71.41.4:8000"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({"error": "No image file"}), 400
    file = request.files['image']
    operation = request.form.get('operation')

    if not file or not operation:
        return jsonify({"error": "Missing image or operation"}), 400

    files = {'image': (file.filename, file.stream, file.content_type)}
    data = {'operation': operation}

    try:
        response = requests.post(f"{master_url}/process", files=files, data=data)
        response_data = response.json()
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status/<task_id>', methods=['GET'])
def status(task_id):
    try:
        response = requests.get(f"{master_url}/status/{task_id}")
        response_data = response.json()
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
