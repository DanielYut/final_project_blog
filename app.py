from flask import Flask, render_template, redirect
from extensions import db, login_manager, mail
from faker import Faker
import random, json, os
from flask_login import logout_user
from flask_mail import Mail


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "campushub-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///campushub.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Email Config
    app.config["MAIL_SERVER"] = "smtp.gmail.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USERNAME"] = "daniel950401@gmail.com"   
    app.config["MAIL_PASSWORD"] = "dmoi ylhi uaib tldg"           
    app.config["MAIL_DEFAULT_SENDER"] = "daniel950401@gmail.com"   

    # Init extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # Models
    from models.post import Post
    from models.user import User
    

    # Blueprints
    from routes.auth import auth_bp
    from routes.posts import posts_bp
    from routes.reset import reset_bp
    from routes.likes import likes_bp
    

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(reset_bp)
    app.register_blueprint(likes_bp)

    # ---------------------------
    # Routes
    # ---------------------------

    @app.route("/")
    def force_login():
        return redirect("/login")

    @app.route("/guest")
    def guest_mode():
        logout_user()
        return redirect("/home")

    @app.route("/home")
    def home():
        return render_template("index.html")

    # ---------------------------
    # Database Initialization
    # ---------------------------
    with app.app_context():
        db.create_all()

        fake = Faker("en_US")

        # Fake Users
        if User.query.count() < 30:
            print("Generating fake users...")
            for _ in range(30):
                name = fake.name()
                if not User.query.filter_by(username=name).first():
                    user = User(username=name, email=fake.email())
                    user.set_password("123456")
                    db.session.add(user)
            db.session.commit()

        users = User.query.all()

        # Load article data
        json_path = os.path.join(os.path.dirname(__file__), "data/english_articles.json")
        with open(json_path, "r", encoding="utf-8") as f:
            articles = json.load(f)

        if Post.query.count() == 0:
            print("Importing articles...")
            for article in articles:
                author = random.choice(users)
                post = Post(
                    title=article["title"],
                    content=article["content"],
                    tag=article.get("tag", "Life"),
                    user_id=author.id
                )
                db.session.add(post)
            db.session.commit()
            print("Imported.")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
