# -*- coding: utf-8 -*-
import os

BOOTSTRAP_SERVE_LOCAL = True
SECRET_KEY = 'Bon-Jovi-Have-a-Nice-Day'

basedir = os.path.abspath(os.path.dirname(__file__))
SQLITE_DB_URL = 'sqlite:///' + os.path.join(basedir, 'slb.db')
