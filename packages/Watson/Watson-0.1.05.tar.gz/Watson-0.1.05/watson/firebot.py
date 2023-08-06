from pinder.campfire import Campfire
from twisted.application import service
import traceback, time, logging
from twisted.internet import reactor

from watson.chatbot import Chatbot

class Firebot(Chatbot):

    def __init__(self, name, commands, auth_token, subdomain, room_name, log_file='/var/log/chatbot.log', log_level=logging.INFO):
        super(Firebot, self).__init__(name, commands, log_file, log_level)
        self.auth_token = auth_token
        self.subdomain = subdomain
        self.room_name = room_name
        self.room = None
        self.users = {}
        
        reactor.addSystemEventTrigger('before', 'shutdown', self.disconnect)
        self.shutting_down = False

    def speak(self, user, message):
        if not self.room:
            self.logger.error("Must have a room before I can speak!")
            return

        if "\n" in message or "\r" in message:
            self.room.paste(message)
        else:
            self.room.speak(message)

    def connect(self):
        self.campfire = Campfire(self.subdomain, self.auth_token)
        self.room = self.campfire.find_room_by_name(self.room_name)
        self.room.join()
        self.username = self.campfire.me()['name']

        def callback(message):
            text = message['body']
            user_id = message['user_id']
            user = self.users.get(user_id)

            if user_id:
                if not user:
                    user = self.campfire.user(user_id)['user']['name']
                    self.users[user_id] = user
    
                self.perform_action(user, text)

        def err_callback(exc):
            self.error(exc)

        self.room.join()
        self.room.listen(callback, err_callback, start_reactor=False)
        application = service.Application("firebot")
        return application

    def error(self, exc):
        self.room.leave()
        self.logger.error(traceback.format_exc())
        if not self.shutting_down:
            self.logger.info("Was disconnected, trying again in 10 seconds.")
            time.sleep(10)
            self.connect()

    def disconnect(self):
        self.logger.info("Disconnect was called. The next error you see is simply Twisted shutting down.")
        self.shutting_down = True
        self.room.leave()
        reactor.stop()
