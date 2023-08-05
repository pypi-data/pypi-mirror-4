# -*- encoding:utf-8 -*-
"""
    flaskext.actions
    ~~~~~~~~~~~~~~~~~

    Description of the module goes here...

    :copyright: (c) 2010 by Young King.
    :license: BSD, see LICENSE for more details.
"""
from werkzeug import script
from .server_actions import server_actionnames
from .help_actions import help_actionnames

class Manager(object):
    """
    Management class for handle flask app.


    :param application: Flask instance
    :default_help_actions: load default help actions . Default is True.
    :default_server_actions: load default server actions. Default is False.
    """
    def __init__(self, application,default_help_actions=True,default_server_actions=False):
        self.application = application
        self._actions = {
                'shell'     :   script.make_shell(lambda: {"app": application},
                                    "Interactive Flask Shell"),
                'runserver' :   script.make_runserver(lambda: application,
                                    use_reloader=True, threaded=True, hostname='0.0.0.0',
                                    port=7777, use_debugger=True),
                }
        if default_help_actions:
            self.add_actions(help_actionnames)
        if default_server_actions:
            self.add_actions(server_actionnames)


    def register(self,name):
        """a decorator for add action """
        def deco(func):
            self.add_action(name,func)
            return func
        return deco

    def add_actions(self,funcmap):
        """
        Add multiple actions at once.
        """
        for name,func in funcmap.items():
            self.add_action(name,func)

    def add_action(self, name, func):
        """ add an action"""
        self._actions[name] = func(self.application)

    def run(self):
        script.run(self._actions, '')
