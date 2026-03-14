# MediaStreamingByFlask

A Flask-based home security camera application that streams live video and audio from your local camera and microphone to a web browser.

## Features

- Live MJPEG video streaming
- Live WAV audio streaming
- Video recording to file with start/stop controls
- Download recorded video

## Requirements

- Python 3.9+
- Webcam (video capture device)
- Microphone (audio input device)
- System dependencies for PyAudio (e.g., `portaudio19-dev` on Debian/Ubuntu)

## Installation

```bash
# Install system dependencies (Debian/Ubuntu)
sudo apt-get install portaudio19-dev python3-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

```bash
python app.py
```

Open `http://localhost:9000` in your browser.

## Configuration

Configuration is managed via environment variables (see `config.py`):

| Variable            | Default | Description                  |
|---------------------|---------|------------------------------|
| `HOST`              | 0.0.0.0 | Server bind address         |
| `PORT`              | 9000    | Server port                  |
| `FLASK_DEBUG`       | false   | Enable Flask debug mode      |
| `CAMERA_DEVICE`     | 0       | Video capture device index   |
| `AUDIO_DEVICE_INDEX`| 1       | Audio input device index     |

## Project Structure

```
├── app.py              # Flask application with video/audio routes
├── camera.py           # Video camera capture and recording
├── config.py           # Centralized configuration
├── requirements.txt    # Python dependencies
├── static/
│   └── recorder.js     # Frontend recording controls
└── templates/
    └── index.html      # Main UI page
```
