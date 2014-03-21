# -*- coding: utf-8 -*-

import os
import time
import subprocess
import json

from flask import Blueprint, request
from sqlalchemy import and_

from app.models import *
from app.database import DbUtil
from app.util import generate_nginx_config


mod = Blueprint('api', __name__, template_folder='templates', static_folder='static')


@mod.before_request
def get_config():
    global NGINX_CONFIG_DIR
    global NGINX_RELOAD_CMD

    NGINX_RELOAD_CMD = Config.query.filter(Config.key == 'NGINX_RELOAD_CMD')[0].value
    NGINX_CONFIG_DIR = Config.query.filter(Config.key == 'NGINX_CONFIG_DIR')[0].value.rstrip('/')


@mod.route('/pool/<pool_name>', methods=['GET'])
def get_pool(pool_name):
    return get_nginx_config(pool_name).replace('\n', '<br>').replace('\t', '    ').replace(' ', '&nbsp;')


@mod.route('/pool/<pool_name>/addMember', methods=['POST'])
def add_member(pool_name):
    param_list = json.loads(request.data)
    add_members = []
    for param in param_list:
        members = UpstreamMember.query.filter(
            and_(UpstreamMember.name == param['name'], UpstreamMember.pool_name == pool_name)).all()
        if len(members) == 0:
            member = UpstreamMember()
        else:
            member = members[0]

        member.pool_name = pool_name
        member.name = param['name']
        member.ip = param['ip']
        member.port = param.get('port') or 8080
        member.weight = param.get('weight') or 100
        member.max_fails = param.get('maxFails') or 3
        member.fail_time_out = param.get('failTimeout') or 2
        add_members.append(member)
    DbUtil.add(add_members)
    return json.dumps({'errorCode': 0}, ensure_ascii=False)


@mod.route('/pool/<pool_name>/delMember', methods=['POST'])
def remove_member(pool_name):
    param_list = json.loads(request.data)
    for name in param_list:
        members = UpstreamMember.query.filter(
            and_(UpstreamMember.name == name, UpstreamMember.pool_name == pool_name)).all()
        DbUtil.delete(members)
    return json.dumps({'errorCode': 0}, ensure_ascii=False)


@mod.route('/pool/<pool_name>/clear', methods=['GET'])
def clear_member(pool_name):
    members = UpstreamMember.query.filter(UpstreamMember.pool_name == pool_name).all()
    DbUtil.delete(members)
    return json.dumps({'errorCode': 0}, ensure_ascii=False)


@mod.route('/pool/<pool_name>/deploy')
def deploy(pool_name):
    status = -1

    try:
        for config_file in os.listdir(NGINX_CONFIG_DIR):
            os.remove(NGINX_CONFIG_DIR + '/' + config_file)

        save_nginx_config()

        p = subprocess.Popen(NGINX_RELOAD_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        status = p.wait()
        message = p.stderr.readline()
    except Exception, e:
        message = str(e)

    m = {'errorCode': status, 'taskId': 123}

    if status != 0:
        m['message'] = message or 'Deploy Failed'
    else:
        time.sleep(1)

    return json.dumps(m, ensure_ascii=False)


@mod.route('/pool/add', methods=['POST'])
def add_pool():
    param = json.loads(request.data)
    pool_name = param['name']
    pools = Pool.query.filter(Pool.name == pool_name).all()
    if len(pools) > 0:
        pool = pools[0]
    else:
        pool = Pool()

    pool.name = param['name']
    pool.port = param.get('port') or 80
    pool.server_name = param.get('server_name') or 'localhost'
    pool.location = param.get('location') or '/'
    DbUtil.add(pool)

    return json.dumps({'errorCode': 0}, ensure_ascii=False)


@mod.route('/pool/<pool_name>/delete', methods=['GET'])
def del_pool(pool_name):
    clear_member(pool_name)
    pools = Pool.query.filter(Pool.name == pool_name).all()
    DbUtil.delete(pools)

    return json.dumps({'errorCode': 0}, ensure_ascii=False)


def get_nginx_config(pool_name):
    pools = Pool.query.filter(Pool.name == pool_name).all()
    config = ''
    if len(pools) > 0:
        config = generate_nginx_config(pools[0])
    return config


def save_nginx_config():
    pools = Pool.query.all()
    for pool in pools:
        config = generate_nginx_config(pool)
        with open(NGINX_CONFIG_DIR + '/' + pool.name, 'w') as f:
            f.write(config)
