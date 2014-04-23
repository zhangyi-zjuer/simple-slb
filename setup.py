# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-14.
import os

from app.models import *
from app.database import DbUtil


def set_config():
    DbUtil.add([Config('NGINX_CONFIG_DIR', '/etc/nginx/sites-enabled/'),
                Config('NGINX_RELOAD_CMD', '/usr/sbin/nginx -s reload')])


def add_slb_server():
    server = Server()
    server.name = 'SLB'
    server.port = 80
    server.server_name = '_'
    server.description = u'SLB路由'
    server.access_log = '/var/log/nginx/slb_access.log'
    server.error_log = '/var/log/nginx/slb_error.log'

    pool = Pool()
    pool.location = '/'
    pool.description = u'重定向到SLB服务端口'

    member = Member()

    member.ip = '127.0.0.1'
    member.port = 8888
    member.fail_timeout = 2
    member.weight = 100
    member.max_fails = 3

    pool.members.append(member)
    server.pools.append(pool)

    DbUtil.add([server])


def setup():
    r = raw_input("If you have already setup, All Data will removed. Do you want setup?(y/n) ").lower()
    while not r in ['y', 'n', 'yes', 'no']:
        r = raw_input("Please Enter correct character (y or n): ").lower()

    if 'y' in r:
        init_db()
        print 'Set up Successfully'
    else:
        print 'Nothing Changed'

if __name__ == "__main__":
    setup()
    set_config()
    add_slb_server()
