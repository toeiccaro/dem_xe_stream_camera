# stream/camera_api.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cv2
from process.video_processor import VideoProcessorCamSau

router = APIRouter()
camera_url_sau = 'rtsp://admin:Quangtri2024@192.168.1.122'

# API that serves video stream
@router.get("/stream_ai_cam_sau")
async def stream_ai_cam_sau():
    camera_url = camera_url_sau  # Replace with your camera URL
    model_path = "yolo11x.pt"
    cam_path = '/home/hello/project/dem_xe_be/app/images/cam_sau'
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
