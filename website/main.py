from flask import Flask, jsonify, render_template, request, redirect, url_for, send_file, send_from_directory
from werkzeug.utils import secure_filename
import os
import requests
import time
import pyrebase
import firebase_admin
from firebase_admin import storage

config ={
    "apiKey": "##",
    "authDomain": "##",
    "databaseURL": "##",
    "projectId": "##",
    "storageBucket": "##",
    "messagingSenderId": "##",
    "appId": "##",
    "measurementId": "##"
}

#storage initialization
firebase = pyrebase.initialize_app(config)
storage = firebase.storage()


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def start():
    return render_template('start.html')

@app.route('/upload', methods=['GET', 'POST'])
def started():
    return render_template('upload.html')

def get_download_url(file_path):
    dd = storage.download(file_path,"new.jpg")
    return dd

UPLOAD_FOLDER = 'uploads'
GENERATED_VIDEO_FOLDER = 'templates\gen_videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GENERATED_VIDEO_FOLDER'] = GENERATED_VIDEO_FOLDER

@app.route('/generate_video', methods=['POST', 'GET'])
def generate_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        # print(file_path)
        path_on_cloud = f"images/{filename}"
        #upload
        storage.child(path_on_cloud).put(file_path)
        generation_id = generate_video_from_image(file_path)
        print(generation_id)
        if generation_id:
            print('hii')
            return jsonify({'generation_id': generation_id}), 200
        else:
            return jsonify({'error': 'Failed to generate video'}), 501
    else:
        return jsonify({'error': 'No file provided in the request'}), 401


@app.route('/generating_video', methods=['POST','GET'])
def generate_video_from_image(image_path):
    response = requests.post(
        "https://api.stability.ai/v2beta/image-to-video",
        headers={
            "authorization": "Enter your api key here"###
        },
        files={
            "image": open(image_path, "rb")
        },
        data={
            "seed": 0,
            "cfg_scale": 1.8,
            "motion_bucket_id": 127
        },
    )
   

    if response.status_code == 200:
        print("Generation ID:", response.json().get('id'))
        generation_id = response.json().get('id')
        return generation_id
    else:
        return None


@app.route('/uploads/<filename>',methods=['POST','GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/loading/<generation_id>',methods=['POST','GET'])
def loadpage(generation_id):
    time.sleep(10)
    return redirect(url_for('display_video', generation_id=generation_id))

@app.route('/video/<generation_id>',methods=['POST','GET'])
def display_video(generation_id):
    response = requests.get(
        f"https://api.stability.ai/v2beta/image-to-video/result/{generation_id}",
        headers={
            'accept': "video/*",
            'authorization': "Enter your api key here"###
        },
    )
    if response.status_code == 202:
        print("Generation in-progress, try again in 10 seconds.")
        return render_template('loading.html', generation_id=generation_id)
    if response.status_code == 200:
        print("Generation complete!")
        os.makedirs(app.config['GENERATED_VIDEO_FOLDER'], exist_ok=True)
        video_path = os.path.join(app.config['GENERATED_VIDEO_FOLDER'], f'{generation_id}.mp4')
        with open(video_path, 'wb') as f:
            f.write(response.content)
            path_on_cloud = f'videos/{generation_id}.mp4'
            storage.child(path_on_cloud).put(video_path)
            download_url = storage.child(f'videos/{generation_id}.mp4').get_url(None)
            video_path =f'{download_url}'
        return render_template('video.html',video_path = video_path)
    else:
        return redirect(url_for('error_page'))

# @app.route('/generated_videos/<generation_id>')
# def generated_video(generation_id):
    
#     print(download_url)
#     return download_url

@app.route('/error')
def error_page():
    return render_template('error.html')

if __name__ == '__main__':
    app.run(debug=True)
