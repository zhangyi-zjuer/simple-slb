# -*- coding: utf-8 -*-

import re
import time
import subprocess
import json
from flask import Blueprint, request
from config import NGINX_CONFIG_DIR, NGINX_RELOAD_CMD

mod = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

