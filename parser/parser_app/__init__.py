import urllib

from .resultobj import ParsingResult, SingleResult
from flask import Flask, redirect, url_for, request, flash
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_admin.contrib import sqla
import logging

#logging.basicConfig(filename='/home/r/rapcooc5/mklines/public_html/parser/parser_app/logs.log', level=logging.DEBUG)

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()


# export FLASK_APP=search_and_parse
# export FLASK_ENV=development
# flask run

# from project import db, create_app, models
# db.create_all(app=create_app()) # pass the create_app result so Flask-SQLAlchemy gets the configuration.

class AdminRoleModelView(sqla.ModelView):
    # excluded_list_columns = ('password_hash',)
    def is_accessible(self):
        # print(f"[*] is accessible {current_user}")
        return current_user.is_authenticated and current_user.has_role('Admin')

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


class AdminUserModelView(sqla.ModelView):
    # excluded_list_columns = ('password_hash',)
    column_exclude_list = ('password_hash',)
    column_list = (
    'id', 'username', 'email', 'user_limit', 'limits','roles', 'created_on', 'updated_on', 'user_wallet', 'user_data')

    def is_accessible(self):
        # print(f"[*] is accessible {current_user}")
        return current_user.is_authenticated and current_user.has_role('Admin')

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            flash('Please log in first...')
            next_url = request.url
            return redirect(url_for("auth.login"))

        if current_user.has_role('Admin'):
            return super(MyAdminIndexView, self).index()
        else:
            flash('Ты, что дальтоник? Зеленый цвет от оранжевого не отличаешь?\nТолько чатланин может быть админом!')
            return redirect(url_for("main.index"))


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dfjndsf*(&^*&3424kdflksdfds78465fdsf398439802sdfsdf'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['TESTING'] = True
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='Админ парсера - ты в ответе за котиков!', template_mode='bootstrap3',
                  index_view=MyAdminIndexView())

    db.init_app(app)

    # db.create_all()
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    from .models.user_models import User, Role, roles_users
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        # return db.session.query(User).get(user_id)
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    app.jinja_env.globals.update(get_favico=get_favicon_url)
    with app.app_context():
        db.create_all()
        if not User.query.filter(User.email == 'admin@parser.ru').first():
            user = User(
                email="admin@parser.ru", username="superAdmin",
                password_hash=generate_password_hash("qwerty1#", method='sha256'),
                user_limit = 100
            )
            user.roles.append(Role(name='Admin'))
            db.session.add(user)
            db.session.commit()

        if not User.query.filter(User.email == 'user@parser.ru').first():
            user = User(
                email="user@parser.ru", username="user1",
                password_hash=generate_password_hash("123456", method='sha256')
            )
            user.roles.append(Role(name='User'))
            db.session.add(user)
            db.session.commit()
        admin.add_view(AdminUserModelView(User, db.session))
        admin.add_view(AdminRoleModelView(Role, db.session))

    return app


def get_favicon_url(single: SingleResult):
    # print("favicon", single)
    p = urllib.parse.urlparse(single.url)
    return f"https://www.google.com/s2/favicons?domain={p.scheme}://{p.netloc}"
