# stream/camera_api.py
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import StreamingResponse
import cv2
from process.video_processor import VideoProcessorCamSau
import logging

router = APIRouter()
camera_url_sau = 'rtsp://admin:Quangtri2024@192.168.1.122'
logger = logging.getLogger("camera_stream_ai")

# API that serves video stream
@router.get("/stream_ai_cam_sau")
async def stream_ai_cam_sau():
    camera_url = camera_url_sau  # Replace with your camera URL
    model_path = "yolo11x.pt"
    cam_path = '/home/hello/project/be_server/app/images/cam_sau'
    video_processor = VideoProcessorCamSau(source=camera_url, model_path=model_path, cam_path=cam_path)

    def generate():
        try:
            while True:
                frame = video_processor.process_frame()
                if frame is not None:
                    # Encode the frame in JPEG format
                    ret, jpeg = cv2.imencode('.jpg', frame)
                    if not ret:
                        continue
                    # Convert the frame to byte format for streaming
                    frame_bytes = jpeg.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
                else:
                    # Nếu không còn frame, có thể dừng stream hoặc làm gì đó ở đây
                    pass
        except Exception as e:
            # Log lỗi nếu cần thiết
            print(f"Error during streaming: {e}")
        finally:
            # Giải phóng tài nguyên sau khi hoàn tất stream hoặc có lỗi
            video_processor.stream.release()

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@router.get("/camera_ai")
def start_stream(background_tasks: BackgroundTasks):
    """API để bắt đầu stream video mà không cần trả về dữ liệu."""
    background_tasks.add_task(background_task_ai_cam_sau)
    return {"message": "Video stream is now running in background."}

def background_task_ai_cam_sau():
    camera_url = camera_url_sau  # Replace with your camera URL
    model_path = "yolo11x.pt"
    cam_path = '/home/hello/project/be_server/app/images/cam_sau'
    video_processor = VideoProcessorCamSau(source=camera_url, model_path=model_path, cam_path=cam_path)
    try:
        while True:
            frame = video_processor.process_frame()
            if frame is not None:
                # Encode the frame in JPEG format
                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                # Convert the frame to byte format for streaming
                frame_bytes = jpeg.tobytes()
                logger.debug("Đã xử lý một khung hình.")
                # yield (b'--frame\r\n'
                #        b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n')
            else:
                # Nếu không còn frame, có thể dừng stream hoặc làm gì đó ở đây
                pass
    except Exception as e:
        # Log lỗi nếu cần thiết
        print(f"Error during streaming: {e}")
    finally:
        # Giải phóng tài nguyên sau khi hoàn tất stream hoặc có lỗi
        video_processor.stream.release()