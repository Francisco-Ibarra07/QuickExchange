import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from quickexchange import app, bcrypt, db
from quickexchange.forms import RegistrationForm, LoginForm, UpdateAccountForm, DataPostForm, PostForm
from quickexchange.models import User, Post, DataPost
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route("/home", methods=['GET', 'POST'])
def home():
    form = DataPostForm()

    # Return top url if pop button was pressed
    if form.pop_button.data:
        last_post = DataPost.query.order_by(DataPost.id.desc()).first()
        if last_post is None:
            flash(f'No Data set yet. Set a new post then hit "Push" to store it', 'danger')
            return redirect(url_for('home'))
        elif last_post.url:
            return redirect(last_post.url)
        elif last_post.img_filename:
            image_file = url_for('static', filename='profile_pics/' + last_post.img_filename)
            return render_template('preview-media.html', title='Preview Media', image_file=image_file, history=DataPost.query.order_by(DataPost.id.desc()).all())
    
    # If push button was pressed
    elif form.push_button.data:
        if form.img.data and form.url.data:
            flash(f'Looks like you are trying to submit two things. Choose one only!', 'danger')
        elif form.url.data:
            # Create a new url post object and store it
            new_data_post = DataPost(url=form.url.data)
            db.session.add(new_data_post)
            db.session.commit()
            flash(f'New URL set to: {form.url.data}', 'success')
        elif form.img.data:
            picture_filename = save_picture(form.img.data)
            new_data_post = DataPost(img_filename=picture_filename)
            db.session.add(new_data_post)
            db.session.commit()
            flash(f'New image set!', 'success')

        return redirect(url_for('home'))
    
    return render_template('home.html', form=form, history=DataPost.query.order_by(DataPost.id.desc()).all())

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegistrationForm()
    if form.validate_on_submit(): # This tells us if our form was validated on submit

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # Decode() returns us a string
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()

        flash(f'Your account has been created! You are now able to log in', 'success') # Displays a message at the top 
        return redirect(url_for('login')) # Then we redirect the user to home page

    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next') # <-- use get() to access args dictionary so that if it DNE, it throws None
            
            if next_page is not None:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

# Randomizes picture file name to avoid collisions. Then saves image in db
def save_picture(form_picture):
    random_hex = secrets.token_hex(8) 
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)
    
    # Resize img using Pillow module
    # output_size = (125, 125)
    # i = Image.open(form_picture)
    # i.thumbnail(output_size)
    # i.save(picture_path)

    form_picture.save(picture_path)

    return picture_filename

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account')) # <-- POST GET redirect pattern. Prevents browser giving that warning that you will POST again

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form, history=DataPost.query.order_by(DataPost.id.desc()).all())

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()

    if form.validate_on_submit():
        flash('Post has been created!', 'success')
        return redirect(url_for('home'))

    return render_template('create-post.html', title='New Post', form=form)

