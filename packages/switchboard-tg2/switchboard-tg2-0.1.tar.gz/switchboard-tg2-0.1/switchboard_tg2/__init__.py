# -*- coding: utf-8 -*-
"""The switchboard-tg2 package"""


def plugme(app_config, options):
    def switchboard_setup(app):
        from tg import config, request
        from switchboard import configure, operator
        # Load builtins
        __import__('switchboard.builtins')
        # Setup the global operator for our switchboard switches
        configure(config, nested=True)
        # Hook the operator up to the user and request objects
        #operator.get_user = lambda: self.user
        # request is actually a StackedObjectProxy and we want the underlying
        # webob.Request object
        operator.get_request = lambda: request._current_obj()
        return app
    app_config.register_hook('after_config', switchboard_setup)
    return dict(appid='switchboard', global_helpers=False)
