from flask import Flask, render_template, redirect
from extensions import db, login_manager
from faker import Faker
import random, json, os
from flask_login import logout_user

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "campushub-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///campushub.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    # Models
    from models.post import Post
    from models.user import User

    # Blueprints
    from routes.auth import auth_bp
    from routes.posts import posts_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)

    # -------------------------------------------------
    # ⭐ 1. 強制首頁 → 登入頁
    # -------------------------------------------------
    @app.route("/")
    def force_login():
        return redirect("/login")

    # -------------------------------------------------
    # 2. 訪客模式（強制登出 → 未登入狀態）
    # -------------------------------------------------
    @app.route("/guest")
    def guest_mode():
        logout_user()
        return redirect("/home")

    # -------------------------------------------------
    # 3. 首頁（無限滾動載入文章）
    # -------------------------------------------------
    @app.route("/home")
    def home():
        return render_template("index.html")

    # -------------------------------------------------
    # Database Initialization
    # -------------------------------------------------
    with app.app_context():
        db.create_all()

        fake = Faker("en_US")

        # 生成假使用者
        if User.query.count() < 30:
            print("⚙ Generating 30 English users...")
            for _ in range(30):
                name = fake.name()
                password = "123456"
                if not User.query.filter_by(username=name).first():
                    user = User(username=name)
                    user.set_password(password)
                    db.session.add(user)
            db.session.commit()
            print("✔ Users generated.")

        users = User.query.all()

        # 讀取 JSON 文章
        json_path = os.path.join(os.path.dirname(__file__), "data/english_articles.json")
        with open(json_path, "r", encoding="utf-8") as f:
            articles = json.load(f)

        # 初次載入假文章
        if Post.query.count() == 0:
            print("⚙ Importing tagged articles...")

            for article in articles:
                author = random.choice(users)
                post = Post(
                    title=article["title"],
                    content=article["content"],
                    tag=article.get("tag", "Life"),  #新增 TAG
                    user_id=author.id
                )
                db.session.add(post)

            db.session.commit()
            print("✔ Successfully imported tagged articles!")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
