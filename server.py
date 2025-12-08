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
            'success': True
        }
    
    return {'success': False}

@app.route('/')
def index():
    """Serve the HTML client page"""
    return send_from_directory('.', 'index.html')

@app.route('/scan', methods=['POST'])
def scan_barcode():
    """
    Endpoint to receive video frames and scan for barcodes.
    Expects base64 encoded image data in JSON format.
    Optional 'redirect' parameter: if true, redirects to configured URL with barcode.
    """
    try:
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Check if redirect is requested
        should_redirect = data.get('redirect', False)
        
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
        
        # Apply image preprocessing to improve barcode detection
        # This is especially helpful for low-quality desktop cameras
        
        # 1. Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 2. Apply adaptive thresholding to handle varying lighting conditions
        adaptive_thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # 3. Apply sharpening to enhance edges
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(gray, -1, kernel)
        
        # Try multiple preprocessing approaches
        images_to_scan = [
            ('original', image),
            ('gray', gray),
            ('blurred', blurred),
            ('adaptive_thresh', adaptive_thresh),
            ('sharpened', sharpened)
        ]
        
        # Save image copies if configured
        images_location = os.getenv('IMAGES_LOCATION_COPY')
        if images_location:
            try:
                import datetime
                os.makedirs(images_location, exist_ok=True)
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                
                cnt = 1
                for img_type, img in images_to_scan:
                    filename = f'scan_{timestamp}_{cnt}_{img_type}.jpg'
                    filepath = os.path.join(images_location, filename)
                    cv2.imwrite(filepath, img)
                    cnt += 1
            except Exception as e:
                # Log error but don't fail the request
                print(f"Warning: Failed to save image copy: {e}")
        
        # Scan for barcode using multiple preprocessing methods
        result = {'success': False}
        for img_type, processed_image in images_to_scan[1:]:  # Skip original, start from gray
            result = decode_barcode(processed_image)
            if result.get('success'):
                print(f"🎉 Barcode detected using {img_type} image.")
                break
        
        # If redirect is requested and barcode was success, redirect
        if should_redirect and result.get('success'):
            redirect_url_template = os.getenv('REDIRECT_URL', 'http://localhost/search/{code}')
            
            # Replace placeholders with actual values
            redirect_url = redirect_url_template.replace('{code}', result['data'])
            redirect_url = redirect_url.replace('{protocol}', request.scheme)
            redirect_url = redirect_url.replace('{host}', request.host)
            
            return '', 302, {'Location': redirect_url}
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5555))
    flask_env = os.getenv('FLASK_ENV', 'development')
    is_production = flask_env == 'production'
    
    print("🚀 Barcode Scanner Service starting...")
    print(f"📷 Server will be available at http://localhost:{port}")
    print(f"🔧 Environment: {flask_env}")
    print("🔍 Ready to scan barcodes!")
    redirect_url = os.getenv('REDIRECT_URL', None)
    if redirect_url:
        print(f"🔗 Redirect URL template set to: {redirect_url}")
    
    if is_production:
        # Production: Use Gunicorn
        print("⚙️  Running with Gunicorn (production mode)")
        import subprocess
        subprocess.run([
            'gunicorn',
            '--workers', '2',
            '--worker-class', 'sync',
            '--timeout', '120',
            '--graceful-timeout', '120',
            '--keep-alive', '5',
            '--bind', f'0.0.0.0:{port}',
            '--access-logfile', '-',
            '--error-logfile', '-',
            '--log-level', 'info',
            'server:app'
        ])
    else:
        # Development: Use Flask development server
        print("⚙️  Running with Flask development server")
        app.run(host='0.0.0.0', port=port, debug=True)
