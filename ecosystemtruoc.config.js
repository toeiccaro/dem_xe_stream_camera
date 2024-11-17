module.exports = {
  apps: [
    {
      name: 'camera_ai_truoc',  // Tên ứng dụng
      script: '/home/hello/project/stream_camera/camera_ai_env/bin/uvicorn',  // Đường dẫn đến `uvicorn`
      args: 'main_truoc:app --reload --host 192.168.1.112 --port 8010',  // Lệnh chạy ứng dụng FastAPI
      interpreter: 'none',  // Không sử dụng Node.js, vì bạn đang chạy ứng dụng Python
      watch: false,  // Không theo dõi thay đổi mã nguồn (có thể bật nếu cần)
    },
  ],
};
