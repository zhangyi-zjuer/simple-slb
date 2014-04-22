# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-17.
import re
from flask import Markup


NGINX_CONFIG_TEMPLATE = """
server {
    listen ${port};
    server_name ${server_name};
    ${access_log}
    ${error_log}

    ${location}
}

${upstream}
"""

LOCATION_TEMPLATE = """
    location ${location} {
        proxy_pass http://${upstream_name};
        ${extra}
    }
"""

UPSTREAM_TEMPLATE = """
upstream ${upstream_name} {
    ${proxys}
}
"""


def str_to_html(s):
    """
    Generate string to html
    """
    s = s.replace('\n', '<br>').replace('\t', '    ').replace(' ', '&nbsp;')
    return Markup(s)


def generate_nginx_config(server):
    """
    Get server config
    """
    server_name = server.server_name or '_'
    port = server.port or 80
    access_log = 'access_log ' + server.access_log + ';' if server.access_log else ''
    error_log = 'error_log ' + server.error_log + ';' if server.error_log else ''
    pools = server.pools

    locations = []
    upstreams = []

    for pool in pools:
        members = pool.members
        upstream = []
        location = ''
        extra = pool.extra or ''
        extra = ('\n' + ' ' * 8).join(
            [ele.strip().rstrip(';') + ';' for ele in extra.split('\n') if len(ele.strip()) > 0]).strip()
        upstream_name = 'upstream-' + str(pool.id)

        if members:
            location = LOCATION_TEMPLATE.replace('${location}', pool.location)
            location = location.replace('${upstream_name}', upstream_name)
            location = location.replace('${extra}', extra)

            for member in members:
                server = 'server %s:%d max_fails=%d weight=%d fail_timeout=%ds;' % (
                    member.ip, member.port, member.max_fails or 3,
                    member.weight or 100, member.fail_timeout or 2)
                upstream.append(server)

        if len(upstream) > 0:
            upstream = UPSTREAM_TEMPLATE.replace('${proxys}', '\n    '.join(upstream)).replace('${upstream_name}',
                                                                                               upstream_name)
            locations.append(location)
            upstreams.append(upstream)

    replacement = {
        '${port}': port,
        '${server_name}': server_name,
        '${location}': '\n'.join(locations).strip(),
        '${upstream}': '\n'.join(upstreams).strip(),
        '${access_log}': access_log,
        '${error_log}': error_log
    }

    nginx_config = NGINX_CONFIG_TEMPLATE
    for k, v in replacement.iteritems():
        nginx_config = nginx_config.replace(k, str(v))

    return re.sub(r'(?m)^\s*$', '', nginx_config.strip())


if __name__ == "__main__":
    from app.models import *

    server = Server.query[1]

    print generate_nginx_config(server)