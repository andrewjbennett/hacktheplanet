from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
flags = Table('flags', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('name', VARCHAR(length=120)),
    Column('flag', VARCHAR(length=120)),
    Column('points', SMALLINT),
)

flags_attempted = Table('flags_attempted', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('flag_id', INTEGER),
    Column('user_id', INTEGER),
    Column('correct', SMALLINT),
)

flags_scored = Table('flags_scored', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('flag_id', INTEGER),
    Column('user_id', INTEGER),
)

user = Table('user', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('username', VARCHAR(length=64)),
    Column('email', VARCHAR(length=120)),
    Column('role', SMALLINT),
    Column('zid', VARCHAR(length=10)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['flags'].drop()
    pre_meta.tables['flags_attempted'].drop()
    pre_meta.tables['flags_scored'].drop()
    pre_meta.tables['user'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['flags'].create()
    pre_meta.tables['flags_attempted'].create()
    pre_meta.tables['flags_scored'].create()
    pre_meta.tables['user'].create()
