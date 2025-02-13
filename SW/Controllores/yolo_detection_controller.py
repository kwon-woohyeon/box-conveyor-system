import cv2
import socket
import json
import time
from ultralytics import YOLO


# 이새끼 버려
def run_detection_system():
    # 클래스 목록 로드
    def load_class_list(file_path):
        with open(file_path, "r") as my_file:
            return my_file.read().splitlines()

    # 모델 로드
    model = YOLO('app/models/box.pt')
    damagemodel = YOLO('app/models/hole.pt')
    cautionmodel = YOLO('app/models/caution.pt')
    class_list = load_class_list("app/models/coco.txt")

    # 소켓 연결 설정
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.0.214', 12346))

    # 웹캠 초기화
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    while True:
        try:
            # 소켓에서 메시지를 수신
            client_socket.settimeout(0.1)  # 수신 대기 시간 설정
            try:
                message = client_socket.recv(1024).decode()
                if message == "capture":
                    ret, frame = cap.read()
                    if ret:
                        # 캡처한 프레임을 저장하거나 원하는 처리를 수행
                        cv2.imwrite("static/detected_image/captured_frame.jpg", frame)
                        print("Captured and saved frame.")
            except socket.timeout:
                pass  # 타임아웃 발생 시 무시하고 다음으로 진행

            # 프레임 읽기 및 감지
            ret, frame = cap.read()
            if ret:
                frame = detect_boxes(frame, model, damagemodel, cautionmodel, class_list, client_socket)
                cv2.imshow("Detection", frame)

            # 'q' 키를 누르면 루프 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(f"Error: {e}")
            break

    # 자원 정리
    client_socket.close()
    cap.release()
    cv2.destroyAllWindows()

def detect_boxes(imagecapture, model, damagemodel, cautionmodel, class_list, client_socket):
    # 메인 모델을 사용하여 이미지에서 박스 감지 수행
    detect_params = model.predict(source=[imagecapture], conf=0.65, save=False)
    boxes = detect_params[0].boxes

    qr_detected = False
    hole_detected = False
    qr_value = None
    qr_zone = None

    # 각 박스에 대해 감지 결과 처리
    for box in boxes:
        clsID = int(box.cls.numpy()[0])
        bb = box.xyxy.numpy()[0]
        x1, y1, x2, y2 = map(int, bb)

        # QR 코드 감지
        qr_value, qr_zone = detect_qr_code(imagecapture)
        if qr_value:
            qr_detected = True

        # HOLE 감지
        hole_detected = detect_hole_in_box(imagecapture, x1, y1, x2, y2, qr_zone=qr_zone, damagemodel=damagemodel)

        # CAUTION 감지
        detect_caution_in_box(imagecapture, x1, y1, x2, y2, cautionmodel=cautionmodel)

        # 상태 코드 설정
        status_code = (
            "1" if qr_detected and not hole_detected else
            "2" if not qr_detected and hole_detected else
            "3" if not qr_detected else
            "4" if hole_detected else
            "-1"
        )

        # 서버로 전송할 메시지 준비
        message = {
            "status": status_code,
            "qr_value": qr_value if qr_value else ""
        }

        # 소켓을 통해 메시지 전송
        client_socket.sendall(json.dumps(message).encode())

        # 검출된 객체에 대한 시각적 표시 추가 (테두리 등)
        cv2.rectangle(imagecapture, (x1, y1), (x2, y2), (255, 0, 0), 2)

    return imagecapture

def detect_qr_code(frame):
    detector = cv2.QRCodeDetector()
    value, pts, _ = detector.detectAndDecode(frame)

    if pts is not None and value:
        pts = pts[0].astype(int)
        qr_zone = (int(pts[0][0]), int(pts[0][1]), int(pts[2][0]), int(pts[2][1]))
        cv2.rectangle(frame, (qr_zone[0], qr_zone[1]), (qr_zone[2], qr_zone[3]), (0, 255, 0), 2)
        return value, qr_zone

    return None, None

def detect_hole_in_box(frame, x1, y1, x2, y2, qr_zone=None, damagemodel=None):
    roi = frame[y1:y2, x1:x2]
    detect_params = damagemodel.predict(source=[roi], conf=0.6, save=False)
    boxes = detect_params[0].boxes

    for box in boxes:
        clsID = int(box.cls.numpy()[0])
        if damagemodel.names[clsID] == "HOLE":
            bb = box.xyxy.numpy()[0]
            x1_hole, y1_hole, x2_hole, y2_hole = map(int, bb)
            
            if qr_zone is None or not (
                qr_zone[0] <= x1 + x1_hole <= qr_zone[2] and
                qr_zone[1] <= y1 + y1_hole <= qr_zone[3]
            ):
                cv2.rectangle(frame, (x1 + x1_hole, y1 + y1_hole), (x1 + x2_hole, y1 + y2_hole), (0, 0, 255), 2)
                return True
    return False

def detect_caution_in_box(frame, x1, y1, x2, y2, cautionmodel=None):
    roi = frame[y1:y2, x1:x2]
    detect_params = cautionmodel.predict(source=[roi], conf=0.5, save=False)
    boxes = detect_params[0].boxes

    for box in boxes:
        clsID = int(box.cls.numpy()[0])
        if cautionmodel.names[clsID] == "CAUTION":
            bb = box.xyxy.numpy()[0]
            x1_caution, y1_caution, x2_caution, y2_caution = map(int, bb)
            cv2.rectangle(frame, (x1 + x1_caution, y1 + y1_caution), (x1 + x2_caution, y1 + y2_caution), (255, 255, 0), 2)
            print("CAUTION detected in box.")

def stop_detection_system():
    global client_socket, cap

    # 시스템 중지 처리
    if client_socket:
        client_socket.close()
    if cap:
        cap.release()
    cv2.destroyAllWindows()
    print("Detection system stopped.")

