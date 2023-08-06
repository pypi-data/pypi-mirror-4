import logging, traceback
import unicodedata

from watson.stateful import State
from watson.grammar import create_grammars, match_grammars

class Chatbot(object):
    '''
    Base chatbot class, must not be instantiated directly. All sublasses must at least override connect and speak
    for whichever service the subclass supports.
    '''

    default_phrase = 'I... have no idea what you\'re talking about. Try the command "help" for a list of my functions'
    welcome_phrase = "Hello, %s here, how may I assist you?"
    goodbye_phrase = "Oh what a world, what a world..."

    def __init__(self, name="Watson", command_names=(), log_file='/var/log/chatbot.log', log_level=logging.INFO):
        self._modules = {}
        self._commands = {}
        self.state = State(self)
        self.welcome_phrase = self.welcome_phrase % name
        self.command_grammars = create_grammars("/".join(command_names) + " <phrase>")
        
        formatter = logging.Formatter('[%(asctime)s %(levelname)s] - %(message)s')
        
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        
        self.logger = logging.getLogger("watson")
        self.logger.addHandler(handler)
        self.logger.setLevel(log_level)
    
    def speak(self, message, user):
        '''
        the method used to send a message, requires the user that triggered the message, in case the bit needs it
        
        to be implemented by subclasses
        '''
        raise NotImplementedError

    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def error(self):
        raise NotImplementedError

    def add_module(self, module):
        if not module.__module_name__ in self._modules:
            for dependency in module.__module_dependencies__:
                if not dependency in self._modules:
                    raise ValueError('Module dependency missing! Module "{0}" requires module "{1}", which has not been added yet.'.format(module.__module_name__, dependency))
            self._modules[module.__module_name__] = module
            module.bot = self

            for command in module.command_functions:
                self._commands[command.__name__] = command
        else:
            raise ValueError("Duplicate module added. Cannot have multiple modules with the same name: " + module.__module_name__)

    def get_module(self, name):
        return self._modules.get(name, None)

    def get_all_modules(self):
        return self._modules.values()

    def get_command(self, name):
        return self._commands.get(name, None)

    def perform_action(self, user, message):
        '''
        parses out the message. if it's a command, it calls do_command.
        if it's not a command, it gets the chat modules to try to overhear it if they can
        '''
        self.logger.info(getattr(self,'username',None))
        if not getattr(self,'username',None) or user != self.username:
            try:
                message = unicodedata.normalize('NFKD', unicode(message)).encode('ascii', 'ignore').lower()
                self.state.check_answer(user, message)
    
                parsed = match_grammars(str(message), self.command_grammars)
                if parsed:
                    self.do_command(user, parsed['phrase'].lower())
                else:
                    hit = False
                    for module in self._modules.values():
                        hit |= module.overhear(user, message)
                        if hit:
                            break
    
            except Exception:
                self.logger.error(traceback.format_exc())
                try:
                    self.speak(user, "Whoops, looks like that caused me to crash. Check my log files to see what happened!")
                except:
                    self.logger.error(traceback.format_exc())

    def do_command(self, user, command):
        '''
        goes through all chat modules and gets them to try to perform an action if they can. if nothing can, it says a predefined phrase
        '''
        hit = False
        storable = True
        
        for module in self._modules.values():
            module_hit, storable = module.perform_command(user, command)
            hit |= module_hit
            if hit:
                if storable:
                    self.state.store_command(user, command)
                break
            
        if not hit:
            self.speak(user, self.default_phrase)
