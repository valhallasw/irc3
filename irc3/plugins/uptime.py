# -*- coding: utf-8 -*-
__doc__ = '''
==============================================
:mod:`irc3.plugin.uptime` Uptime plugin
==============================================

Add an ``uptime`` command.

.. autoclass:: Uptime
   :members:

'''
from irc3.plugins.command import command
import time
import irc3


@irc3.plugin
class Uptime:

    def __init__(self, bot):
        self.bot = bot
        bot.uptimes = self
        self.uptime = time.time()
        self.connection_uptime = None
        config = bot.config.get(__name__, {})
        self.fmt = config.get('fmt', '{days} days {hours} hours')
        self.privmsg = config.get('privmsg',
                                  'Up since {0}. Connected since {1}')

    def connection_made(self):
        self.connection_uptime = time.time()

    def delta(self, value):
        values = []
        for base in [3600*24, 3600, 60, 1]:
            d, value = divmod(value, base)
            values.append(int(d))
        values = dict(zip(['days', 'hours', 'minutes', 'seconds'], values))
        return self.fmt.format(**values)

    @command(permission='view')
    def uptime(self, mask, target, args):
        """Show uptimes

            %%uptime
        """
        now = time.time()
        uptime = self.delta(now - self.uptime)
        connection_uptime = self.delta(now - (self.connection_uptime or now))
        if not target.is_channel:
            target = target.nick
        self.bot.privmsg(target,
                         self.privmsg.format(uptime, connection_uptime))
