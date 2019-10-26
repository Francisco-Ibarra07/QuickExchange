from flask import render_template, url_for, flash, redirect
from quickexchange import app, db
from quickexchange.forms import RegistrationForm, LoginForm, URLSetterForm
from quickexchange.models import User, Post, URLPost

url_stack = []

@app.route('/')
def root():
    return redirect(url_for('home'))

@app.route("/home", methods=['GET', 'POST'])
def home():
    form = URLSetterForm()

    # Return top url if pop button was pressed
    if form.pop_button.data:
        last_url = URLPost.query.order_by(URLPost.id.desc()).first()
        print(last_url)
        if not last_url:
            flash(f'No URL set yet. Type in a valid URL then hit "Push" to store it', 'danger')
        else:
            return redirect(last_url)

    if form.validate_on_submit():
        # If push button was pressed, set new url
        if form.push_button.data:

            # Create a new url post object and store it
            new_url_post = URLPost(url=form.url.data)
            db.session.add(new_url_post)
            db.session.commit()

            flash(f'New URL set to: {form.url.data}.')
    
    return render_template('home.html', form=form, history=URLPost.query.order_by(URLPost.id.desc()).all())

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit(): # This tells us if our form was validated on submit
        flash(f'Account created for {form.username.data}', 'success') # Displays a message at the top 
        return redirect(url_for('home')) # Then we redirect the user to home page

    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # If form was submitted correctly
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html', title='Login', form=form)
