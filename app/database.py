# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-14.
import collections

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool

from config import SQLITE_DB_URL


engine = create_engine(SQLITE_DB_URL, convert_unicode=True, poolclass=NullPool)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = session.query_property()


class DbUtil:
    def __init__(self):
        pass

    @staticmethod
    def __op__(obj, op_type):
        if not obj:
            return

        if isinstance(obj, collections.Iterable):
            for ele in obj:
                getattr(session, op_type)(ele)
        else:
            getattr(session, op_type)(obj)

        session.commit()

    @staticmethod
    def add(obj):
        DbUtil.__op__(obj, 'add')

    @staticmethod
    def delete(obj):
        DbUtil.__op__(obj, 'delete')
