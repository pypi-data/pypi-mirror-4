import logging, traceback

from twisted.application import service
from twisted.internet import stdio
from twisted.protocols import basic
from twisted.internet import reactor

from watson.chatbot import Chatbot
from os import linesep
import unicodedata


class Receiver(basic.LineReceiver):
    
    '''
    def __init__(self, bot):
        self.bot = bot
        # super(Receiver, self).__init__()
    '''
    
    def connectionMade(self):
        self.transport.write('>>> ')

    def lineReceived(self, line):
        try:
            self.bot.perform_action("",line)
        except:
            self.transport.write('Had an error. Check my logs!\n')
            self.bot.logger.error(traceback.format_exc())
        self.transport.write('>>> ')

class Shellbot(Chatbot):

    def __init__(self, name, commands, log_file='/var/log/chatbot.log', log_level=logging.INFO):
        super(Shellbot, self).__init__(name, commands, log_file, log_level)
        self.receiver = Receiver()
        self.receiver.bot = self
        self.receiver.delimiter = linesep

    def speak(self, user, message):
        message = unicodedata.normalize('NFKD', unicode(message)).encode('ascii','ignore').replace("\n",self.receiver.delimiter)
        self.receiver.sendLine(message)

    def connect(self):
        stdio.StandardIO(self.receiver)
        application = service.Application("shellbot")
        return application

    def error(self, exc):
        pass

    def disconnect(self):
        reactor.stop()
