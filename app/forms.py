# -*- coding: utf-8 -*-

from app import *
from wtforms.validators import Required, Email, Length, NumberRange, ValidationError
from wtforms import Form, TextField, BooleanField, TextAreaField, PasswordField,IntegerField, SelectField, SubmitField
from flask.ext.wtf.recaptcha import RecaptchaField
from config import *


def not_null_value(form, field):

    if field.data == "null":
        raise ValidationError(u'Моля изберете валидна опция')



class LoginForm(Form):
    user_email = TextField('email', validators=[Required(message=u'Write your email here'), Email(message=u"Write your email here"),Length(min=5, message=u'Invalid email')])


class RegisterForm(Form):
    user_email = TextField('email', validators=[Required(message=u'Write your email here'), Email(message=u"Write your email here"),Length(min=5, message=u'Write your email here')])
    website = TextField('website', validators=[Required(message=u'Website'), Length(min=3, message=u'Website')])
