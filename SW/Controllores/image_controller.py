from flask import request, jsonify, current_app
from app.utils import SaveYoloImage
import os
from app_factory import db

def UploadImage():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    # 이미지 파일을 받고 저장할 경로를 설정
    image_file = request.files['image']
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_file.filename)
    image_file.save(image_path)  # 이미지 파일을 지정된 경로에 저장

    qr_data_id = 1  # 예시로 사용 중인 qr_data_id입니다. 실제 환경에 맞게 설정해야 합니다.
    status_code = int(request.form.get('status_code', 0))  # YOLO로부터 받은 상태 코드 (1-3 범위)


    # YOLO 데이터를 저장하는 함수 호출
    yolo_data = SaveYoloImage(db.session, image_file, qr_data_id, status_code)

    return jsonify({"message": "Image saved successfully", "image_path": yolo_data.image}), 200