# pylint: skip-file
from flask import Blueprint, request, jsonify, send_file
from app.services.image_service import process_image_logic
import io

bp = Blueprint('image_controller', __name__)

@bp.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files or 'lip_color' not in request.form:
        return jsonify({"error": "Faltan parámetros requeridos"}), 400

    img_file = request.files['image']
    lip_color_hex = request.form['lip_color']
    
    processed_image = process_image_logic(img_file, lip_color_hex)

    img_byte_arr = io.BytesIO()
    processed_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name='output_image.png')