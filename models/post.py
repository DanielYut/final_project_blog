from extensions import db
from datetime import datetime
from models.like import Like

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)

    tag = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="posts")
    comments = db.relationship("Comment", backref="post", cascade="all, delete")
    likes = db.relationship("Like", backref="post", lazy="dynamic")

    @property
    def like_count(self):
        return Like.query.filter_by(post_id=self.id).count()