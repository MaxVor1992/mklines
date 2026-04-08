# -*- coding: utf-8 -*-
import urllib
from functools import lru_cache

from .resultobj import ParsingResult, SingleResult
from flask import Flask, redirect, url_for, request, flash, g
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, expose
from flask_admin.contrib import sqla
from dotenv import load_dotenv
import os
import logging
from logging.handlers import RotatingFileHandler

# Загружаем переменные окружения
load_dotenv()

# Инициализация расширений
db = SQLAlchemy()

def get_favicon_url(single):
    """Получение favicon для URL"""
    p = urllib.parse.urlparse(single.url)
    return f"https://www.google.com/s2/favicons?domain={p.scheme}://{p.netloc}"


class AdminRoleModelView(sqla.ModelView):
    """Представление администрирования для ролей"""
    
    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('Admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class AdminUserModelView(sqla.ModelView):
    """Представление администрирования для пользователей"""
    column_exclude_list = ('password_hash',)
    column_list = (
        'id', 'username', 'email', 'user_limit', 'limits', 'roles', 
        'created_on', 'updated_on', 'user_wallet', 'user_data'
    )

    def is_accessible(self):
        return current_user.is_authenticated and current_user.has_role('Admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))


class MyAdminIndexView(AdminIndexView):
    """Кастомная главная страница админки"""
    
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            flash('Please log in first...')
            return redirect(url_for("auth.login"))

        if current_user.has_role('Admin'):
            return super(MyAdminIndexView, self).index()
        else:
            flash('Только администраторы имеют доступ к этой странице!')
            return redirect(url_for("main.index"))


def create_app(config_object=None):
    """Фабрика приложений Flask с правильной конфигурацией"""
    app = Flask(__name__)

    # Конфигурация приложения
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    
    # Настройки таймаутов запросов
    app.config['REQUEST_TIMEOUT'] = int(os.environ.get('REQUEST_TIMEOUT', 30))
    app.config['MAX_WORKERS'] = int(os.environ.get('MAX_WORKERS', 4))
    
    # Инициализация админки
    admin = Admin(
        app, 
        name='Админ парсера', 
        index_view=MyAdminIndexView()
    )

    # Инициализация расширений
    db.init_app(app)

    # Настройка логирования
    if not app.debug:
        file_handler = RotatingFileHandler(
            'parser.log', 
            maxBytes=10240, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Parser application startup')

    # Инициализация Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models.user_models import User, Role, roles_users
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Регистрация blueprint'ов
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    # Добавляем глобальную функцию для шаблонов
    app.jinja_env.globals.update(get_favico=get_favicon_url)

    # Инициализация БД и создание тестовых пользователей
    with app.app_context():
        db.create_all()
        
        # Создаем админа если не существует
        if not User.query.filter(User.email == 'admin@parser.ru').first():
            user = User(
                email="admin@parser.ru", 
                username="superAdmin",
                password_hash=generate_password_hash("qwerty1#", method='sha256'),
                user_limit=100
            )
            user.roles.append(Role(name='Admin'))
            db.session.add(user)
            db.session.commit()

        # Создаем тестового пользователя если не существует
        if not User.query.filter(User.email == 'user@parser.ru').first():
            user = User(
                email="user@parser.ru", 
                username="user1",
                password_hash=generate_password_hash("123456", method='sha256')
            )
            user.roles.append(Role(name='User'))
            db.session.add(user)
            db.session.commit()
            
        # Добавляем представления в админку
        admin.add_view(AdminUserModelView(User, db.session))
        admin.add_view(AdminRoleModelView(Role, db.session))

    return app
