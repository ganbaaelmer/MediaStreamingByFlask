import logging
import threading

import cv2

from config import Config

logger = logging.getLogger(__name__)


class RecordingThread(threading.Thread):
    """Background thread that writes video frames to a file."""

    def __init__(self, camera_capture):
        super().__init__(daemon=True)
        self._capture = camera_capture
        self._running = True
        self._lock = threading.Lock()

        fourcc = cv2.VideoWriter_fourcc(*Config.VIDEO_CODEC)
        self._writer = cv2.VideoWriter(
            Config.VIDEO_OUTPUT_PATH,
            fourcc,
            Config.VIDEO_FPS,
            Config.VIDEO_RESOLUTION,
        )

    def run(self):
        logger.info("Recording started")
        while self._running:
            ret, frame = self._capture.read()
            if ret:
                self._writer.write(frame)
        self._writer.release()
        logger.info("Recording stopped")

    def stop(self):
        self._running = False


class VideoCamera:
    """Manages a video camera capture and optional recording."""

    def __init__(self, device=None):
        device = device if device is not None else Config.CAMERA_DEVICE
        self._capture = cv2.VideoCapture(device)
        if not self._capture.isOpened():
            raise RuntimeError(f"Cannot open camera device {device}")

        self._lock = threading.Lock()
        self._is_recording = False
        self._recording_thread = None
        logger.info("Camera opened on device %s", device)

    def get_frame(self):
        """Capture a single JPEG-encoded frame. Returns bytes or None."""
        with self._lock:
            ret, frame = self._capture.read()

        if not ret:
            logger.warning("Failed to capture frame")
            return None

        encode_params = [cv2.IMWRITE_JPEG_QUALITY, Config.JPEG_QUALITY]
        ret, jpeg = cv2.imencode(".jpg", frame, encode_params)
        if not ret:
            return None

        return jpeg.tobytes()

    def start_record(self):
        """Start recording video to file."""
        if self._is_recording:
            logger.warning("Recording already in progress")
            return

        self._is_recording = True
        self._recording_thread = RecordingThread(self._capture)
        self._recording_thread.start()

    def stop_record(self):
        """Stop recording video."""
        if not self._is_recording:
            return

        self._is_recording = False
        if self._recording_thread is not None:
            self._recording_thread.stop()
            self._recording_thread.join(timeout=5)
            self._recording_thread = None

    def release(self):
        """Release camera resources."""
        self.stop_record()
        self._capture.release()
        logger.info("Camera released")

    def __del__(self):
        self.release()
