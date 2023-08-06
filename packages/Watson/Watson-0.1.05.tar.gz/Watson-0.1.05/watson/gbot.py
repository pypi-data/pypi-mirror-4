from twisted.words.xish import domish
from wokkel.xmppim import MessageProtocol, AvailablePresence
from twisted.application import service
from twisted.words.protocols.jabber import jid
from wokkel.client import XMPPClient
from watson.chatbot import Chatbot
from twisted.internet import reactor
import logging


class GBotProtocol(MessageProtocol):
    def connectionMade(self):
        self.bot.logger.info("Connected!")

        # send initial presence
        self.send(AvailablePresence())

    def connectionLost(self, reason):
        self.bot.logger.info("Disconnected!")

    def onMessage(self, msg):

        if msg["type"] == 'chat' and hasattr(msg, "body") and msg.body:
            user = msg["from"]
            message = msg.body
            self.send(AvailablePresence())
            return self.bot.perform_action(user, message)


class Gbot(Chatbot):

    def __init__(self, name, commands, username, password, log_file='/var/log/chatbot.log', log_level=logging.INFO):
        super(Gbot, self).__init__(name, commands, log_file, log_level)
        self.username = username
        self.password = password

    def speak(self, user, message):
        if not self.protocol:
            print "Must have a protocol before I can speak!"
            return

        reply = domish.Element((None, "message"))
        reply["to"] = user
        reply["from"] = self.protocol.parent.jid.full()
        reply["type"] = 'chat'
        reply.addElement("body", content=message)

        self.protocol.send(reply)

    def connect(self):
        application = service.Application("gbot")

        xmppclient = XMPPClient(jid.internJID(self.username), self.password)
        xmppclient.logTraffic = False
        self.protocol = GBotProtocol()
        self.protocol.bot = self
        self.protocol.setHandlerParent(xmppclient)
        xmppclient.setServiceParent(application)
        return application

    def error(self):
        pass

    def disconnect(self):
        reactor.stop()
