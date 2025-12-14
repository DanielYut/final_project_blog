from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.like import Like
from models.post import Post

likes_bp = Blueprint("likes", __name__)

@likes_bp.route("/api/posts/<int:post_id>/like", methods=["POST"])
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)

    like = Like.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if like:
        db.session.delete(like)
        liked = False
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        liked = True

    db.session.commit()

    return jsonify({
        "liked": liked,
        "like_count": post.likes.count()
    })