from quickexchange import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    # How our object is printed
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


# Post as in Blog Post (not POST http)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class DataPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), default=None)
    img_filename = db.Column(db.String(), default=None)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        if self.url:
            return f"{self.url}"
        else:
            return f"{self.img_filename}"

# Quick way to import models and test:
# >>> from quickexchange.models import User, Post, DataPost
# >>> from quickexchange import db
# >>> db.create_all()
# >>> User.query.all()
# []
# >>> DataPost.query.all()
# []