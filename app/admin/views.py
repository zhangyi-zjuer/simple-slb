# -*- coding: utf-8 -*-

import re
from flask import Blueprint, redirect, url_for, render_template, Markup, request
from app.models import *
from app.admin.forms import *
from app.database import session
from sqlalchemy import and_

mod = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


@mod.route('/', methods=['GET'])
def index():
    redirect(url_for('admin.get_pool'))


@mod.route('/pool', methods=['GET'])
def get_pool():
    pools = Pool.query.all()
    for pool in pools:
        pool.url = '/admin/pool/' + pool.name
        pool.members = get_members(pool)

    return render_template('pool.html', pools=pools)


@mod.route('/pool/add', methods=['GET', 'POST'])
def add_pool():
    return edit_pool()


@mod.route('/pool/<pool_name>/member/add', methods=['GET', 'POST'])
def add_member(pool_name):
    return edit_member(pool_name=pool_name)


@mod.route('/pool/<pool_name>/member/clear', methods=['GET', 'POST'])
def clear_member(pool_name):
    members = UpstreamMember.query.filter(
        UpstreamMember.pool_name == pool_name).all()
    for member in members:
        session.delete(member)
    session.commit()
    return redirect(url_for('admin.pool_members', pool_name=pool_name))


@mod.route('/pool/<pool_name>/<member_name>/edit', methods=['GET', 'POST'])
def edit_member(pool_name, member_name=None):
    form = MemberForm()
    form.pool_name.data = pool_name
    member = UpstreamMember()
    if member_name:
        member = \
            UpstreamMember.query.filter(
                and_(UpstreamMember.pool_name == pool_name, UpstreamMember.name == member_name))[0]

    if request.method == 'GET':
        if member_name:
            form = get_form_from_db(member, MemberForm())

        return render_template('form_template.html', form=form)

    if not form.validate_on_submit():
        return render_template('form_template.html', form=form)

    add_form_data_to_db(member, form)

    return redirect(url_for('admin.pool_members', pool_name=pool_name))


@mod.route('/pool/<pool_name>/<member_name>/delete')
def del_member(pool_name, member_name):
    members = UpstreamMember.query.filter(
        and_(UpstreamMember.pool_name == pool_name, UpstreamMember.name == member_name)).all()
    for member in members:
        session.delete(member)
    session.commit()
    return redirect(url_for('admin.pool_members', pool_name=pool_name))


@mod.route('/pool/<pool_name>/member')
def pool_members(pool_name):
    members = UpstreamMember.query.filter(UpstreamMember.pool_name == pool_name).all()
    return render_template('member.html', members=members, pool_name=pool_name)


@mod.route('/pool/<pool_name>/delete', methods=['GET'])
def del_pool(pool_name):
    pools = Pool.query.filter(Pool.name == pool_name).all()
    for pool in pools:
        session.delete(pool)
    members = UpstreamMember.query.filter(UpstreamMember.pool_name == pool_name).all()
    for member in members:
        session.delete(member)
    session.commit()
    return redirect(url_for('admin.get_pool'))


@mod.route('/pool/<pool_name>/edit', methods=['GET', 'POST'])
def edit_pool(pool_name=None):
    form = PoolForm()
    pool = Pool()
    if pool_name:
        pool = Pool.query.filter(Pool.name == pool_name)[0]

    if request.method == 'GET':
        if pool_name:
            form = get_form_from_db(pool, PoolForm())

        return render_template('form_template.html', form=form)

    if not form.validate_on_submit():
        return render_template('form_template.html', form=form)
    add_form_data_to_db(pool, form)

    return redirect(url_for('admin.get_pool'))


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
    session.add(nginx_config_dir)
    session.add(nginx_reload_cmd)
    session.commit()
    return redirect(url_for('admin.config'))


def get_members(pool):
    members = UpstreamMember.query.filter(UpstreamMember.pool_name == pool.name).all()
    member_list = []
    for m in members:
        s = "[%s]\t%s:%d max_fails=%d weight=%d fail_timeout=%ds" % (m.name,
                                                                     m.ip, m.port, m.max_fails, m.weight,
                                                                     m.fail_timeout)
        member_list.append(s)

    return Markup('<br>'.join(member_list))


def add_form_data_to_db(obj, form):
    for attr in [attr for attr in dir(form) if hasattr(getattr(form, attr), 'data')]:
        if attr not in ['__class__', 'csrf_token'] and hasattr(obj, attr):
            setattr(obj, attr, getattr(form, attr).data)
            print attr, getattr(form, attr).data

    session.add(obj)
    session.commit()


def get_form_from_db(obj, form):
    for attr in [attr for attr in dir(obj)]:
        if attr not in ['__class__', 'csrf_token'] and hasattr(form, attr) and hasattr(getattr(form, attr), 'data'):
            setattr(getattr(form, attr), 'data', getattr(obj, attr))
    return form