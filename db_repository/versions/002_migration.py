from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
flags_attempted = Table('flags_attempted', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('flag_id', Integer),
    Column('user_id', Integer),
    Column('correct', SmallInteger, default=ColumnDefault(0)),
    Column('flag', String(length=120)),
    Column('timestamp', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['flags_attempted'].columns['flag'].create()
    post_meta.tables['flags_attempted'].columns['timestamp'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['flags_attempted'].columns['flag'].drop()
    post_meta.tables['flags_attempted'].columns['timestamp'].drop()
