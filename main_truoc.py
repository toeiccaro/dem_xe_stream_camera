import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stream.camera_api import router as camera_router  # Cập nhật import từ thư mục stream
from stream.camera_stream_ai_cam_truoc import router as camera_stream_ai_cam_truoc  # Cập nhật import từ thư mục stream

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("camera_stream")

# Khởi tạo ứng dụng FastAPI
app = FastAPI()

# Cấu hình CORS
origins = ["http://localhost", "http://127.0.0.1", "http://192.168.1.112", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router của camera vào ứng dụng FastAPI
app.include_router(camera_router)
app.include_router(camera_stream_ai_cam_truoc)

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI on port 8010!"}

# Thêm sự kiện startup

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.1.112", port=8010, log_level="info", reload=True)
