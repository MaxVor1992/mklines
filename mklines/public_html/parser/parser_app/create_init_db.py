import os
from search_and_parse import db, create_app
from werkzeug.security import generate_password_hash, check_password_hash

os.remove("db.sqlite")

db.create_all(app=create_app())  # pass the create_app result so Flask-SQLAlchemy gets the configuration.

from models.user_models import User, Role

if not User.query.filter(User.email == 'admin@parser.ru').first():
    user = User(
        email="admin@parser.ru", username="superAdmin",
        password_hash=generate_password_hash("qwerty1#", method='sha256')
    )
    user.roles.append(Role(name='Admin'))
    db.session.add(user)
    db.session.commit()

if not User.query.filter(User.email == 'user@parser.ru').first():
    user = User(
        email="user@parser.ru", username="user1", password_hash=generate_password_hash("123456", method='sha256')
    )
    user.roles.append(Role(name='User'))
    db.session.add(user)
    db.session.commit()
