import os


class Config:
    """Application configuration."""

    # Server
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 9000))
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    # Video
    CAMERA_DEVICE = int(os.environ.get("CAMERA_DEVICE", 0))
    VIDEO_FPS = 20.0
    VIDEO_RESOLUTION = (640, 480)
    VIDEO_OUTPUT_PATH = os.path.join("static", "video.avi")
    VIDEO_CODEC = "MJPG"
    JPEG_QUALITY = 80

    # Audio
    AUDIO_FORMAT_WIDTH = 16  # bits per sample
    AUDIO_CHANNELS = 2
    AUDIO_RATE = 44100
    AUDIO_CHUNK = 1024
    AUDIO_DEVICE_INDEX = int(os.environ.get("AUDIO_DEVICE_INDEX", 1))
