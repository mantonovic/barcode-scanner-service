# Barcode Scanner Service 📷

A real-time barcode scanning web service that uses your device's camera to detect and decode barcodes.

## Features

- 🎥 Real-time video stream processing
- 📱 Works on mobile and desktop devices
- 🔍 Supports multiple barcode formats (QR codes, UPC, EAN, Code128, etc.)
- ⚡ Fast detection and response
- 🎨 Modern, responsive UI
- 🔄 Automatic continuous scanning

## Architecture

- **Backend**: Flask server with OpenCV and pyzbar for barcode detection
- **Frontend**: HTML5 with Camera API for video capture
- **Communication**: REST API with base64-encoded frame transmission

## Requirements

### Option 1: Docker (Recommended)
- Docker
- Docker Compose
- Modern web browser with camera support
- Camera/webcam device

### Option 2: Manual Setup
- Python 3.8+
- Modern web browser with camera support
- Camera/webcam device

## Installation & Usage

### 🐳 Option 1: Using Docker (Recommended)

This is the easiest way to run the service with all dependencies included.

1. **Build and start the service:**
   ```bash
   docker-compose up -d
   ```

2. **Open your browser and navigate to:**
   ```
   http://localhost:5555
   ```

3. **View logs (optional):**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the service:**
   ```bash
   docker-compose down
   ```

#### Alternative: Using Docker directly

```bash
# Build the image
docker build -t barcode-scanner .

# Run the container
docker run -d -p 5000:5000 --name barcode-scanner barcode-scanner

# Stop the container
docker stop barcode-scanner
docker rm barcode-scanner
```

### 🔧 Option 2: Manual Installation

1. **Install system dependencies (for pyzbar):**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y libzbar0
   
   # macOS
   brew install zbar
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   python server.py
   ```

4. **Open your browser and navigate to:**
   ```
   http://localhost:5555
   ```

### 🔧 Port Configuration

The default port is **5555**, but you can configure it using the `PORT` environment variable:

**Docker:**
```bash
# In docker-compose.yml, change:
environment:
  - PORT=8080
ports:
  - "8080:8080"
```

**Manual:**
```bash
PORT=8080 python server.py
```

## How to Use

1. Click "Start Camera" to begin scanning

2. Point your camera at a barcode - when detected, the code will be displayed automatically

## API Endpoints

### `POST /scan`
Receives a video frame and scans for barcodes.

**Request:**
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

**Response (barcode found):**
```json
{
  "found": true,
  "data": "1234567890",
  "type": "EAN13"
}
```

**Response (no barcode):**
```json
{
  "found": false
}
```

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## Supported Barcode Formats

- QR Code
- EAN-8, EAN-13
- UPC-A, UPC-E
- Code 39, Code 93, Code 128
- Interleaved 2 of 5 (ITF)
- Codabar
- DataBar
- PDF417
- And more...

## Development

The service scans frames every 500ms by default. You can adjust this interval in `index.html`:

```javascript
scanInterval = setInterval(captureAndScan, 500); // Change 500 to your desired interval
```

## Troubleshooting

**Camera not working:**
- Ensure you're using HTTPS or localhost (browsers require secure context for camera access)
- Grant camera permissions when prompted
- Check if another application is using the camera

**Barcode not detected:**
- Ensure good lighting conditions
- Hold the barcode steady and in focus
- Try different distances from the camera
- Make sure the barcode is not damaged or obscured

## License

MIT