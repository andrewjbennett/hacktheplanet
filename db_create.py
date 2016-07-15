import psycopg2
from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import app
from app.data import db
import os.path

db.init_app(app)
with app.app_context():
    db.create_all()

    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
      api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
      api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    else:
      api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

