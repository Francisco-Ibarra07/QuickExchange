import os
from quickexchange import app, db, login_manager
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
    storage_path = db.Column(db.String(), default=None)
    hashed_filename = db.Column(db.String(), default=None)
    approved_filename = db.Column(db.String(100), default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    @classmethod
    def delete(cls, data_post):
        try:
            # If the post that we are deleting happens to be a file, delete it from storage as well
            if data_post.approved_filename:
                if os.path.exists(data_post.storage_path):
                    print(f'Removing file: {data_post.hashed_filename}')
                    os.remove(data_post.storage_path)
                else:
                    print("The file does not exist")

            db.session.delete(data_post)
            db.session.commit()
        except:
            print('error on deleting post')

    @classmethod
    def create_new_url_post(cls, author, url):
        if (not author or not url):
            print(f'Invalid inputs: {author}, {url}')
            return
        
        # If we have reached our post limit, delete the oldest post
        if(len(author.posts) >= app.config['MAX_DATAPOSTS_ALLOWED']):
            deleteMe = author.posts.pop(0)
            print(f'Max post limit reached. Deleting: {deleteMe}')
            cls.delete(deleteMe)
        
        try:
            new_url_post = cls(url=url, author=author)
            db.session.add(new_url_post)
            db.session.commit()
            return new_url_post
        except:
            # TODO(FI): https://is.gd/KVemWL <-- look into errors if db throws an exception
            print("Error on adding and commiting new data post")


    @classmethod
    def create_new_file_post(cls, author, approved_filename, hashed_filename, storage_path):
        if (not author) or (not approved_filename) or (not hashed_filename) or (not storage_path):
            print(f'Invalid inputs: {author}, {approved_filename}, {hashed_filename}, {storage_path}')
            return
        
        if(len(author.posts) >= app.config['MAX_DATAPOSTS_ALLOWED']):
            deleteMe = author.posts.pop(0)
            cls.delete(deleteMe)

        try:
            new_file_post = cls(author=author, approved_filename=approved_filename, hashed_filename=hashed_filename, storage_path=storage_path)
            db.session.add(new_file_post)
            db.session.commit()
            return new_file_post
        except:
            # TODO(FI): https://is.gd/KVemWL <-- look into errors if db throws an exception
            print("Error on adding and commiting new data post")

    def __repr__(self):
        if self.url:
            return f"{self.url}"
        else:
            return f"{self.approved_filename}"

# Quick way to import models and test:
# >>> from quickexchange.models import User, DataPost
# >>> from quickexchange import db
# >>> db.create_all()
# >>> User.query.all()
# []
# >>> DataPost.query.all()
# []