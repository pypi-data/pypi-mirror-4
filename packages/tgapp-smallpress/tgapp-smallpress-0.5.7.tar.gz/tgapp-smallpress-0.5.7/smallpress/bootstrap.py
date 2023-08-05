# -*- coding: utf-8 -*-
"""Setup the smallpress application"""

from smallpress import model
from tgext.pluggable import app_model
import tg

def bootstrap(command, conf, vars):
    print 'Bootstrapping smallpress...'

    g = app_model.Group(group_name='smallpress', display_name='Smallpress blogging users')
    model.DBSession.add(g)
    model.DBSession.flush()

    u1 = model.DBSession.query(app_model.User).filter_by(user_name='manager').first()
    if u1:
        g.users.append(u1)
    model.DBSession.flush()