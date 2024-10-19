# pylint: skip-file
import os
import numpy as np
from flask import Flask, request, jsonify, send_file
from PIL import Image, ImageColor
import cv2
from skimage.filters import gaussian
from test import evaluate
import io

app = Flask(__name__)

def sharpen(img):
    img = img * 1.0
    gauss_out = gaussian(img, sigma=5)
    alpha = 1.5
    img_out = (img - gauss_out) * alpha + img 
    img_out = img_out / 255.0
    mask_1 = img_out < 0
    mask_2 = img_out > 1
    img_out = img_out * (1 - mask_1)
    img_out = img_out * (1 - mask_2) + mask_2
    img_out = np.clip(img_out, 0, 1)
    img_out = img_out * 255
    return np.array(img_out, dtype=np.uint8)

def lips(image, parsing, part=12, color=[230, 50, 20]):
    b, g, r = color
    tar_color = np.zeros_like(image)
    tar_color[:, :, 0] = b
    tar_color[:, :, 1] = g
    tar_color[:, :, 2] = r
    np.repeat(parsing[:, :, np.newaxis], 3, axis=2)

    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    tar_hsv = cv2.cvtColor(tar_color, cv2.COLOR_BGR2HSV)

    image_hsv[:, :, 0:1] = tar_hsv[:, :, 0:1]

    changed = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)

    changed[parsing != part] = image[parsing != part]
    return changed

def eyebrow(image, parsing, part=2, color=[230, 50, 20]):
    b, g, r = color
    tar_color = np.zeros_like(image)
    tar_color[:, :, 0] = b
    tar_color[:, :, 1] = g
    tar_color[:, :, 2] = r
    
    image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    tar_hsv = cv2.cvtColor(tar_color, cv2.COLOR_BGR2HSV)
    image_hsv[:, :, 0:1] = tar_hsv[:, :, 0:1]
    
    changed = cv2.cvtColor(image_hsv, cv2.COLOR_HSV2BGR)
    changed[parsing != part] = image[parsing != part]
    
    return changed

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files or 'lip_color' not in request.form or 'eyebrow_color' not in request.form :
        return jsonify({"error": "Faltan parámetros requeridos"}), 400

    img_file = request.files['image']
    lip_color_hex = request.form['lip_color']
    eyebrow_color_hex = request.form['eyebrow_color']

    # Convertir colores hexadecimales a RGB
    lip_color = ImageColor.getcolor(lip_color_hex, "RGB")
    eyebrow_color = ImageColor.getcolor(eyebrow_color_hex, "RGB")
    
    # Cargar la imagen
    image = np.array(Image.open(img_file))
    ori = image.copy()
    h, w, _ = ori.shape
    image = cv2.resize(image, (1024, 1024))
    
    # Evaluar la imagen para obtener el parsing
    cp = "cp/79999_iter.pth"
    parsing = evaluate(img_file, cp)
    parsing = cv2.resize(parsing, image.shape[0:2], interpolation=cv2.INTER_NEAREST)
    
    # Aplicar cambios de maquillaje solo en los labios
    part = 12  # Labio superior
    image = lips(image, parsing, part, lip_color)
    
    part = 13  # Labio inferior
    image = lips(image, parsing, part, lip_color)
    
    # Para ceja izquierda
    part = 2  # Left eyebrow
    image = eyebrow(image, parsing, part, eyebrow_color)

    # Para ceja derecha
    part = 3  # Right eyebrow
    image = eyebrow(image, parsing, part, eyebrow_color)

    image = cv2.resize(image, (w, h))

    # Convertir la imagen procesada a un objeto BytesIO para enviar en la respuesta
    output_image = Image.fromarray(image)
    img_byte_arr = io.BytesIO()
    output_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name='output_image.png')

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Cambia el puerto si es necesario