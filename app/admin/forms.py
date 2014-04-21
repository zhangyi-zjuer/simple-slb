# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-17.

from flask_wtf import Form
from wtforms import TextField, HiddenField, IntegerField, SubmitField
from wtforms.validators import Required, NumberRange, Length


class ServerForm(Form):
    name = TextField('Name',
                     validators=[Required(), Length(min=2, max=30, message='Invalid Name (Length Between 2 -30)')])
    port = IntegerField('Port',
                        validators=[Required(), NumberRange(min=1, max=65535, message='Out of Range(1 - 65535)')],
                        default=80)
    server_name = TextField('ServerName', validators=[Required(), Length(min=5, max=30,
                                                                         message='Invalid ServerName \
                                                                         (Length Between 5 - 30)')])
    submit_button = SubmitField('OK')


class PoolForm(Form):
    location = TextField('Location', validators=[Required()], default='/')
    description = TextField('Description')
    submit_button = SubmitField('OK')


class MemberForm(Form):
    name = TextField('Name', validators=[Required()])
    pool_name = HiddenField('PoolName', validators=[Required()])
    ip = TextField('Ip', validators=[Required(), Length(min=5, max=50, message='Wrong Ip')])
    port = IntegerField('Port',
                        validators=[Required(), NumberRange(min=1, max=65535, message='Out of Range(1 - 65535)')],
                        default=8080)
    weight = IntegerField('Weight',
                          validators=[Required(), NumberRange(min=1, max=10000, message='Out of Range(1 - 10000)')],
                          default=100)
    max_fails = IntegerField('MaxFails',
                             validators=[Required(), NumberRange(min=1, max=100, message='Out of Range(1-100)')],
                             default=3)
    fail_timeout = IntegerField('FailTimeout',
                                validators=[Required(), NumberRange(min=0, max=100, message='Out or Range(0-100)')],
                                default=2)
    submit_button = SubmitField('OK')


class ConfigForm(Form):
    nginx_config_dir = TextField('Nginx_Config_Dir', validators=[Required()])
    nginx_reload_cmd = TextField('Nginx_Reload_Cmd', validators=[Required()])
    submit_button = SubmitField('OK')
