from flask import render_template, url_for, flash, redirect
from quickexchange import app
from quickexchange.forms import RegistrationForm, LoginForm, URLSetterForm
from quickexchange.models import User, Post

posts = [
    {
        'author': 'Francisco Ibarra',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

url_stack = []


@app.route("/home", methods=['GET', 'POST'])
def home():
    form = URLSetterForm()

    # Return top url if pop button was pressed
    if form.pop_button.data:
        if len(url_stack) == 0:
            flash(f'No URL set yet. Type in a valid URL then hit "Push" to store it', 'danger')
        else:
            return redirect(url_stack[0])

    if form.validate_on_submit():
        # If push button was pressed, set new url
        if form.push_button.data:
            flash(f'New URL set to: {form.url.data}.')
            url_stack.insert(0, form.url.data)
        
    return render_template('home.html', form=form, history=url_stack)

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
