# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-14.
import os
from app.models import *
from app.database import session


def setup_config():
    session.add(Config('NGINX_CONFIG_DIR', '/etc/nginx/site-enabled/'))
    session.add(Config('NGINX_RELOAD_CMD', '/usr/sbin/nginx -s reload'))
    session.commit()


def add_test_pool():
    pool = Pool()
    pool.name = 'Test'
    pool.port = 80
    pool.server_name = 'localhost'
    pool.location = '/'
    session.add(pool)

    pool = Pool()
    pool.name = 'Test1'
    pool.port = 80
    pool.server_name = 'localhost'
    pool.location = '/'
    session.add(pool)

    pool = Pool()
    pool.name = 'Test2'
    pool.port = 80
    pool.server_name = 'localhost'
    pool.location = '/'
    session.add(pool)
    
    session.commit()


def setup():
    if os.path.exists('./slb.db'):
        print "Database File 'slb.db' already exsits"
        r = raw_input("Do you want re setup (y/n) : ").lower()
        while not (r == 'y' or r == 'n' or r == 'yes' or r == 'no'):
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
