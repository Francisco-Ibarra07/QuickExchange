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
    posts = db.relationship('DataPost', backref='author', lazy=True)

    # How our object is printed
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class DataPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), default=None)
    img_filename = db.Column(db.String(), default=None)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @classmethod
    def create_new_data_post(cls, author, url=None, img_filename=None):
        if (url is None) and (img_filename is None):
            print("Both args are None")
            return
        
        # Check size of current posts
        # If greater than max posts, delete the oldest
        max_posts = 10
        # TODO(FI): If deleting something like a file, delete it from storage also
        if (len(author.posts) >= max_posts):
            print(f'From {author.posts}')
            print(f'Deleting: {author.posts[0]}')
            deleteMe = author.posts.pop(0)
            db.session.delete(deleteMe)

        # Add new url or file post
        new_data_post = None
        if url is not None:
            new_data_post = cls(url=url, author=author)
        elif img_filename is not None:
            new_data_post = cls(img_filename=img_filename, author=author)
        
        try:
            db.session.add(new_data_post)
            db.session.commit()
            return new_data_post
        except:
            print("Error on adding and commiting new data post")

    def __repr__(self):
        if self.url:
            return f"{self.url}"
        else:
            return f"{self.img_filename}"

# Post as in Blog Post (not POST http)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# Quick way to import models and test:
# >>> from quickexchange.models import User, Post, DataPost
# >>> from quickexchange import db
# >>> db.create_all()
# >>> User.query.all()
# []
# >>> DataPost.query.all()
# []