import traceback
from flask import jsonify, render_template
from app_factory import db
from app.models.qr import QrInput, QrData, StatusCode
import app.controllers.machine_controller as mc

# GET ALL
def GetAllQr():
    try:
        # app을 함수 내부에서 지연 임포트하여 순환 의존성 문제 방지
        from app_factory import create_app
        app = create_app()
        
        with app.app_context():
            # 리스트를 하나씩 꺼내와서 변수로 만듦.
            for detection in mc.box_detection:
                qr_data_id = detection["message"].get("qr_value")
                status_code = detection["message"].get("status")
                image_path = detection["img_path"]
                
                
                # qr_data_id가 유효한 정수인지 확인
                if not qr_data_id or not str(qr_data_id).isdigit():
                    print(f"Invalid qr_data_id: '{qr_data_id}', skipping this entry.")
                    continue  # 올바른 정수 값이 아니라면 해당 항목을 건너뜁니다.


                # 데이터베이스에 각 데이터를 추가
                qr_input = QrInput(
                    qr_data_id=qr_data_id,
                    status_code_id=status_code,
                    image=image_path
                )
                db.session.add(qr_input)

            # 한 번에 모든 변경사항을 커밋
            db.session.commit()
            print("데이터 저장 성공: 모든 데이터를 데이터베이스에 저장했습니다.")
        
            # 데이터가 저장되었으므로 리스트를 초기화합니다.
            mc.box_detection.clear()
    except Exception as e:
        db.session.rollback()
        print(f"데이터 저장 실패: {e}")
        traceback.print_exc()

        
    try:
        with app.app_context():
            query = (
                db.session.query(
                    QrInput.qr_data_id.label('qr_data_id'),
                    QrInput.status_code_id,
                    QrInput.image,
                    QrInput.created_date.label('qr_input_created_date'),
                    QrData.send_name,
                    QrData.receive_name,
                    QrData.receive_address,
                    QrData.receive_phone,
                    QrData.created_date.label('qr_data_created_date'),
                    StatusCode.id.label('status_code_id'),
                    StatusCode.description.label('status_description')
                )
                .join(QrData, QrInput.qr_data_id == QrData.id, isouter=True)
                .outerjoin(StatusCode, QrInput.status_code_id == StatusCode.id)
            )

            results = []
            for row in query.all():
                print("**row : " + str(row))
                results.append({
                    'qr_data_id': row.qr_data_id,
                    'image': row.image if row.image else 'default_image.png',
                    'qr_input_created_date': row.qr_input_created_date,
                    'send_name': row.send_name,
                    'receive_name': row.receive_name,
                    'receive_address': row.receive_address,
                    'receive_phone': row.receive_phone,
                    'qr_data_created_date': row.qr_data_created_date,
                    'status_code_id': row.status_code_id,
                    'status_description': row.status_description
                })
                
            if not results:
                print("No data found!")  # 데이터가 없을 때 확인

            return render_template("boxdata.html", results=results)
    except Exception as e:
        print(f"Database query failed: {e}")
        traceback.print_exc()  # 예외의 구체적인 내용 출력
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.remove()