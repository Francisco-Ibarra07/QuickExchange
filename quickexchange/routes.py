import os
import jwt
import secrets
import datetime
from werkzeug.utils import secure_filename
from quickexchange import app, bcrypt, db
from quickexchange.models import User, DataPost
from quickexchange.forms import (
    RegistrationForm,
    LoginForm,
    UpdateAccountForm,
    DataPostForm,
)
from flask import Markup
from flask import render_template, url_for, flash, redirect, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
def root():
    return redirect(url_for("home"))


@app.route("/home", methods=["GET", "POST"])
def home():
    form = DataPostForm()

    # If user isn't authenticated, send to landing page
    if not current_user.is_authenticated:
        return render_template("landing-page.html", title="Welcome")

    # Return top url if pop button was pressed
    if form.pop_button.data:
        latest_post = next(reversed(current_user.posts), None)
        if latest_post is None:
            flash(
                f'No Data set yet. Set a new post then hit "Push" to store it', "danger"
            )
            return redirect(url_for("home"))
        elif latest_post.url:
            return redirect(latest_post.url)
        elif latest_post.approved_filename:
            file_url = url_for(
                "static", filename="uploads/" + latest_post.hashed_filename
            )
            return redirect(file_url)

    # If push button was pressed
    elif form.push_button.data:
        if form.file.data and form.url.data:
            flash(
                f"Looks like you are trying to submit two things. Choose one only!",
                "danger",
            )
        elif form.url.data:
            DataPost.create_new_url_post(url=form.url.data, author=current_user)
            flash(f"New URL set to: {form.url.data}", "success")
        elif form.file.data:
            # Validate file input
            file = form.file.data
            approved_filename = ""
            hashed_filename = ""
            filepath_for_storage = ""
            if allowed_file(file.filename):
                approved_filename = secure_filename(file.filename)
                random_hex = secrets.token_hex(16)
                f_name, f_ext = os.path.splitext(approved_filename)
                hashed_filename = random_hex + f_ext
                filepath_for_storage = os.path.join(
                    app.config["FILE_UPLOAD_PATH"], hashed_filename
                )
                file.save(filepath_for_storage)
                DataPost.create_new_file_post(
                    author=current_user,
                    approved_filename=approved_filename,
                    hashed_filename=hashed_filename,
                    storage_path=filepath_for_storage,
                )
                flash(f"New file set to: {approved_filename}", "success")
            else:
                flash(f"That file extension is not allowed!", "danger")
                msg = Markup(
                    "You can find the list of allowed file extensions here: "
                    + "<a target='_blank' href='http://localhost:5000/about'>Allowed File Extensions</a>"
                )
                flash(msg, "warning")

        else:
            flash(f"There is nothing to push!", "info")
        return redirect(url_for("home"))

    history = reversed(current_user.posts) if len(current_user.posts) > 0 else None
    return render_template(
        "home.html",
        title="Home",
        form=form,
        history=history,
        max_dataposts_allowed=app.config["MAX_DATAPOSTS_ALLOWED"],
    )


@app.route("/auth")
def authenticate():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"message": "incorrect inputs"}), 401

    user = User.query.filter_by(email=auth.username).first()

    if user is None:
        return jsonify({"message": "user does not exist!"}), 401

    # Create and return new token if credentials pass
    if bcrypt.check_password_hash(user.password, auth.password):
        token = jwt.encode(
            {
                "user": user.email,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
            },
            app.config["SECRET_KEY"],
        )
        return jsonify({"token": token.decode("UTF-8")})
    else:
        return (
            jsonify({"message": "Login Unsuccessful. Please check email and password"}),
            401,
        )


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()
    if form.validate_on_submit():  # This tells us if our form was validated on submit

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )  # Decode() returns us a string
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_pw
        )
        db.session.add(user)
        db.session.commit()

        login_user(user)
        flash(
            f"Your account has been created!", "success"
        )  # Displays a message at the top
        return redirect(url_for("home"))  # Then we redirect the user to home page

    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")

            if next_page is not None:
                return redirect(next_page)
            else:
                return redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")

    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            img_file = form.picture.data
            random_hex = secrets.token_hex(16)
            f_name, f_ext = os.path.splitext(secure_filename(img_file.filename))
            new_img_filename = random_hex + f_ext
            img_storage_path = os.path.join(
                app.root_path, "static/profile_pics", new_img_filename
            )
            img_file.save(img_storage_path)

            # Delete the old profile picture if its not the default one
            if current_user.image_file != "default.jpg":
                old_img_file = current_user.image_file
                old_img_file_path = os.path.join(
                    app.root_path, "static/profile_pics", old_img_file
                )
                if os.path.exists(old_img_file_path):
                    os.remove(old_img_file_path)

            current_user.image_file = new_img_filename

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(
            url_for("account")
        )  # <-- POST GET redirect pattern. Prevents browser giving that warning that you will POST again

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/get-latest-post")
def get_latest_post():
    # Make sure user email is passed in
    user_email = request.args.get("email")
    if user_email is None:
        return jsonify({"message": "email not supplied"}), 400

    # Make sure user exists
    target_user = User.query.filter_by(email=user_email).first()
    if target_user is None:
        return jsonify({"message": "user does not exist"}), 400

    # Return latest post if user exists
    latest_post = next(reversed(target_user.posts), None)
    if latest_post is None:
        return jsonify({"message": "no posts found"})
    elif latest_post.url:
        return (
            jsonify({"message": "post found", "type": "url", "url": latest_post.url}),
            200,
        )
    elif latest_post.approved_filename:
        file_path = url_for("static", filename="uploads/" + latest_post.hashed_filename)
        url_for_TESTING = f"http://127.0.0.1:5000{file_path}"
        return (
            jsonify({"message": "post found", "type": "url", "url": url_for_TESTING}),
            200,
        )
    else:
        return (
            jsonify({"message": "error: couldnt determine if url or image file"}),
            500,
        )


# Inputs -> File and form data
# In betwee, -> Validate file(s) and user. Store new file if its correct
# Output -> Sucess or failure message
@app.route("/create-file-post", methods=["GET", "POST"])
def create_file_post():

    # Get input files
    request_file_data = request.files
    request_form_data = request.form

    # Make sure request contains file and form data
    if request_file_data is None or request_form_data is None:
        print("no file data or form data supplied")
        return jsonify({"message": "no files or form data supplied"}), 400

    # Make sure an email is provided so we can find the user
    # Make sure an actual file is passed in
    file = request_file_data.get("file")
    user_email = request_form_data.get("email")
    if file is None or user_email is None:
        print("no file or email supplied")
        return jsonify({"message": "no file or email was supplied"}), 400

    # Validate file input
    approved_filename = ""
    hashed_filename = ""
    filepath_for_storage = ""
    if allowed_file(file.filename):
        approved_filename = secure_filename(file.filename)
        random_hex = secrets.token_hex(16)
        f_name, f_ext = os.path.splitext(approved_filename)
        hashed_filename = random_hex + f_ext
        filepath_for_storage = os.path.join(
            app.config["FILE_UPLOAD_PATH"], hashed_filename
        )

    else:
        print("file extension given is not supported")
        return jsonify({"message": "file extension given is not supported"}), 400

    # Make sure user exists
    target_user = User.query.filter_by(email=user_email).first()
    if target_user is None:
        print("user does not exist")
        return jsonify({"message": "user does not exist"}), 400

    # Save the new file (with approved_filename) and author it with the requested user
    try:
        file.save(filepath_for_storage)
        DataPost.create_new_file_post(
            author=target_user,
            approved_filename=approved_filename,
            hashed_filename=hashed_filename,
            storage_path=filepath_for_storage,
        )

        return jsonify({"message": "new post created"}), 200
    except:
        print("error on creating new post")
        return jsonify({"message": "error on creating new post"}), 500


def allowed_file(filename):
    ext = filename.rsplit(".", 1)[1].lower()
    print(f"filetype saw: {ext}")
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_FILE_EXTENSIONS"]
    )


# Inputs -> url key
# In Between-> Validate input, and store url if correct
# Output -> success or failure message
@app.route("/create-url-post", methods=["GET", "POST"])
def create_url_post():

    # Have silent set to true so it can return None if DNE
    request_data = request.get_json(silent=True)
    if request_data is None:
        print("no data supplied")
        return jsonify({"message": "no data supplied"}), 400

    # Make sure an email is provided so we can find the user
    if "email" not in request_data:
        print("email not supplied")
        return jsonify({"message": "email not supplied"}), 400

    # Make sure either url or file is given (but not both)
    if "url" not in request_data:
        return jsonify({"message": "url was not supplied"}), 400

    # Make sure user exists
    user_email = request_data["email"]
    target_user = User.query.filter_by(email=user_email).first()
    if target_user is None:
        print("user does not exist")
        return jsonify({"message": "user does not exist"}), 400

    # Save the new datapost and author it with the requested user
    try:
        print(f'url supplied: {request_data["url"]}')
        DataPost.create_new_url_post(url=request_data["url"], author=target_user)
        return jsonify({"message": "new post created", "url": request_data["url"]}), 200
    except:
        print("error on creating new post")
        return jsonify({"message": "error on creating new post"}), 500

