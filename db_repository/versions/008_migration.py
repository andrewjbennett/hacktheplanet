from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
flags_maxlevel = Table('flags_maxlevel', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('flag_id', Integer),
    Column('user_id', Integer),
    Column('maxlevel', SmallInteger),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['flags_maxlevel'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['flags_maxlevel'].drop()
