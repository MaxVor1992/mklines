from flask_login import UserMixin

# db = SQLAlchemy()
# SQLAlchemy.create_engine("sqlite:///users.db")
from werkzeug.security import generate_password_hash, check_password_hash

from .. import db
import datetime

roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('roles.id'))
)


class Role(db.Model):
    """Модель роли пользователя"""
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name


class User(db.Model, UserMixin):
    """Модель пользователя"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_limit = db.Column(db.Integer, default=0)
    user_wallet = db.Column(db.Integer, default=0)
    user_data = db.Column(db.String(256))
    created_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    active = db.Column(db.Boolean(), default=True)

    # Для получения доступа к связанным объектам
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    # @property
    # def limits(self):
    #     return self.user_limit

    @property
    def limits(self):
        return self.user_limit

    @limits.setter
    def limits(self, v):
        if not self.has_role('Admin'):
            self.user_limit = v

    @limits.getter
    def limits(self):
        if self.has_role('Admin'):
            return 100
        else:
            return self.user_limit

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def __unicode__(self):
        return self.username

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def has_role(self, *args):
        # print(f"[*] role checked [{args}]")
        return set(args).issubset({role.name for role in self.roles})

    def __repr__(self):
        return '<User {}>'.format(self.username)

