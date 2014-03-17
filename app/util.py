# -*- coding: utf-8 -*-
# Created by zhangyi on 14-3-17.
from flask import Markup
from app.models import *

NGINX_CONFIG_TEMPLATE = """
server {
    listen ${port};
    server_name ${server_name};
    ${location}
}
${upstream}
"""

LOCATION_TEMPLATE = """
    location ${location} {
        proxy_pass http://${upstream_name};
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


def generate_nginx_config(pool):
    """
    Get pool config
    """
    server_name = pool.server_name or 'localhost'
    upstream_members = UpstreamMember.query.filter(UpstreamMember.pool_name == pool.name).all()
    port = pool.port or 80

    upstream = []
    location = ''
    upstream_name = pool.name + '.upstream'

    if upstream_members and len(upstream_members) > 0:
        location = LOCATION_TEMPLATE.replace('${location}', pool.location)
        location = location.replace('${upstream_name}', upstream_name)
        for upstream_member in upstream_members:
            server = 'server %s:%d max_fails=%d weight=%d fail_timeout=%ds;' % (
                upstream_member.ip, upstream_member.port or 8080, upstream_member.max_fails or 3,
                upstream_member.weight or 100, upstream_member.fail_timeout or 2)
            upstream.append(server)

    if len(upstream) > 0:
        upstream = UPSTREAM_TEMPLATE.replace('${proxys}', '\n    '.join(upstream)).replace('${upstream_name}',
                                                                                           upstream_name)
    else:
        upstream = ''

    replacement = {
        '${port}': port,
        '${server_name}': server_name,
        '${location}': location.strip(),
        '${upstream}': upstream.strip()
    }

    nginx_config = NGINX_CONFIG_TEMPLATE
    for k, v in replacement.iteritems():
        nginx_config = nginx_config.replace(k, str(v))

    return nginx_config.strip()


if __name__ == "__main__":
    from app.models import *

    pool = Pool()
    pool.pool_name = 'just-test'
    pool.port = 80
    pool.proxy_path = '/test'
    pool.server_name = 'just-test.dianping.com'

    um = UpstreamMember()
    um.port = 8080
    um.ip = 'www.dianping.com'

    print generate_nginx_config(pool)



