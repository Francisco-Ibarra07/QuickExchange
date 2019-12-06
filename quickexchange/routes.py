import os
import jwt
import secrets
import datetime
from quickexchange import app, bcrypt, db
from quickexchange.models import User, DataPost
from quickexchange.forms import RegistrationForm, LoginForm, UpdateAccountForm, DataPostForm
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required

@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route("/home", methods=['GET', 'POST'])
def home():
    form = DataPostForm()

    # If user isn't authenticated, send to landing page
    if not current_user.is_authenticated:
        return render_template('landing-page.html')

    # Return top url if pop button was pressed
    if form.pop_button.data:
        last_post = next(reversed(current_user.posts), None)
        if last_post is None:
            flash(f'No Data set yet. Set a new post then hit "Push" to store it', 'danger')
            return redirect(url_for('home'))
        elif last_post.url:
            return redirect(last_post.url)
        elif last_post.img_filename:
            image_file = url_for('static', filename='profile_pics/' + last_post.img_filename)
            return redirect(image_file)
    
    # If push button was pressed
    elif form.push_button.data:
        if form.img.data and form.url.data:
            flash(f'Looks like you are trying to submit two things. Choose one only!', 'danger')
        elif form.url.data:
            DataPost.create_new_data_post(url=form.url.data, author=current_user)
            flash(f'New URL set to: {form.url.data}', 'success')
        elif form.img.data:
            picture_filename = save_picture(form.img.data)
            DataPost.create_new_data_post(img_filename=picture_filename, author=current_user)
            flash(f'New image set!', 'success')
        else:
            flash(f'Nothing was submitted!', 'info')
        return redirect(url_for('home'))

    history = reversed(current_user.posts) if len(current_user.posts) > 0 else None
    return render_template('home.html', form=form, history=history)

@app.route("/auth")
def authenticate():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'incorrect inputs'}), 401
    
    user = User.query.filter_by(email=auth.username).first()

    if user is None:
        return jsonify({'message': 'user does not exist!'}), 401

    # Create and return new token if credentials pass
    if bcrypt.check_password_hash(user.password, auth.password):
        token = jwt.encode({
            'user': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
        }, app.config['SECRET_KEY'])
        return jsonify({'token': token.decode('UTF-8')})
    else:
        return jsonify({'message': 'Login Unsuccessful. Please check email and password'}), 401


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

# Randomizes picture file name to avoid collisions. 
# Saves image and returns new img name
def save_picture(form_picture):
    random_hex = secrets.token_hex(8) 
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_filename)

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
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/get-latest-post")
def get_latest_post():
    # Make sure user email is passed in
    user_email = request.args.get('email')
    if user_email is None:
        return jsonify({'message': 'email not supplied'}), 400

    # Make sure user exists
    target_user = User.query.filter_by(email=user_email).first()
    if target_user is None:
        return jsonify({'message': 'user does not exist'}), 400

    # Return latest post if user exists
    latest_post = next(reversed(target_user.posts), None)
    if latest_post is None:
        return jsonify({'message': 'no posts found'})
    elif latest_post.url:
        return jsonify({
            'message': 'post found',
            'type': 'url',
            'url': latest_post.url
        }), 200
    elif latest_post.img_filename:
        img_url = url_for('static', filename='profile_pics/' + latest_post.img_filename)
        url_for_TESTING = f'http://127.0.0.1:5000{img_url}'
        return jsonify({
            'message': 'post found',
            'type': 'url',
            'url': url_for_TESTING
        }), 200
    else:
        return jsonify({'message': 'error: couldnt determine if url or image file'}), 500

# Inputs -> File and form data
# In betwee, -> Validate file(s) and user. Store new file if its correct
# Output -> Sucess or failure message
@app.route("/create-file-post", methods=['GET', 'POST'])
def create_file_post():
    
    # Get input files
    request_file_data = request.files
    request_form_data = request.form
    print(request_file_data)
    print(request_form_data)

    if request_file_data is None or request_form_data is None:
        print('no file data or form data supplied')
        return jsonify({'message': 'no files or form data supplied'}), 400
    
    # Make sure an email is provided so we can find the user
    # Make sure an actual file is passed in
    file = request_file_data.get("file")
    user_email = request_form_data.get("email")
    if file is None or user_email is None:
        print('no file or email supplied')
        return jsonify({'message': 'no file or email was supplied'}), 400
    
    # Make sure user exists
    target_user = User.query.filter_by(email=user_email).first()
    if target_user is None:
        print('user does not exist')
        return jsonify({'message': 'user does not exist'}), 400
    
    # Save the new datapost and author it with the requested user
    try:
        # TODO(FI): Save image to a better location and check for validation of file (i.e file name, size, extension type)
        # Also delete image from folder once it comes time to DELETE!
        picture_filename = save_picture(file)
        DataPost.create_new_data_post(img_filename=picture_filename, author=target_user)
        return jsonify({'message': 'new post created'}), 200
    except:
        print('error on creating new post')
        return jsonify({'message': 'error on creating new post'}), 500  

# Inputs -> url key
# In Between-> Validate input, and store url if correct
# Output -> success or failure message
@app.route("/create-url-post", methods=['GET','POST'])
def create_url_post():
    
    # Have silent set to true so it can return None if DNE
    request_data = request.get_json(silent=True)
    if request_data is None:
        print('no data supplied')
        return jsonify({'message': 'no data supplied'}), 400

    # Make sure an email is provided so we can find the user
    if 'email' not in request_data:
        print('email not supplied')
        return jsonify({'message': 'email not supplied'}), 400

    # Make sure either url or file is given (but not both)
    if 'url' not in request_data:
        return jsonify({'message': 'url was not supplied'}), 400

    # Make sure user exists
    user_email = request_data['email']
    target_user = User.query.filter_by(email=user_email).first()
    if target_user is None:
        print('user does not exist')
        return jsonify({'message': 'user does not exist'}), 400
    
    # Save the new datapost and author it with the requested user
    try:
        print(f'url supplied: {request_data["url"]}')
        DataPost.create_new_data_post(url=request_data['url'], author=target_user)
        return jsonify({
            'message': 'new post created',
            'url': request_data['url']
        }), 200
    except:
        print('error on creating new post')
        return jsonify({'message': 'error on creating new post'}), 500
