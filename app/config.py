import os
basedir = os.path.abspath(os.path.dirname(__file__))
# configuration
DATABASE = 'hacktheplanet.db'
DEBUG = True
CSRF_ENABLED = True
SECRET_KEY = "redacted"
USERNAME = "redacted"
PASSWORD = "redacted"

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URI']

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


