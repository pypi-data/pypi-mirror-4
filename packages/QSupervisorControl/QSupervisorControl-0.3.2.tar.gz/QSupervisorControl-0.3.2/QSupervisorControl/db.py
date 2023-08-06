# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import sqlalchemy
import os


def get_engine():
    print '%s' % os.path.join(os.environ.get('HOME'), 'qsc.dat')

    return sqlalchemy.create_engine(
        'sqlite:///%s' % os.path.join(os.environ.get('HOME'), 'qsc.dat'),
        echo=True
    )


def get_session():
    Session = sessionmaker()
    Session.configure(bind=get_engine())

    return Session()

Base = declarative_base()


class Launche(Base):

    __tablename__ = 'launche'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    monitor_pattern = sqlalchemy.Column(sqlalchemy.String)
    touch_file = sqlalchemy.Column(sqlalchemy.String)
    log_file = sqlalchemy.Column(sqlalchemy.String)
    path = sqlalchemy.Column(sqlalchemy.String)

    def __init__(self, name, monitor_pattern=None):
        self.name = name
        self.monitor_pattern = monitor_pattern

Base.metadata.create_all(get_engine())
