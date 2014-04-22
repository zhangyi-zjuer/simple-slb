# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-14.
from sqlalchemy import Column, INTEGER, CHAR, TEXT, ForeignKey
from sqlalchemy.orm import relationship, backref
from database import Base, engine


class Server(Base):
    __tablename__ = 'Server'
    __table_args__ = {}
    id = Column(u'ID', INTEGER(), primary_key=True, nullable=False)
    name = Column(u'Name', CHAR(length=64), unique=True)
    port = Column(u'Port', INTEGER(), nullable=False, default=80)
    server_name = Column(u'ServerName', CHAR(length=255))
    description = Column(u'Description', TEXT)
    error_log = Column(u'ErrorLog', CHAR(length=255))
    access_log = Column(u'AccessLog', CHAR(length=255))
    pools = relationship('Pool', backref=backref('server'))


class Pool(Base):
    __tablename__ = 'Pool'
    __table_args__ = {}
    id = Column(u'ID', INTEGER(), primary_key=True, nullable=False)
    location = Column(u'Location', CHAR(length=32), unique=True)
    description = Column(u'Description', TEXT)
    extra = Column(u'Extra', TEXT)
    server_id = Column(u'Server.ID', INTEGER, ForeignKey('Server.ID'))
    members = relationship('Member', backref=backref('pool'))


class Member(Base):
    __tablename__ = 'Member'
    __table_args__ = {}
    id = Column(u'ID', INTEGER(), primary_key=True, nullable=False)
    ip = Column(u'Ip', CHAR(length=128), nullable=False)
    port = Column(u'Port', INTEGER(), nullable=False, default=8080)
    weight = Column(u'Weight', INTEGER(), nullable=False, default=100)
    max_fails = Column(u'MaxFails', INTEGER(), nullable=False, default=3)
    fail_timeout = Column(u'FailTimeout', INTEGER(), nullable=False, default=2)
    pool_id = Column(u'Pool.ID', INTEGER, ForeignKey('Pool.ID'))


class Config(Base):
    __tablename__ = 'Config'
    __table_args__ = {}
    id = Column(u'ID', INTEGER(), primary_key=True, nullable=False)
    key = Column(u'Key', CHAR(length=128))
    value = Column(u'Value', TEXT)

    def __init__(self, key, value):
        self.key = key
        self.value = value


def init_table(table):
    table.metadata.create_all(bind=engine)


def init_db():
    init_table(Server)
    init_table(Pool)
    init_table(Member)
    init_table(Config)
