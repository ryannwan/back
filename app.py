#!/usr/bin/env python
import io
from importlib import import_module
import os

from PIL import Image
from flask import Flask, render_template, Response, request
from flask_cors import CORS


# import camera driver
from werkzeug.utils import secure_filename

import yolo_img

if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera_opencv import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/image',methods=['POST'])
def image():
    if request.method == 'POST':
        f = request.files['file']
        path ='./img'
        f.save(path+f.filename)
        img_url = yolo_img.yolo_detect(path + f.filename)
        with open(img_url, 'rb') as f:
            a = f.read()
        '''对读取的图片进行处理'''
        img_stream = io.BytesIO(a)
        img = Image.open(img_stream)

        imgByteArr = io.BytesIO()
        img.save(imgByteArr, format='PNG')
        imgByteArr = imgByteArr.getvalue()
        print(imgByteArr)
        return imgByteArr

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
