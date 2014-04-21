# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-14.
import os

from app.models import *
from app.database import DbUtil


def setup_config():
    DbUtil.add([Config('NGINX_CONFIG_DIR', '/etc/nginx/sites-enabled/'),
                Config('NGINX_RELOAD_CMD', '/usr/sbin/nginx -s reload')])


def add_server():
    server = Server()
    server.name = 'ppe'
    server.port = 80
    server.server_name = 'ppe.slb.dp'
    server.access_log = '/var/log/nginx/ppe_access.log'
    server.error_log = '/var/log/nginx/ppe_error.log'

    pool = Pool()
    pool.location = '/'

    member = Member()

    member.ip = '127.0.0.1'
    member.port = 8888
    member.fail_timeout = 2
    member.weight = 100
    member.max_fails = 3

    pool.members.append(member)
    server.pools.append(pool)

    pool = Pool()
    pool.location = '/test'

    member = Member()

    member.ip = '127.0.0.1'
    member.port = 8888
    member.fail_timeout = 2
    member.weight = 100
    member.max_fails = 3

    pool.members.append(member)

    member = Member()

    member.ip = '127.0.0.1'
    member.port = 8000
    member.fail_timeout = 2
    member.weight = 100
    member.max_fails = 3

    pool.members.append(member)
    server.pools.append(pool)

    DbUtil.add([server])


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
    add_server()
