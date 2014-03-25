# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-14.
import os

from app.models import *
from app.database import DbUtil


def setup_config():
    DbUtil.add([Config('NGINX_CONFIG_DIR', '/etc/nginx/sites-enabled/'),
                Config('NGINX_RELOAD_CMD', '/usr/sbin/nginx -s reload')])


def add_test_pool():
    pool = Pool()
    pool.name = 'ppe'
    pool.port = 80
    pool.server_name = 'ppe.slb.dp'
    pool.location = '/'

    server = UpstreamMember()
    server.pool_name = 'ppe'
    server.name = 'admin'
    server.ip = '127.0.0.1'
    server.port = 8888
    server.fail_timeout = 2
    server.weight = 100
    server.max_fails = 3

    DbUtil.add([pool, server])


def setup():
    if os.path.exists('./slb.db'):
        print "Database File 'slb.db' already exsits"
        r = raw_input("Do you want re setup (y/n) : ").lower()
        while not r in ['y', 'n', 'yes', 'no']:
            r = raw_input("Please Enter correct character (y or n): ").lower()

        if 'y' in r:
            os.remove('./slb.db')
            init_db()
            print 'Set up Successfully'
        else:
            print 'Nothing Changed'
    else:
        init_db()
        print 'New Database Set up Successfully'


if __name__ == "__main__":
    setup()
    setup_config()
    add_test_pool()
