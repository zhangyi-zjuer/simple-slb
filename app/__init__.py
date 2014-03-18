# -*- coding: utf-8 -*-

import sys

from flask import Flask
from flask_bootstrap import Bootstrap
from database import session as database_session

# set encoding
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
Bootstrap(app)
app.config.from_object('config')


@app.teardown_appcontext
def shutdown_session(exception=None):
    database_session.remove()

import views

from api.views import mod as api_module
from admin.views import mod as admin_module


app.register_blueprint(api_module, url_prefix='/api')
app.register_blueprint(admin_module, url_prefix='/admin')
