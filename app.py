from flask import Flask, render_template
from config import Config
from extensions import db, login_manager

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "campushub-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///campushub.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)

    # 載入 Blueprint
    from routes.auth import auth_bp
    from routes.posts import posts_bp  

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)   

    # 首頁
    @app.route("/")
    def index():
        from models.post import Post
        posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
        return render_template("index.html", posts=posts)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
