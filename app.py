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
from camera_opencv import Camera

from camera_video import Video

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)
CORS(app, supports_credentials=True)
from flask_socketio import SocketIO

socketio = SocketIO()
socketio.init_app(app)

@socketio.on('test', namespace='api')   # 监听前端发回的包头 test ,应用命名空间为 api
def test():  # 此处可添加变量，接收从前端发回来的信息
    print('触发test函数')
    socketio.emit('api', {'data': 'test_OK'}, namespace='api') # 此处 api 对应前端 sockets 的 api

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

# def gen(Video):
#     while True:
#         frame = Video.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#
# @app.route('/video_feed',methods=['POST'])
# def video_feed():
#     f = request.files['file']
#     path = './video/'
#     f.save(path + f.filename)
#     """Video streaming route. Put this in the src attribute of an img tag."""
#     return Response(gen(Video()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

def gen(camera):
    """Video streaming generator function."""
    yield b'--frame\r\n'
    while True:
        frame = camera.get_frame()
        yield b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n--frame\r\n'


@app.route('/video_feed',methods=['GET'])
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
