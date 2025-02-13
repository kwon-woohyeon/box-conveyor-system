# app/controllers/yolo_controller.py

from flask import jsonify, request
from app_factory import db
from app.models.qr import QrInput
import os
from werkzeug.utils import secure_filename

##이거 날려
# YOLO 데이터 저장
def save_yolo_data():
    # 이미지, 상태 코드 추출
    if 'image' not in request.files or 'status_code' not in request.form:
        return jsonify({"error": "Image file or status code missing"}), 400

    #yolo에서 받아오는 데이터
    image_file = request.files['image']
    status_code = request.form.get("status_code")
    qr_data_id = request.form.get("qr_data_id")

    if not qr_data_id or not status_code:
        return jsonify({"error": "qr_data_id 또는 status_code가 없습니다."}), 400

    # 이미지 저장
    image_directory = "static/images"
    os.makedirs(image_directory, exist_ok=True)
    filename = secure_filename(f"{qr_data_id}_{status_code}.jpg")
    image_path = os.path.join(image_directory, filename)
    image_file.save(image_path)
    print(f"이미지 파일이 저장되었습니다: {image_path}")

    try:
        # DB에 이미지 경로와 상태 코드 저장
        qr_input = QrInput(
            qr_data_id=qr_data_id,
            status_code_id=status_code,
            image=image_path
        )
        db.session.add(qr_input)
        db.session.commit()
        
        response = {
            "message": "Image and data successfully saved.",
            "data": {
                "image_path": image_path,
                "status_code": status_code,
                "qr_data_id": qr_data_id,
            }
        }
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()


# # YOLO 데이터 조회
# def get_yolo_data():
#     try:
#         yolo_data = db.session.query(QrInput).all()
#         data = [
#             {
#                 "qr_input_id": entry.id,
#                 "qr_data_id": entry.qr_data_id,
#                 "status_code": entry.status_code_id,
#                 "image": entry.image,
#                 "created_date": entry.created_date
#             } for entry in yolo_data
#         ]
#         return jsonify(data), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#     finally:
#         db.session.close()