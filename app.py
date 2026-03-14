import logging
import struct
import threading

import pyaudio
from flask import Flask, Response, jsonify, render_template, request

from camera import VideoCamera
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Video
# ---------------------------------------------------------------------------

_video_camera = None
_video_lock = threading.Lock()
_last_frame = None


def _get_camera():
    """Lazily initialize the video camera (thread-safe)."""
    global _video_camera
    if _video_camera is None:
        with _video_lock:
            if _video_camera is None:
                _video_camera = VideoCamera()
    return _video_camera


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/record_status", methods=["POST"])
def record_status():
    camera = _get_camera()
    data = request.get_json(silent=True)
    if data is None or "status" not in data:
        return jsonify(error="Missing 'status' field"), 400

    if data["status"] == "true":
        camera.start_record()
        return jsonify(result="started")
    else:
        camera.stop_record()
        return jsonify(result="stopped")


def _generate_video_frames():
    """Yield MJPEG frames for the video stream."""
    global _last_frame
    camera = _get_camera()

    while True:
        frame = camera.get_frame()
        if frame is not None:
            _last_frame = frame
        elif _last_frame is None:
            continue

        output = _last_frame if frame is None else frame
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + output + b"\r\n\r\n"
        )


@app.route("/video_viewer")
def video_viewer():
    return Response(
        _generate_video_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


# ---------------------------------------------------------------------------
# Audio
# ---------------------------------------------------------------------------

_audio_engine = pyaudio.PyAudio()


def _build_wav_header(sample_rate, bits_per_sample, channels):
    """Build a WAV header for a continuous audio stream."""
    byte_rate = sample_rate * channels * bits_per_sample // 8
    block_align = channels * bits_per_sample // 8
    # Use a large data size placeholder for continuous streaming
    data_size = 0x7FFFFFFF

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        data_size + 36,
        b"WAVE",
        b"fmt ",
        16,                 # PCM header size
        1,                  # PCM format
        channels,
        sample_rate,
        byte_rate,
        block_align,
        bits_per_sample,
        b"data",
        data_size,
    )
    return header


def _generate_audio():
    """Yield WAV audio data from the microphone."""
    wav_header = _build_wav_header(
        Config.AUDIO_RATE,
        Config.AUDIO_FORMAT_WIDTH,
        Config.AUDIO_CHANNELS,
    )

    stream = _audio_engine.open(
        format=pyaudio.paInt16,
        channels=Config.AUDIO_CHANNELS,
        rate=Config.AUDIO_RATE,
        input=True,
        input_device_index=Config.AUDIO_DEVICE_INDEX,
        frames_per_buffer=Config.AUDIO_CHUNK,
    )
    logger.info("Audio stream started")

    try:
        first_run = True
        while True:
            data = stream.read(Config.AUDIO_CHUNK, exception_on_overflow=False)
            if first_run:
                data = wav_header + data
                first_run = False
            yield data
    except GeneratorExit:
        stream.stop_stream()
        stream.close()
        logger.info("Audio stream closed")


@app.route("/audio")
def audio():
    return Response(_generate_audio(), mimetype="audio/x-wav")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        threaded=True,
    )
