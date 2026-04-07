from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Length, Email, EqualTo
PASS_LENGTH_MIN = 6


class SignupUserForm(FlaskForm):
    username = StringField(label=('Введите имя:'),
                           validators=[DataRequired(),
                                       Length(min=3, max=64,
                                              message='Длина имени должна быть между %(min)d и %(max)d символами')])
    email = StringField(label=('Email'), validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(label=('дер пароль'),
                             validators=[DataRequired(),
                                         Length(min=PASS_LENGTH_MIN,
                                                message='Пароль должен быть не менее %(min)d символов, вы слышали о PBKDF2?')])

    confirm_password = PasswordField(
        label=('пароль еще разочек, это всегда приятно'),
        validators=[DataRequired(message='*Required'),
                    EqualTo('password', message='Пароли должны совпадать, как ни странно!')])
    submit = SubmitField(label=('ОК'))

    def validate_username(self, username):
        excluded_chars = " *?!'^+%&/()=}][{$#"
        for char in self.username.data:
            if char in excluded_chars:
                raise ValidationError(
                    f"Символ {char} не может присутствовать в имени.")

    def validate_password(self, password):
        psw = password.data
        if psw.isnumeric() or psw.isalpha() or psw.lower() == psw or psw.upper() == psw:
            raise ValidationError(
                f"пароль должен содержать мешанину из букв разного регистра и цифр, да нас тоже это бесит, но это мы еще спецсимволы не включили")


class LoginUserForm(FlaskForm):
    email = StringField(label=('Email'), validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField(label=('дер пароль'),
                             validators=[DataRequired(),
                                         Length(min=PASS_LENGTH_MIN,
                                                message='Пароль должен быть не менее %(min)d символов, вы слышали о PBKDF2?')])
    remember_me = BooleanField(label=('Запомнить меня'))
    submit = SubmitField(label=('ОК'))


