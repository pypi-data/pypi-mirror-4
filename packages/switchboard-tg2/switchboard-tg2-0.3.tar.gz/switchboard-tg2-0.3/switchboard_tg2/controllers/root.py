# -*- coding: utf-8 -*-
"""Main Controller"""
from tg import TGController, expose

from switchboard.admin.controllers import CoreAdminController


class RootController(TGController):
    def __init__(self):
        super(RootController, self).__init__()
        self._c = CoreAdminController()

    @expose('mako:switchboard.admin.templates.index')
    def index(self, by='-date_modified'):
        return self._c.index(by)

    @expose('json')
    def add(self, key, label='', description=None, **kwargs):
        return self._c.add(key, label, description, **kwargs)

    @expose('json')
    def update(self, curkey, key, label='', description=None):
        return self._c.update(curkey, key, label, description)

    @expose('json')
    def status(self, key, status):
        return self._c.status(key, status)

    @expose('json')
    def delete(self, key):
        return self._c.delete(key)

    @expose('json')
    def add_condition(self, *args, **kwargs):
        return self._c.add_condition(*args, **kwargs)

    @expose('json')
    def remove_condition(self, *args, **kwargs):
        return self._c.remove_condition(*args, **kwargs)
