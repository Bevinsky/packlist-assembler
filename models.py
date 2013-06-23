from peewee import *
import peewee
import config

db = MySQLDatabase(config.database,
                   user=config.dbuser,
                   passwd=config.dbpass)

class Base(Model):
    class Meta:
        database = db


class Channel(Base):
    id = PrimaryKeyField()
    name = CharField(max_length=100,
                     null=False,
                     unique=True)


class Bot(Base):
    id = PrimaryKeyField()
    name = CharField(max_length=100,
                     null=False,
                     unique=True)
    channel = ForeignKeyField(Channel,
                              null=False,
                              related_name='bots')


class Pack(Base):
    id = PrimaryKeyField()
    pack_number = IntegerField(null=False)
    count = IntegerField(null=False)
    size = IntegerField(null=False)
    name = TextField(null=False)
    bot = ForeignKeyField(Bot,
                          null=False,
                          related_name='packlist')



def create_models():
    Channel.create_table()
    Bot.create_table()
    Pack.create_table()
