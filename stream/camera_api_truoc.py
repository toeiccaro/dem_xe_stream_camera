import logging
import cv2
import time
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
from threading import Thread

# Cấu hình logging
logger = logging.getLogger("camera_stream")
is_processing = False

# URL RTSP của camera
camera_url = 'rtsp://admin:Quangtri2024@192.168.1.123'

router = APIRouter()

def gen_frames():
    logger.info("Bắt đầu kết nối tới camera.")
    cap = cv2.VideoCapture(camera_url)
    if not cap.isOpened():
        logger.error("Không thể kết nối tới camera. Kiểm tra URL RTSP.")
        raise RuntimeError("Không thể kết nối tới camera.")

    logger.info("Kết nối thành công tới camera.")
    while True:
        success, frame = cap.read()
        if not success:
            logger.warning("Không nhận được khung hình từ camera. Dừng stream.")
            break
        
        current_time = time.strftime("%Y-%m-%d %H:%M:%S")

        # Log kích thước của khung hình kèm thời gian
        height, width, _ = frame.shape
        logger.info(f"[{current_time}] frame: {width}x{height}")

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        logger.debug("Đã xử lý một khung hình.")
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    logger.info("Đã ngắt kết nối camera.")

@router.get("/camera")
def start_stream():
    """API để bắt đầu stream video mà không cần trả về dữ liệu."""
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")


# @router.get("/camera")
# def start_stream():
#     return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")