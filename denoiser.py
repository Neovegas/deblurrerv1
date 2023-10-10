import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model
from scipy.signal import hann
from skimage.io import imread
from skimage.transform import resize
from sklearn.model_selection import train_test_split
import cv2
import io
from PIL import Image
import base64

model = load_model("model.keras")

def imageToBytes(img):
    image = Image.fromarray((img*255).astype(np.uint8) )
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes = image_bytes.getvalue()
    return image_bytes

def bytesToImage(bytes_img):
    image = Image.open(io.BytesIO(bytes_img))
    image_array = np.array(image).astype(np.float32)/255
    return image_array

def process_bytes(bytes_img):
    image_array_rgb = bytesToImage(bytes_img)
    image_array_rgb  = denoiser.denoise_image( image_array_rgb  , iteration=1)
    return imageToBytes(image_array_rgb )

def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')


def denoise_chunks(chunks, model):
    denoised_chunks = model.predict(chunks, verbose=0)
    denoised_chunks = np.clip(0, 1, denoised_chunks)
    return denoised_chunks

def image_to_chunks(input_image, chunk_size, overlap):
    # Get the dimensions of the input image
    height, width, channels = input_image.shape

    # Create a list to store chunks
    chunks = []

    # Calculate the step size for overlapping chunks
    step = chunk_size - overlap

    for y in range(0, height, step):
        for x in range(0, width, step):
            # Extract a chunk from the input image
            chunk = input_image[y:y+chunk_size, x:x+chunk_size].copy()

            # Check if the chunk size is less than 64x64 and pad it with zeros if needed
            if chunk.shape[0] < chunk_size or chunk.shape[1] < chunk_size:
                padded_chunk = np.zeros((chunk_size, chunk_size, channels), dtype=np.uint8)
                padded_chunk[:chunk.shape[0], :chunk.shape[1]] = chunk
                chunk = padded_chunk

            chunks.append(chunk)

    return np.array(chunks) 

def chunks_to_image(denoised_chunks, input_image, chunk_size, overlap):
    # Get the dimensions of the input image
    height, width, channels = input_image.shape



    # Reconstruct the denoised image
    output_image = np.zeros((height + (chunk_size- height//chunk_size) + overlap, width+ (chunk_size-width//chunk_size) + overlap, 3), dtype=np.float32)
    index = 0

    # Calculate the step size for overlapping chunks
    step = chunk_size - overlap

    for y in range(0, height, step):
        for x in range(0, width, step):

            chunk = denoised_chunks[index]

            # Apply Hanning window to the chunk during reconstruction for each channel
            hann_window = hann(chunk_size)
            for c in range(channels):
                chunk[:, :, c] = (chunk[:, :, c].astype(np.float32)) * hann_window[:, np.newaxis] * hann_window[np.newaxis, :]

            output_image[y:y+chunk_size, x:x+chunk_size, :] += chunk
            index += 1
    
    return output_image[0:input_image.shape[0],0:input_image.shape[1]]


def denoise_image(input_image, iteration=1):

    #Extracting chunks
    chunk_size = 128
    overlap = chunk_size//2
    temp_image = input_image

    for _ in range(iteration):
        padded_image =  np.pad(temp_image.astype(np.float32), [(chunk_size,chunk_size), (chunk_size,chunk_size), (0,0)], mode='constant')
        chunks = image_to_chunks(padded_image , chunk_size=chunk_size , overlap=overlap)
        chunks = denoise_chunks(chunks, model)
        padded_image = chunks_to_image(chunks, padded_image , chunk_size=chunk_size , overlap=overlap)
        temp_image = padded_image[chunk_size:-chunk_size,chunk_size:-chunk_size ]
    

    output_image = np.clip(0, 1,temp_image)



    
    return output_image

