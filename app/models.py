from .data import * 
from random import SystemRandom

from base64 import b64encode, b64decode
from backports.pbkdf2 import pbkdf2_hmac, compare_digest
from flask.ext.login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func
import datetime

ROLE_USER = 0
ROLE_ADMIN = 1
FALSE = 0

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index=True, unique = True)
    email = db.Column(db.String(120), index = True, unique = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)
    zid = db.Column(db.String(10), index = True, unique = True)
    _password = db.Column(db.String(120), index = False, unique = False)
    _salt = db.Column(db.String(120))
    points = db.Column(db.Integer, default = 0)
    ctfteam = db.Column(db.SmallInteger, default=ROLE_USER)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        if self._salt is None:
            self._salt = bytes(SystemRandom().getrandbits(128))
        self._password = self._hash_password(value)

    def _hash_password(self, password):
        pwd = password.encode("utf-8")
        salt = bytes(self._salt)
        buff = pbkdf2_hmac("sha512", pwd, salt, iterations=100000)
        return b64encode(bytes(buff))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def check_password(self, password):
        new_hash = self._hash_password(password)
        return compare_digest(b64decode(new_hash), b64decode(self._password))

    def __repr__(self):
        return '<User %r>' % (self.username)
 

# https://realpython.com/blog/python/python-web-applications-with-flask-part-ii/

class Flags(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    wargame_id = db.Column(db.Integer, db.ForeignKey("wargames.id"))
    level = db.Column(db.Integer)
    flag = db.Column(db.String(120), index=True, unique=False)
    points = db.Column(db.SmallInteger)
    def __init__(self, wargame_id=None, level=None, flag=0, points=0):
      self.wargame_id = wargame_id
      self.level = level
      if flag == 0:
        self.flag = bytes(SystemRandom().getrandbits(128))
        print "setting flag to be: %s" % (self.flag)
      else:
        self.flag = flag
      self.points = points
    def __repr__(self):
      return '<Flags wid %r lvl %r flg %r pnt %r>' % (self.wargame_id, self.level, self.flag, self.points)

class Wargames(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), index=True, unique=True)
    maxlevel = db.Column(db.Integer)
    info = db.Column(db.String(120))

class Flags_scored(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    flag_id = db.Column(db.Integer, db.ForeignKey("flags.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    timestamp = db.Column(db.DateTime)
    def __init__(self, flag_id=None, user_id=None, timestamp=None):
      self.flag_id=flag_id
      self.user_id = user_id
      if timestamp is None:
        self.timestamp = func.now()
      else :
        self.timestamp = timestamp


class Flags_attempted(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    flag_id = db.Column(db.Integer, db.ForeignKey("flags.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    correct = db.Column(db.SmallInteger, default = FALSE)
    flag = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime)
    def __init__(self, flag_id=None, user_id=None,correct=0,flag=None, timestamp=None):
      self.flag_id = flag_id
      self.user_id = user_id
      self.correct = correct
      self.flag = flag
      if timestamp is None:
        self.timestamp = func.now()
      else:
        self.timestamp = timestamp

    def set_correct(self, correct=0):
      self.correct = correct

class Flags_maxlevel(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    wargame_id = db.Column(db.Integer, db.ForeignKey("wargames.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    maxlevel = db.Column(db.SmallInteger)

class Flags_proposed(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    wargame_id = db.Column(db.Integer, db.ForeignKey("wargames.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    flag_id = db.Column(db.Integer, db.ForeignKey("flags.id"))
    timestamp = db.Column(db.DateTime)
    flag = db.Column(db.String(120))

    def __init__(self, wargame_id=None, user_id=None, flag_id=None, timestamp=None, flag=None):
      self.wargame_id = wargame_id
      self.user_id = user_id
      self.flag_id = flag_id
      if timestamp is None:
        self.timestamp = func.now()
      else:
        self.timestamp = timestamp
      self.flag = flag


