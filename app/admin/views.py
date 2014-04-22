# -*- coding: utf-8 -*-

import os
import time
import json
import subprocess

from flask import Blueprint, redirect, url_for, render_template, request, Markup

from app.models import *
from app.admin.forms import *
from app.database import DbUtil
from app.util import generate_nginx_config


mod = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


@mod.route('/', methods=['GET'])
def index():
    redirect(url_for('admin.get_servers'))


@mod.route('/servers', methods=['GET'])
def servers():
    return render_template('server.html', servers=Server.query.all())


@mod.route('/server/add', methods=['GET', 'POST'])
def add_server():
    return edit_server()


@mod.route('/server/<server_id>/edit', methods=['GET', 'POST'])
def edit_server(server_id=None):
    form = ServerForm()
    server = Server()
    if server_id:
        server = Server.query.filter(Server.id == server_id)[0]

    if request.method == 'GET':
        if server_id:
            form = get_form_from_db(server, ServerForm())

        return render_template('form_template.html', form=form)

    if not form.validate_on_submit():
        return render_template('form_template.html', form=form)
    add_form_data_to_db(server, form)

    return redirect(url_for('admin.servers'))


@mod.route('/server/<server_id>/delete', methods=['GET'])
def del_server(server_id):
    DbUtil.delete(Server.query.filter(Server.id == server_id).all())
    return redirect(url_for('admin.servers'))


@mod.route('/server/<server_id>/pools')
def pools(server_id):
    server = Server.query.filter(Server.id == server_id)[0]
    for pool in server.pools:
        pool.member_info = get_members(pool)
    return render_template('pool.html', pools=server.pools, server=server)


@mod.route('/server/<server_id>/pool/add', methods=['GET', 'POST'])
def add_pool(server_id):
    return edit_pool(server_id=server_id)


@mod.route('/pool/<pool_id>/edit', methods=['GET', 'POST'])
def edit_pool(server_id=None, pool_id=None):
    form = PoolForm()
    pool = Pool()

    if pool_id:
        pool = Pool.query.filter(Pool.id == pool_id)[0]
        if not server_id:
            server_id = pool.server.id

    if request.method == 'GET':
        if pool_id:
            form = get_form_from_db(pool, PoolForm())
        return render_template('form_template.html', form=form)

    if not form.validate_on_submit():
        return render_template('form_template.html', form=form)

    pool.server = Server.query.filter(Server.id == server_id)[0]
    add_form_data_to_db(pool, form)

    return redirect(url_for('admin.pools', server_id=server_id))


@mod.route('/pool/<pool_id>/del', methods=['GET', 'POST'])
def del_pool(pool_id):
    pool = Pool.query.filter(Pool.id == pool_id)[0]
    server_id = pool.server.id
    DbUtil.delete(pool)
    return redirect(url_for('admin.pools', server_id=server_id))


@mod.route('/pool/<pool_id>/members')
def members(pool_id):
    pool = Pool.query.filter(Pool.id == pool_id)[0]
    return render_template('member.html', members=pool.members, pool=pool)


@mod.route('/pool/<pool_id>/member/add', methods=['GET','POST'])
def add_member(pool_id):
    return edit_member(pool_id=pool_id)


@mod.route('/member/<member_id>/edit', methods=['GET', 'POST'])
def edit_member(pool_id=None, member_id=None):
    form = MemberForm()
    member = Member()
    if member_id:
        member = Member.query.filter(Member.id == member_id)[0]
        if not pool_id:
            pool_id = member.pool.id

    if request.method == 'GET':
        if member_id:
            form = get_form_from_db(member, MemberForm())

        return render_template('form_template.html', form=form)

    if not form.validate_on_submit():
        return render_template('form_template.html', form=form)

    member.pool = Pool.query.filter(Pool.id == pool_id)[0]
    add_form_data_to_db(member, form)

    return redirect(url_for('admin.members', pool_id=pool_id))


@mod.route('/member/<member_id>/del')
def del_member(member_id):
    member = Member.query.filter(Member.id == member_id)[0]
    pool_id = member.pool.id
    DbUtil.delete(member)
    return redirect(url_for('admin.members', pool_id=pool_id))


@mod.route('/config', methods=['GET'])
def config():
    configs = Config.query.all()
    return render_template('config.html', configs=configs)


@mod.route('/config/edit', methods=['GET', 'POST'])
def edit_config():
    form = ConfigForm()
    nginx_config_dir = Config.query.filter(Config.key == 'NGINX_CONFIG_DIR')[0]
    nginx_reload_cmd = Config.query.filter(Config.key == 'NGINX_RELOAD_CMD')[0]
    if request.method == 'GET':
        form.nginx_config_dir.data = nginx_config_dir.value
        form.nginx_reload_cmd.data = nginx_reload_cmd.value
        return render_template('form_template.html', form=form)

    if not form.validate_on_submit():
        return render_template('form_template.html', form=form)

    nginx_config_dir.value = form.nginx_config_dir.data
    nginx_reload_cmd.value = form.nginx_reload_cmd.data
    DbUtil.add([nginx_config_dir, nginx_reload_cmd])

    return redirect(url_for('admin.config'))


@mod.route('/deploy')
def deploy():
    status = -1
    nginx_reload_cmd = Config.query.filter(Config.key == 'NGINX_RELOAD_CMD')[0].value
    nginx_config_dir = Config.query.filter(Config.key == 'NGINX_CONFIG_DIR')[0].value.rstrip('/')
    try:
        for config_file in os.listdir(nginx_config_dir):
            os.remove(nginx_config_dir + '/' + config_file)

        save_nginx_config(nginx_config_dir)

        p = subprocess.Popen(nginx_reload_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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


def get_members(pool):
    return Markup('<br>'.join([member.ip + ':' + str(member.port) for member in pool.members]))


def add_form_data_to_db(obj, form):
    for attr in [attr for attr in dir(form) if hasattr(getattr(form, attr), 'data')]:
        if attr not in ['__class__', 'csrf_token'] and hasattr(obj, attr):
            setattr(obj, attr, getattr(form, attr).data)
            print attr, getattr(form, attr).data

    DbUtil.add(obj)


def get_form_from_db(obj, form):
    for attr in [attr for attr in dir(obj)]:
        if attr not in ['__class__', 'csrf_token'] and hasattr(form, attr) and hasattr(getattr(form, attr), 'data'):
            setattr(getattr(form, attr), 'data', getattr(obj, attr))
    return form


def save_nginx_config(nginx_config_dir):
    servers = Server.query.all()
    for server in servers:
        config = generate_nginx_config(server)
        with open(nginx_config_dir + '/' + server.name, 'w') as f:
            f.write(config)