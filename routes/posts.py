from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from models.post import Post
from extensions import db

posts_bp = Blueprint("posts", __name__)

# 文章列表
@posts_bp.route("/posts")
def list_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("post_list.html", posts=posts)


# 單篇文章
@posts_bp.route("/posts/<int:post_id>")
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post_view.html", post=post)


# 建立文章（需登入）
@posts_bp.route("/posts/create", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        new_post = Post(
            title=title,
            content=content,
            user_id=current_user.id
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect("/")

    return render_template("post_create.html")
