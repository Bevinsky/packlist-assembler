import irclib.session as session
import irclib.connection as connection
import irclib.dcc as dcc
from models import Channel, Bot, Pack
import peewee
import re


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

    def irc_connect(self, nick):
        #TODO
        pass

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



