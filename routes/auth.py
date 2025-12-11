from flask import Blueprint, render_template, request, redirect
from flask_login import login_user, logout_user, login_required, current_user
from models.user import User
from extensions import db

auth_bp = Blueprint("auth", __name__)


# ---------------------------
# 註冊
# ---------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # 檢查帳號是否存在
        if User.query.filter_by(username=username).first():
            return render_template("register.html", error="此帳號已被使用")

        # 檢查 email 是否存在
        if User.query.filter_by(email=email).first():
            return render_template("register.html", error="此 Email 已被註冊")

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ---------------------------
# 登入
# ---------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return render_template("login.html", error="帳號或密碼錯誤")

        login_user(user)
        return redirect("/home")

    return render_template("login.html")


# ---------------------------
# 登出
# ---------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")
