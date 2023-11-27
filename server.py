from flask import Flask, request, render_template, send_file
import cv2
import numpy as np
import io
import base64
import denoiser

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    # Get the uploaded image file
    file = request.files['file']

    if file:
        print(" [+] New image denoising request")
        image_data      = file.read()
        image_array     = denoiser.bytesToImage(image_data)
        processed_image = denoiser.denoise_image(image_array)
        image_bytes     = denoiser.imageToBytes(processed_image)
        image_encoded   = denoiser.encode_image(image_bytes)
        return image_encoded
    return 'No image provided'

if __name__ == '__main__':
    app.run(debug=True)
