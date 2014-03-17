# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-14.

from sqlalchemy import Column, INTEGER, CHAR, TEXT

from database import Base, engine


class Pool(Base):
    __tablename__ = 'Pool'
    __table_args__ = {}
    id = Column(u'ID', INTEGER(), primary_key=True, nullable=False)
    name = Column(u'Name', CHAR(length=64))
    port = Column(u'Port', INTEGER(), nullable=False, default=80)
    server_name = Column(u'ServerName', CHAR(length=128))
    location = Column(u'Location', CHAR(length=32))


class UpstreamMember(Base):
    __tablename__ = 'UpstreamMember'
    __table_args__ = {}
    id = Column(u'ID', INTEGER(), primary_key=True, nullable=False)
    name = Column(u'Name', CHAR(length=64), nullable=False)
    pool_name = Column(u'PoolName', CHAR(length=64), nullable=False)
    ip = Column(u'Ip', CHAR(length=128), nullable=False)
    port = Column(u'Port', INTEGER(), nullable=False, default=8080)
    weight = Column(u'Weight', INTEGER(), nullable=False, default=100)
    max_fails = Column(u'MaxFails', INTEGER(), nullable=False, default=3)
    fail_timeout = Column(u'FailTimeout', INTEGER(), nullable=False, default=2)


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
    init_table(Pool)
    init_table(UpstreamMember)
    init_table(Config)

