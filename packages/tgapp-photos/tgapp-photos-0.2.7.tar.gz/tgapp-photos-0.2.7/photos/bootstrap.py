# -*- coding: utf-8 -*-
"""Setup the photos application"""

from photos import model
from tgext.pluggable import app_model

def bootstrap(command, conf, vars):
    print 'Bootstrapping photos...'

    s1 = model.Gallery(name='default')
    model.DBSession.add(s1)
    model.DBSession.flush()

    g = app_model.Group(group_name='photos', display_name='Photos users')
    model.DBSession.add(g)
    model.DBSession.flush()

    u1 = model.DBSession.query(app_model.User).filter_by(user_name='manager').first()
    if u1:
        g.users.append(u1)
    model.DBSession.flush()

