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

### React Integration Example

Here's how to create a React component (v19.0.0+) that integrates with the barcode scanner service:

```jsx
import { useRef, useEffect, useState } from 'react';

/**
 * BarcodeScanner component for React 19
 * @param {Object} props
 * @param {Function} props.onScanned - Callback function that receives the scanned barcode data
 * @param {string} props.serverUrl - URL of the barcode scanner service (default: http://localhost:5555)
 * @param {number} props.scanInterval - Interval between scans in ms (default: 500)
 */
export default function BarcodeScanner({ 
  onScanned, 
  serverUrl = 'http://localhost:5555',
  scanInterval = 500 
}) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const scanIntervalRef = useRef(null);
  
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState(null);
  const [lastScan, setLastScan] = useState(null);

  const startCamera = async () => {
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsScanning(true);
    } catch (err) {
      setError(`Camera error: ${err.message}`);
    }
  };

  const stopCamera = () => {
    if (scanIntervalRef.current) {
      clearInterval(scanIntervalRef.current);
      scanIntervalRef.current = null;
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    
    setIsScanning(false);
  };

  const captureAndScan = async () => {
    if (!isScanning || !videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const imageData = canvas.toDataURL('image/jpeg', 0.8);

    try {
      const response = await fetch(`${serverUrl}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
      });

      const result = await response.json();

      if (result.found) {
        setLastScan(result);
        onScanned?.(result); // Call the callback with barcode data
      }
    } catch (err) {
      console.error('Scan error:', err);
    }
  };

  useEffect(() => {
    if (isScanning) {
      scanIntervalRef.current = setInterval(captureAndScan, scanInterval);
    }
    
    return () => {
      if (scanIntervalRef.current) {
        clearInterval(scanIntervalRef.current);
      }
    };
  }, [isScanning, scanInterval]);

  useEffect(() => {
    return () => stopCamera(); // Cleanup on unmount
  }, []);

  return (
    <div style={{ maxWidth: '640px', margin: '0 auto', padding: '20px' }}>
      <h2>Barcode Scanner</h2>
      
      <div style={{ 
        position: 'relative', 
        background: '#000', 
        borderRadius: '8px',
        overflow: 'hidden',
        marginBottom: '20px'
      }}>
        <video 
          ref={videoRef} 
          autoPlay 
          playsInline
          style={{ width: '100%', display: 'block' }}
        />
        <canvas ref={canvasRef} style={{ display: 'none' }} />
      </div>

      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <button 
          onClick={startCamera} 
          disabled={isScanning}
          style={{
            padding: '10px 20px',
            borderRadius: '5px',
            border: 'none',
            background: isScanning ? '#ccc' : '#007bff',
            color: 'white',
            cursor: isScanning ? 'not-allowed' : 'pointer'
          }}
        >
          Start Camera
        </button>
        <button 
          onClick={stopCamera}
          disabled={!isScanning}
          style={{
            padding: '10px 20px',
            borderRadius: '5px',
            border: 'none',
            background: !isScanning ? '#ccc' : '#dc3545',
            color: 'white',
            cursor: !isScanning ? 'not-allowed' : 'pointer'
          }}
        >
          Stop Camera
        </button>
      </div>

      {error && (
        <div style={{ 
          padding: '15px', 
          background: '#f8d7da', 
          color: '#721c24',
          borderRadius: '5px',
          marginBottom: '20px'
        }}>
          {error}
        </div>
      )}

      {lastScan && (
        <div style={{ 
          padding: '15px', 
          background: '#d4edda', 
          color: '#155724',
          borderRadius: '5px'
        }}>
          <strong>Last Scan:</strong> {lastScan.data} ({lastScan.type})
        </div>
      )}

      <p style={{ fontSize: '14px', color: '#666' }}>
        {isScanning ? 'Scanning for barcodes...' : 'Click Start Camera to begin'}
      </p>
    </div>
  );
}
```

**Usage Example:**

```jsx
import BarcodeScanner from './BarcodeScanner';

function App() {
  const handleBarcodeScanned = (result) => {
    console.log('Barcode scanned:', result.data);
    console.log('Barcode type:', result.type);
    
    // Do something with the scanned code
    alert(`Scanned: ${result.data}`);
  };

  return (
    <div>
      <h1>My Barcode Scanner App</h1>
      <BarcodeScanner 
        onScanned={handleBarcodeScanned}
        serverUrl="http://localhost:5555"
        scanInterval={500}
      />
    </div>
  );
}

export default App;
```

### Customization

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

MIT License - see [LICENSE](LICENSE) file for details.

### Dependency Licenses

This project uses the following open-source dependencies:

- **Flask** - BSD-3-Clause
- **Flask-Cors** - MIT
- **opencv-python** - Apache 2.0
- **pyzbar** - MIT
- **numpy** - BSD-3-Clause

All dependencies are compatible with the MIT License.