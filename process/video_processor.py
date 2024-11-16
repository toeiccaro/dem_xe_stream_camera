# video_processor.py
import cv2
import numpy as np
from ultralytics import YOLO
import cvzone
import os
import time
from enum import Enum
from datetime import datetime

class CarType(str, Enum):
    xe_con = "xe_con"
    xe_tai = "xe_tai"
    xe_cau = "xe_cau"
    xe_cong_nong = "xe_cong_nong"
    xe_nang = "xe_nang"

class VideoProcessorCamSau:
    def __init__(self, source, model_path, cam_path):
        self.source = source  # Store the camera source as an attribute
        self.stream = cv2.VideoCapture(source)
        self.model = YOLO(model_path)
        self.class_names = self.load_class_names("coco.txt")
        self.hardcoded_polylines = {
            'area1': [(165, 168), (553, 103), (560, 197), (298, 268)],
            'area2': [(301, 275), (745, 155), (975, 205), (575, 465)]
        }
        self.count = 0
        self.going_up = {}
        self.going_down = {}
        self.gnu = []
        self.gnd = []
        self.vehicle_status = {}

        # Directory to save images (optional, if you need to save images locally)
        self.save_dir = cam_path
        os.makedirs(self.save_dir, exist_ok=True)

    def load_class_names(self, filepath):
        with open(filepath, "r") as f:
            return f.read().splitlines()

    def draw_hardcoded_polylines(self, frame):
        for name, polyline in self.hardcoded_polylines.items():
            polyline_array = np.array(polyline, dtype=np.int32)
            cv2.polylines(frame, [polyline_array], isClosed=True, color=(255, 0, 0), thickness=2)
        return frame
    
    def connect_to_stream(self, source):
        cap = cv2.VideoCapture(source)
        print(f" connect_to_stream = {source}")
        if not cap.isOpened():
            print(f"Error: Failed to connect to camera source {source}")
        return cap
    
    def reconnect_stream(self):
        # Try to reconnect after a short delay
        print("Attempting to reconnect to the camera...")
        self.stream.release()
        time.sleep(5)  # Wait before trying to reconnect
        self.stream = self.connect_to_stream(self.source)

    def process_frame(self):
        ret, frame = self.stream.read()

        # Check if the frame was successfully captured
        if not ret or frame is None:
            print("Error: Failed to capture frame from the source. Check if the video source is accessible.")
            self.reconnect_stream()
            return None  # Skip further processing if the frame is invalid

        frame = cv2.resize(frame, (1020, 500))
        frame = self.draw_hardcoded_polylines(frame)
        results = self.model.track(frame, persist=True, classes=[2, 7])

        if results and hasattr(results[0], 'boxes') and results[0].boxes is not None:
            boxes = results[0].boxes.xyxy.int().cpu().tolist()
            class_ids = results[0].boxes.cls.int().cpu().tolist()
            track_ids = results[0].boxes.id.int().cpu().tolist() if results[0].boxes.id is not None else [None] * len(boxes)

            for box, class_id, track_id in zip(boxes, class_ids, track_ids):
                self.process_box(frame, box, track_id, class_id)
        else:
            print("No objects detected in this frame.")

        return frame

    def process_box(self, frame, box, track_id, class_id):
        c = self.class_names[class_id]
        x1, y1, x2, y2 = box
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        # Kiểm tra nếu xe đang trong khu vực 1
        if cv2.pointPolygonTest(np.array(self.hardcoded_polylines['area1'], dtype=np.int32), (cx, cy), False) >= 0:
            self.vehicle_status[track_id] = "in_area1"

        # Kiểm tra nếu xe đang trong khu vực 2 và đã từng ở khu vực 1
        if (cv2.pointPolygonTest(np.array(self.hardcoded_polylines['area2'], dtype=np.int32), (cx, cy), False) >= 0 and
            self.vehicle_status.get(track_id) == "in_area1"):
            print("cccccccccccc222222222222222222----------->111111111111111111")

            self.record_vehicle(frame, x1, y1, x2, y2, track_id, c, "vao")
            self.vehicle_status[track_id] = "moved_to_area2"

        # Kiểm tra nếu xe đang trong khu vực 2 và di chuyển trở lại khu vực 1
        if cv2.pointPolygonTest(np.array(self.hardcoded_polylines['area2'], dtype=np.int32), (cx, cy), False) >= 0:
            self.vehicle_status[track_id] = "in_area2"

        if (cv2.pointPolygonTest(np.array(self.hardcoded_polylines['area1'], dtype=np.int32), (cx, cy), False) >= 0 and
            self.vehicle_status.get(track_id) == "in_area2"):
            print("cccccccccccc1111111111111111----------->2222222222222222")
            print("c333")
            self.record_vehicle(frame, x1, y1, x2, y2, track_id, c, "ra")
            self.vehicle_status[track_id] = "moved_to_area1"

    def record_vehicle(self, frame, x1, y1, x2, y2, track_id, class_name, direction):
        # This is a simplified version since we're not saving images to the DB
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cvzone.putTextRect(frame, f'{track_id}', (x1, y2), 1, 1)
        cvzone.putTextRect(frame, f'o_to', (x1, y1), 1, 1)
        
        print("callhere111", track_id)

        date_folder = datetime.now().strftime("%Y%m%d")  # Lấy ngày hiện tại
        direction_folder = os.path.join(self.save_dir, direction, date_folder)  # Tạo đường dẫn cho thư mục
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(direction_folder, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Tạo đường dẫn cho ảnh
        image_path = os.path.join(direction_folder, f'vehicle_{track_id}_{timestamp}.jpg')
        print("callhere222", track_id)

        folder_path = direction_folder
        # Check for existing images with the same track_id
        for filename in os.listdir(folder_path):
            if filename.startswith(f'vehicle_{track_id}_'):
                # Extract timestamp from the existing filename
                existing_time_str = filename.split('_')[2] + '_' + filename.split('_')[3][:6]
                existing_time = datetime.strptime(existing_time_str, "%Y%m%d_%H%M%S")

                # Check if the existing time is within 1 hour of the new timestamp
                new_time = datetime.now()
                if abs((new_time - existing_time).total_seconds()) <= 300:
                    print(f"Image for track_id {track_id} already exists within 5 minutes. Skipping save.")
                    return  # Skip saving if an image exists within 1 hour
        # cv2.imwrite(image_path, frame)        
        print("before save to db", track_id)
        print("class_nameclass_name", class_name)
        car_type = CarType.xe_tai
        # return frame
