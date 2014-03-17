# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-14.

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from config import SQLITE_DB_URL

engine = create_engine(SQLITE_DB_URL, convert_unicode=True, poolclass=NullPool)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
Base.query = session.query_property()

