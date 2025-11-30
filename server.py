from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
from pyzbar import pyzbar
import base64
import os

app = Flask(__name__)
CORS(app)

def decode_barcode(image):
    """
    Decode barcodes from an image.
    Returns the first barcode found or None.
    """
    # Detect and decode barcodes
    barcodes = pyzbar.decode(image)
    
    if barcodes:
        # Return the first barcode found
        barcode = barcodes[0]
        barcode_data = barcode.data.decode('utf-8')
        barcode_type = barcode.type
        return {
            'data': barcode_data,
            'type': barcode_type,
            'found': True
        }
    
    return {'found': False}

@app.route('/')
def index():
    """Serve the HTML client page"""
    return send_from_directory('.', 'index.html')

@app.route('/scan', methods=['POST'])
def scan_barcode():
    """
    Endpoint to receive video frames and scan for barcodes.
    Expects base64 encoded image data in JSON format.
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
        image_bytes = base64.b64decode(image_data)
        
        # Convert to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # Decode image
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Convert to grayscale for better barcode detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Scan for barcode
        result = decode_barcode(gray)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5555))
    print("🚀 Barcode Scanner Service starting...")
    print(f"📷 Server will be available at http://localhost:{port}")
    print("🔍 Ready to scan barcodes!")
    app.run(host='0.0.0.0', port=port, debug=True)
