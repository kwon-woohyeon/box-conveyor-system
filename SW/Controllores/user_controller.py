from flask import jsonify, request, render_template, redirect, url_for
from app_factory import db
from app.models.user import User

# 사용자 데이터를 OrderedDict로 변환하는 함수
def serialize_user(user):
    return {
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'phone': user.phone,
        'is_admin': user.is_admin,
        'created_date': user.created_date,
        'updated_date': user.updated_date
    }

# GET USER
def getUser(user_id):
    try:
        # db에서 유저 조회
        user = db.session.query(User).filter_by(id=user_id).first_or_404()
        
        # 일치하는 유저가 없는 경우
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # 유저 정보 반환
        return jsonify(serialize_user(user)), 200
    except Exception as e:
        db.session.rollback()
        print(f"에러 발생: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()

# GET ALL
def getAllUsers():
    try:
        # db에서 모든 유저 조회
        users = db.session.query(User).all()
        
        # 일치하는 사용자가 없는 경우
        if not users:
            return render_template("userdata.html", users=[])
        
        # 모든 유저의 정보를 serialize_user 함수를 사용해 배열로 변환
        users_data = [serialize_user(user) for user in users]

        # 유저 정보 반환
        return render_template("userdata.html", users=users_data)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()

# UPDATE
def UpdateUser(user_id):
    
    try:
        # db에서 유저 조회
        user = db.session.query(User).filter_by(id=user_id).first_or_404()
        
        # 일치하는 유저가 없는 경우
        if not user:
            return jsonify({"error": "User not found"}), 404

        # 요청으로부터 업데이트할 데이터 받아오기
        data = request.get_json()

        # 유저 정보 업데이트
        if 'username' in data:
            user.username = data['username']
        if 'name' in data:
            user.name = data['name']
        if 'phone' in data:
            user.phone = data['phone']
        if 'is_admin' in data:
            user.is_admin = bool(data['is_admin'])

        # 데이터베이스에 변경 사항 적용
        db.session.commit()
        
        # 유저 정보 반환
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()

        
# DELETE USER
def DeleteUser(user_id):
    print(f"DeleteUser 함수 호출: user_id={user_id}")
    try:
        # db에서 유저 조회
        user = db.session.query(User).filter_by(id=user_id).first_or_404()
        
        # 일치하는 유저가 없는 경우
        if not user:
            return jsonify({"error": "User not found"}), 404

        # 유저 삭제
        db.session.delete(user)
        db.session.commit()
        
        # 삭제 후 사용자 목록 페이지로 리다이렉트
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.session.close()