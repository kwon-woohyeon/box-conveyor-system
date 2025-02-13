# app/controllers/machine_controller.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from config import configure_app
import threading
import cv2
from flask import Flask, render_template, Response, jsonify
import socket
import json
from ultralytics import YOLO
from app_factory import db
from werkzeug.utils import secure_filename
import requests
from app.controllers.Qr_data_controller import QrInput
# from app_factory import db, create_app

# Flask 애플리케이션 생성
app = Flask(__name__)

configure_app(app)

# host = app.config['RASPBERRY_HOST']
# port = app.config['RASPBERRY_PORT']

    # 소켓 연결 설정
def initialize_socket(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))
    return client_socket

host = '192.168.0.214'  # 라즈베리 파이의 IP 주소
port = 12346  # 포트 번호    
client_socket = initialize_socket(host, port)

def send_Raspberry_start():
    # 소켓 생성

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))  # 라즈베리 파이 서버와 연결

        # 전송할 메시지 (JSON 형식으로 key-value 데이터 생성)
        message = {
            "action": "1"  # 원하는 action 값 설정
        }

        print(f"클라이언트에서 메시지 보내기: {message}")
        # JSON 메시지를 문자열로 변환하여 전송
        s.sendall(json.dumps(message).encode())
        print("메시지 전송 완료")


def send_Raspberry_stop():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))

        message = {
            "action": "2",  # 다른 action 값
        }

        print(f"클라이언트에서 메시지 보내기: {message}")
        s.sendall(json.dumps(message).encode())
        print("메시지 전송 완료")
        for detection in box_detection:
            print(f"Message: {detection['message']}, Image Path: {detection['img_path']}")
        


with open("app/models/coco.txt", "r") as my_file:
    class_list = my_file.read().splitlines()

# YOLO 모델 로드
model = YOLO('app/models/box.pt')
damagemodel = YOLO('app/models/hole.pt')
cautionmodel = YOLO('app/models/caution.pt')

client_socket.settimeout(0.1)  # 타임아웃 설정 (예: 0.5초)

# 웹캠 초기화
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# QR 코드 감지 정보
detected_qr_codes = set()
detected_objects = set()
qr_zone = None  # QR 코드의 좌표 영역 저장
last_qr_value = None


# 'HOLE' 감지 함수, QR 코드 영역 무시
def detect_hole_in_box(frame, x1, y1, x2, y2, qr_zone=None):
    roi = frame[y1:y2, x1:x2]
    detect_params = damagemodel.predict(source=[roi], conf=0.5, save=False)
    boxes = detect_params[0].boxes

    for box in boxes:
        clsID = int(box.cls.numpy()[0])
        if class_list[clsID] == "HOLE":
            bb = box.xyxy.numpy()[0]
            x1_hole, y1_hole, x2_hole, y2_hole = map(int, bb)

            if qr_zone is None or not (
                qr_zone[0] <= x1 + x1_hole <= qr_zone[2] and
                qr_zone[1] <= y1 + y1_hole <= qr_zone[3]
            ):
                cv2.rectangle(frame, (x1 + x1_hole, y1 + y1_hole), (x1 + x2_hole, y1 + y2_hole), (0, 0, 255), 2)
                cv2.putText(frame, "HOLE", (x1 + x1_hole, y1 + y1_hole - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                return True
    return False



# 'CAUTION' 객체 감지 함수 (박스 내부에서만 감지)
def detect_caution_in_box(frame, x1, y1, x2, y2):
    roi = frame[y1:y2, x1:x2]
    detect_params = cautionmodel.predict(source=[roi], conf=0.5, save=False)
    boxes = detect_params[0].boxes

    for box in boxes:
        clsID = int(box.cls.numpy()[0])  # 감지된 클래스 ID
        class_name = cautionmodel.names[clsID]  # YOLO 모델에서 제공하는 클래스 이름 가져오기

        # 바운딩 박스 좌표를 가져오기
        bb = box.xyxy.numpy()[0]
        x1_caution, y1_caution, x2_caution, y2_caution = map(int, bb)

        # 박스 내부에서 'CAUTION' 인식
        cv2.rectangle(frame, (x1 + x1_caution, y1 + y1_caution), (x1 + x2_caution, y1 + y2_caution), (0, 0, 255), 2)
        cv2.putText(frame, class_name, (x1 + x1_caution, y1 + y1_caution - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


# QR 코드 감지 함수, 영역 좌표 반환
def detect_qr_code(frame):
    detector = cv2.QRCodeDetector()
    value, pts, _ = detector.detectAndDecode(frame)

    if pts is not None and value:
        pts = pts[0].astype(int)  # 첫 번째 차원에서 flatten 처리
        qr_zone = (int(pts[0][0]), int(pts[0][1]), int(pts[2][0]), int(pts[2][1]))  # 좌표 설정
        cv2.polylines(frame, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        return value, qr_zone

    return None, None


# def store_box_detection_list():
#     try:
#         with app.app_context():
#             # 리스트를 하나씩 꺼내와서 변수로 만듦.
#             for detection in box_detection:
#                 qr_data_id = detection["message"].get("qr_value")
#                 status_code = detection["message"].get("status")
#                 image_path = detection["img_path"]

#                 # 데이터베이스에 각 데이터를 추가
#                 qr_input = QrInput(
#                     qr_data_id=qr_data_id,
#                     status_code_id=status_code,
#                     image=image_path
#                 )
#                 db.session.add(qr_input)

#             # 한 번에 모든 변경사항을 커밋
#             db.session.commit()
#             print("데이터 저장 성공: 모든 데이터를 데이터베이스에 저장했습니다.")
        
#         # 데이터가 저장되었으므로 리스트를 초기화합니다.
#         box_detection.clear()
#     except Exception as e:
#         db.session.rollback()
#         print(f"데이터 저장 실패: {e}")
#     finally:
#         db.session.close()


# MJPEG 스트리밍을 위한 비디오 생성 함수
def generate_video_feed():
    global qr_zone, last_qr_value
    with app.app_context(): #민영 추가
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break
            # YOLO 모델로 객체 감지
            detect_params = model.predict(source=[frame], conf=0.60, save=False)
            boxes = detect_params[0].boxes

            hole_detected = False

            for box in boxes:
                clsID = int(box.cls.numpy()[0])
                bb = box.xyxy.numpy()[0]

                if clsID >= len(class_list):
                    print(f"Warning: clsID {clsID} is out of range for class_list.")
                    continue
                # "PERSON" 클래스 무시
                if class_list[clsID] == "PERSON":
                    continue

                # 객체 바운딩 박스 표시
                x1, y1, x2, y2 = map(int, bb)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, f"{class_list[clsID]}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # 'HOLE' 감지
                hole_detected = detect_hole_in_box(frame, x1, y1, x2, y2, qr_zone=qr_zone)

                # 'CAUTION' 감지를 해당 객체 박스 내부에서만 수행
                detect_caution_in_box(frame, x1, y1, x2, y2)

            # QR 코드 감지 및 위치 추적
            qr_value, qr_zone = detect_qr_code(frame)
            if qr_value:
                last_qr_value = qr_value
                qr_detected = True
            else:
                last_qr_value = None  # QR 코드 감지되지 않으면 값 초기화
                qr_detected = False

            # QR 코드 값 표시 (감지된 경우에만 표시)
            if last_qr_value:
                cv2.putText(frame, f"QR: {last_qr_value}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # JPEG 포맷으로 이미지 인코딩
            _, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()
            # MJPEG 스트리밍 포맷으로 클라이언트로 전송
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            
            message = {
                "status": "1" if qr_detected and not hole_detected else
                            "2" if not qr_detected and hole_detected else
                            "3" if not qr_detected else
                            "4" if hole_detected else
                            "-1",
                "qr_value": last_qr_value if last_qr_value else ""
            }
            try:
                print("데이터 안들어어옴!!!!!!!!!!!!!")
                recv_message = client_socket.recv(1024).decode()
                print("Received message:", recv_message)

                if recv_message == "capture":
                    ret, frame = cap.read()
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("시발 빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    print("빨리 사진 저장해!!!!!!!!!!!!!")
                    
                    image_path = f"static/detected_image/{last_qr_value}.jpg"
                    cv2.imwrite(image_path,frame)
                    
                    client_socket.sendall(json.dumps(message).encode())
                    box_detection_list(message, image_path)
            except socket.timeout:
                print("Timeout reached, no message received.")
                continue  # 타임아웃 시 계속 대기
            
box_detection = []
def box_detection_list(message, img_path):
    # 현재 들어온 message의 qr_value
    qr_value_to_add = message.get("qr_value")

    # 이미 box_detection 리스트에 같은 qr_value가 있는지 확인
    if any(detection["message"].get("qr_value") == qr_value_to_add for detection in box_detection):
        # 이미 존재하면 추가하지 않음
        print(f"qr_value '{qr_value_to_add}' is already in the list, skipping addition.")
    else:
        # 존재하지 않으면 리스트에 추가
        box_detection.append({
            "message": message,
            "img_path": img_path
        })
        print(f"Added message with qr_value '{qr_value_to_add}' to the box_detection list.")

def video_feed():
    print("비디오 호출*****")
    return Response(generate_video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

    
# 머신 제어 페이지 렌더링
def machine_action_page():
    return render_template("machineaction.html")

# if __name__ == '__main__':
#     print("Starting message receiving thread as a daemon...")
#     message_thread = threading.Thread(target=receive_and_process_messages, daemon=True)
#     message_thread.start()
#     app.run(host="0.0.0.0", port=5000, threaded=True)

