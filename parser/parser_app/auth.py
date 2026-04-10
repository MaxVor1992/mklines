from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from .models import user_models
from flask_login import login_user, login_required, logout_user
from .parser_forms import SignupUserForm, LoginUserForm

auth = Blueprint('auth', __name__)


# @auth.route('/admin')
# @roles_required("Admin")
# def admin_panel():
#     return render_template('index.html')

@auth.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginUserForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        remember = form.remember_me.data
        user = user_models.User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash('Проверьте логин и пароль и попытайтесь снова')
            # return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page
            return render_template('forms/login_form.html', form=form)

        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        return redirect(url_for('main.index'))

    return render_template('forms/login_form.html', form=form)


# @auth.route('/login')
# def login():
#     return render_template('login.html')
#
# @auth.route('/login', methods=['POST'])
# def login_post():
#     email = request.form.get('email')
#     password = request.form.get('password')
#     remember = True if request.form.get('remember') else False
#
#     user = user_models.User.query.filter_by(email=email).first()
#
#     # check if the user actually exists
#     # take the user-supplied password, hash it, and compare it to the hashed password in the database
#     if not user or not check_password_hash(user.password_hash, password):
#         flash('Please check your login details and try again.')
#         return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page
#
#     # if the above check passes, then we know the user has the right credentials
#     login_user(user, remember=remember)
#     return redirect(url_for('main.index'))

# @auth.route('/signup')
# def signup():
#     return render_template('signup.html')
#
# @auth.route('/signup', methods=['POST'])
# def signup_post():
#     email = request.form.get('email')
#     name = request.form.get('name')
#     password = request.form.get('password')
#
#     user = user_models.User.query.filter_by(
#         email=email).first()  # if this returns a user, then the email already exists in database
#
#     if user:  # if a user is found, we want to redirect back to signup page so user can try again
#         flash(f'Email address {email} already exists')
#         return redirect(url_for('auth.signup'))
#
#     # create a new user with the form data. Hash the password so the plaintext version isn't saved.
#     new_user = user_models.User(email=email, username=name, password_hash=generate_password_hash(password, method='sha256'))
#     role = user_models.Role.query.filter_by(name='User').one()
#     new_user.roles.append(role)
#     # add the new user to the database
#     db.session.add(new_user)
#     db.session.commit()
#     return redirect(url_for('auth.login'))


@auth.route('/signup', methods=('GET', 'POST'))
def signup():
    form = SignupUserForm()
    if form.validate_on_submit():
        email = form.email.data
        name = form.username.data
        password = form.password.data
        user = user_models.User.query.filter_by(
            email=email).first()  # if this returns a user, then the email already exists in database

        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            flash(f'Email address {email} already exists')
            return render_template('forms/signup_form.html', form=form)

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = user_models.User(email=email, username=name,
                                    password_hash=generate_password_hash(password), limits=100)
        role = user_models.Role.query.filter_by(name='User').one()
        new_user.roles.append(role)
        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('forms/signup_form.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
