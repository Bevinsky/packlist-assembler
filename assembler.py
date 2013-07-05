import irclib.session as session
import irclib.connection as connection
import irclib.dcc as dcc
import irclib.utils as utils
from models import Channel, Bot, Pack
import peewee
import re
import io

import logging
logging.basicConfig(level=logging.DEBUG)


class Assembler(object):
    regex_packlist_line = re.compile(r"""
        \#(\d+)\s+([0-9]+)x\s\[\s*([0-9\.]+[MGKT])\]\s(.*)
    """, re.VERBOSE)

    size_prefix = {'K': 1024,
                   'M': 1024 * 1024,
                   'G': 1024 * 1024 * 1024,
                   'T': 1024 * 1024 * 1024 * 1024}

    def __init__(self, server, port):
        self.__server = server
        self.__port = port
        session.register(self.debug_print)
        session.register(self.handle_dcc)
        session.register(self.dcc_complete)

    def irc_connect(self, nick):
        self._session = session.Session()
        self._irc = self._session.server()
        self._irc.connect(self.__server, self.__port, nick)

    def add_bot(self, channel, name):
        channel = channel.lower()
        name = name.lower()
        try:
            Bot.get(Bot.name == name)
        except peewee.DoesNotExist:
            pass  # this seems really unpythonic somehow
        else:
            raise KeyError('Bot already exists')
        try:
            chan_o = Channel.get(Channel.name == channel)
        except peewee.DoesNotExist:
            chan_o = Channel.create(name=channel)
        Bot.create(name=name,
                   channel=chan_o)

    def parse_packlist(self, data):
        search = Assembler.regex_packlist_line.findall(data)
        for num, count, size_str, name in search:
            size = float(size_str.strip('KMGT'))
            if size_str[-1] in Assembler.size_prefix:
                size *= Assembler.size_prefix(size_str[-1])
            size = int(size)
            try:
                pack = Pack.get((Pack.pack_number == num) & (Pack.bot.name))
                pack.count = count
                pack.size = size
                pack.name = name
                pack.save()
            except peewee.DoesNotExist:
                Pack.create(pack_number=num,
                            count=count,
                            size=size,
                            name=name)

    #@session.register
    @session.filters.events('dcc_complete')
    def dcc_complete(self, event):
        print 'DCC complete from ' + event.source
        fileobj = event.server.fileobj
        fileobj.seek(0)
        data = fileobj.read()
        self.stored = data
        fileobj.close()
        #self.parse_packlist(fileobj.read())



    #@session.register
    @session.filters.events('ctcp')
    def handle_dcc(self, event):
        print 'CTCP ' + event.ctcp + ' from ' + event.nickname.name + ': ' + event.message
        if event.ctcp == 'DCC':
            params = event.message.split()
            ip = utils.ip_quad_to_numstr(int(params[-3]))
            port = int(params[-2])
            size = int(params[-1])
            dccfile = io.BytesIO()

            conn = self._session.dcc('send', (dccfile, size))
            conn.connect(ip, port)


    #@session.register
    #@session.filters.events('text')
    def debug_print(self, event):
        if event.command == 'raw':
            return
        n = u''
        if event.nickname:
            n = event.nickname.name
        print event.command + u"> " + n + u": " + (event.channel or u'') + ": " + (event.message or u'NOMSG')
        #if event.nickname:
        #    print event.nickname.name + u" ",
        #if event.channel:
        #    print event.channel + u" ",
        #if event.message:
        #    print event.message
        #print event.nickname.name + u" " + event.channel + u" " + event.message



