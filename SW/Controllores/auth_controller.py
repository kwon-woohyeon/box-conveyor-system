from flask import request, session, redirect, render_template, url_for, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app_factory import db
# from sqlalchemy.orm import sessionmake

# 회원가입
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = generate_password_hash(request.form.get('password'))
        name = request.form.get('name')
        phone = request.form.get('phone')

        new_user = User(username=username, password=password, name=name, phone=phone)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("User registered successfully", "success")
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash(f"Registration error: {str(e)}", "error")
            return render_template('register.html')

    return render_template('register.html')
        
        
# 로그인
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"Username: {username}")
        print(f"password: {password}")
        user = db.session.query(User).filter_by(username=username).first()

        if user:
            print(f"User found: {user.username}")
        else:
            print("User not found")
            flash("Invalid credentials", "error")
            return render_template('login.html')

        # 비밀번호 확인
        if check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin
            session['username'] = user.username
            session['name'] = user.name
            flash("Login successful", "success")
            print("사용자 인증 됨")
            return redirect(url_for('homepage'))
        else:
            flash("Invalid credentials", "error")
            print("사용자 인증 안됨")
            return render_template('login.html')

    return render_template('login.html')

# 로그아웃
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully", "success")
    return redirect(url_for('home'))
    
