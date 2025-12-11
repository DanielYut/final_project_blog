from flask import Blueprint, render_template, request, redirect
from datetime import datetime, timedelta
from extensions import db, mail
from models.user import User
from flask_mail import Message
import random, string

reset_bp = Blueprint("reset", __name__)


# 產生六位數驗證碼
def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))


# -------------------------------
# 忘記密碼 - 輸入 Email
# -------------------------------
@reset_bp.route("/forgot", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()

        if not user:
            return render_template("forgot_password.html", error="查無此 Email")

        code = generate_code()

        # 準備存入 DB
        user.reset_code = code
        user.reset_code_expire = datetime.now() + timedelta(minutes=10)
        db.session.commit()

        # 寄信
        msg = Message(
            subject="CampusHub 密碼重設驗證碼",
            recipients=[email],
            body=f"你的驗證碼是：{code}\n有效時間 10 分鐘。"
        )
        mail.send(msg)

        print("已寄出驗證碼：", code)

        return redirect("/reset")

    return render_template("forgot_password.html")


# -------------------------------
# 重設密碼 - 驗證碼 + 新密碼
# -------------------------------
@reset_bp.route("/reset", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        code = request.form["code"]
        new_password = request.form["password"]

        user = User.query.filter_by(reset_code=code).first()

        if not user:
            return render_template("reset_password.html", error="驗證碼錯誤")

        if datetime.now() > user.reset_code_expire:
            return render_template("reset_password.html", error="驗證碼已過期，請重新取得")

        user.set_password(new_password)
        user.reset_code = None
        user.reset_code_expire = None
        db.session.commit()

        return redirect("/login")

    return render_template("reset_password.html")
