from flask.ext.wtf import Form
from wtforms import IntegerField, TextField, BooleanField, PasswordField
from wtforms.validators import Required, ValidationError
from .models import *
from .data import db

class LoginForm(Form):
    username = TextField('username', validators = [Required()])
    password = PasswordField('password', validators = [Required()])
    remember_me = BooleanField('remember_me', default = False)

    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False
        
        user = User.query.filter(User.username==self.username.data).first()
        if user is None:
            self.username.errors.append('Unknown username')
            return False
        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True



class RegistrationForm(Form):
  username = TextField('username')
  email = TextField('email address')
  zid = TextField('zid eg z1234567')
  password = PasswordField('password')
  ctfteam = BooleanField('ctfteam', default=False)

  def validate_email(form, field):
    user = User.query.filter(User.email == field.data).first()
    if user is not None:
      raise ValidationError("A user with that email already exists")
  
  def validate_zid(form, field):
    user = User.query.filter(User.zid == field.data).first()
    if user is not None:
      raise ValidationError("A user with that zid already exists")
  
class AddWargameForm(Form):
  name = TextField('wargame name')
  maxlevel = IntegerField('max levels')
  info = TextField('info')

  def validate_name(form, field):
    name = Wargames.query.filter(Wargames.name == field.name).first()
    if name is not None:
        raise ValidationError("A wargame with this name alreay exists")

class EditWargameForm(Form):
  name = TextField('wargame name')
  maxlevel = IntegerField('max levels')
  info = TextField('info')

class EditLevelForm(Form):
  flag = TextField('password')
  points = IntegerField('number of points')
  level = IntegerField('level')


class AddAdminForm(Form):
  username = TextField('username')
  make_admin = BooleanField('make admin', default = False)

class SubmitFlagForm(Form):
  flag = TextField('flag')

class ProposeFlagForm(Form):
  flag = TextField('password')
