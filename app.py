from flask import Flask, request, jsonify, render_template, send_file
import io
import cv2
from ultralytics import YOLO
from util import predict_and_detect, analyse_thread
from PIL import Image, ImageOps
import os
import json
import threading
import io
import base64
import numpy as np

device = "mps"

app = Flask(__name__)
yolo_model = YOLO('models/yolo.pt', verbose=False).to(device)

tasks = {0: {"state": "SUCCESS"}}
results = {0: {"state": "SUCCESS"}}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyse', methods=['POST'])
def submit():
    file_storage = request.files['image']
    nparr = np.fromstring(file_storage.read(), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(frame)
    task_id = max(tasks.keys()) + 1
    path = f'static/img/{task_id}_original.jpg'
    image.save(path)
    tasks[task_id] = {'state': 'PENDING', 'image': path}
    return jsonify({'task_id': task_id})

@app.route('/analyse/<int:task_id>', methods=['GET'])
def analyse_id(task_id):
    if task_id in list(results.keys()):
        return jsonify({'result': results[task_id]['state']})
    else:
        return render_template('loading.html', task_id=task_id, show_error=False)
    
@app.route('/results/<int:task_id>', methods=['GET'])
def result_id(task_id):
    original_image_path = tasks[task_id]['image']
    return render_template('results.html', task_id=task_id, original_image_path=original_image_path)

@app.route('/results/<int:task_id>/heatmap', methods=['GET'])
def heatmap_id(task_id):
    yolo_images = results[task_id]['images']
    heatmaps = []
    for heatmap, classification, sizes in yolo_images:
        img_byte_arr = io.BytesIO()
        heatmap.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        heatmaps.append({'classification': classification, 'heatmap': base64.b64encode(img_byte_arr.getvalue()).decode('utf-8'), 'score': sizes})
    return jsonify({'heatmaps': heatmaps})

@app.route('/yolo', methods=['POST'])
def status():
    file_storage = request.files['frame']
    nparr = np.fromstring(file_storage.read(), np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img, _, _, _ = predict_and_detect(yolo_model, frame)
    image = Image.fromarray(np.array(img, dtype=np.uint8))
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)
    return send_file(img_byte_arr, mimetype='image/jpeg')

if __name__ == '__main__':
    thread = threading.Thread(target=analyse_thread, args=('models/yolo.pt', 'models/best.pt', 'conv3', tasks, results, device), daemon=True)
    thread.start()
    app.run(debug=True)
