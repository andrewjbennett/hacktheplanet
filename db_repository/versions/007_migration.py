from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
flags = Table('flags', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=120)),
    Column('flag', String(length=120)),
    Column('points', SmallInteger),
)

flags_attempted = Table('flags_attempted', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('flag_id', Integer),
    Column('user_id', Integer),
    Column('correct', SmallInteger, default=ColumnDefault(0)),
)

flags_scored = Table('flags_scored', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('flag_id', Integer),
    Column('user_id', Integer),
)

user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('username', String(length=64)),
    Column('email', String(length=120)),
    Column('role', SmallInteger, default=ColumnDefault(0)),
    Column('zid', String(length=10)),
    Column('_password', String(length=120)),
    Column('_salt', String(length=120)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['flags'].create()
    post_meta.tables['flags_attempted'].create()
    post_meta.tables['flags_scored'].create()
    post_meta.tables['user'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['flags'].drop()
    post_meta.tables['flags_attempted'].drop()
    post_meta.tables['flags_scored'].drop()
    post_meta.tables['user'].drop()
