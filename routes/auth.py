from flask import Blueprint, render_template, request, redirect
from flask_login import login_user, logout_user, login_required
from models.user import User
from extensions import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 檢查帳號是否已存在
        existing = User.query.filter_by(username=username).first()
        if existing:
            error = "此帳號已被使用，請換一個帳號"
            return render_template("register.html", error=error)

        # 建立新帳號
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            error = "帳號或密碼錯誤"
            return render_template("login.html", error=error)

        login_user(user)
        return redirect("/home")    #修正！登入成功轉到文章首頁

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")       #登出後回登入頁
