from flask import Blueprint, render_template, request, redirect
from flask_login import login_required, current_user
from models.post import Post
from models.comment import Comment
from extensions import db

posts_bp = Blueprint("posts", __name__)

# -------------------------------------------------
# 文章列表頁
# -------------------------------------------------
@posts_bp.route("/posts")
def list_posts():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("post_list.html", posts=posts)


# -------------------------------------------------
# 單篇文章（含留言功能）
# -------------------------------------------------
@posts_bp.route("/posts/<int:post_id>", methods=["GET", "POST"])
def view_post(post_id):
    post = Post.query.get_or_404(post_id)

    # 新增留言
    if request.method == "POST":
        content = request.form["content"]

        # 登入使用 username，否則顯示「訪客」
        author = current_user.username if current_user.is_authenticated else "訪客"

        new_comment = Comment(
            content=content,
            author=author,
            post_id=post.id
        )

        db.session.add(new_comment)
        db.session.commit()

        return redirect(f"/posts/{post_id}")

    return render_template("post_view.html", post=post)


# -------------------------------------------------
# 建立文章（需登入）
# -------------------------------------------------
@posts_bp.route("/posts/create", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        tag = request.form["tag"]

        new_post = Post(
            title=title,
            content=content,
            tag=tag,
            user_id=current_user.id
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect("/home")

    return render_template("post_create.html")


# -------------------------------------------------
# API：無限捲動文章（含分類過濾與留言數）
# -------------------------------------------------
@posts_bp.route("/api/posts")
def api_posts():
    page = int(request.args.get("page", 1))
    tag = request.args.get("tag", "")
    per_page = 10

    query = Post.query.order_by(Post.created_at.desc())

    if tag:
        query = query.filter_by(tag=tag)

    posts = query.paginate(page=page, per_page=per_page, error_out=False)

    data = []
    for p in posts.items:
        data.append({
            "id": p.id,
            "title": p.title,
            "content": p.content[:80] + "...",
            "author": p.user.username,
            "tag": p.tag,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
            "comment_count": len(p.comments),
            "like_count": p.likes.count()
        })

    return {"posts": data, "has_next": posts.has_next}


# -------------------------------------------------
# 單一分類頁
# -------------------------------------------------
@posts_bp.route("/tag/<tag>")
def posts_by_tag(tag):
    posts = Post.query.filter_by(tag=tag).order_by(Post.created_at.desc()).all()
    return render_template("tag_view.html", posts=posts, tag=tag)


# -----------------------------------------------------------
# API：搜尋功能（先搜尋標題，再搜尋內容）
# -----------------------------------------------------------
@posts_bp.route("/api/search")
def api_search():
    keyword = request.args.get("q", "").strip()

    if not keyword:
        return {"posts": []}

    # 先搜尋標題
    title_results = Post.query.filter(
        Post.title.ilike(f"%{keyword}%")
    ).order_by(Post.created_at.desc()).all()

    if len(title_results) > 0:
        posts = title_results
    else:
        # 標題找不到 → fallback 搜尋內容
        posts = Post.query.filter(
            Post.content.ilike(f"%{keyword}%")
        ).order_by(Post.created_at.desc()).all()

    # 整理搜尋結果
    data = []
    for p in posts:
        data.append({
            "id": p.id,
            "title": p.title,
            "author": p.user.username,
            "tag": p.tag,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
            "content": p.content[:80] + "...",
            "comment_count": len(p.comments),
            "like_count": p.likes.count()
        })

    return {"posts": data}
