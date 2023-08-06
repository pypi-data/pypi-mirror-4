from watson.grammar import create_grammars, match_grammars
import re

def command_function(*syntaxes, **options):
    '''
    This function acts as a wrapper for any chat module command function, which registers the function as a command that should
    be run when the command syntax is sent over chat.
    
    ARGUMENTS
        *syntaxes - a series of strings that specify a command syntax (see watson.grammar)
        **options - a series of options that must be specified by keyword
            storable - a boolean flag indicating whether this 
    
    RETURNS
        A wrapper function to wrap a chat module function, which registers it as a chat command
    
    EXAMPLE
        @command_function("ping")
        def ping(self):
            self.speak("pong")
            
        > watson ping
        pong
    '''
    def g(f):
        if not syntaxes:
            raise ValueError("Must provide at least one valid syntax for each command")
        f.command_syntaxes = syntaxes
        f.command_grammars = []
        f.storable = options.get("storable", True)
        for syntax in syntaxes:
            f.command_grammars += create_grammars(syntax)
        return f
    return g

def overhear_function(*res):
    '''
    This function acts as a wrapper for any chat module function that should be run when a certain regular expression is overheard.
    Any commands sent will never be overheard, and will only be processed by commands
    
    ARGUMENTS
        *res - a series of regular expressions against which the chatbot will compare incoming messages to see if the wrapped function should be run
    
    RETURNS
        A wrapper function to wrap the chat module function that should be called when regular expressions are matched
    
    EXAMPLE
        @overhear_function('long|hard')
        def she_said(self):
            self.speak("that's what she said.")
        
        > that was hard
        that's what she said
    '''
    def g(f):
        if not res:
            raise ValueError("Must provide at least one valid syntax for each command")
        f.overhear_res = [re.compile(r) for r in res]
        return f
    return g

class ChatModuleMeta(type):
    '''
    Meta class for the ChatModule, which handles registering commands and overhear functions
    '''
    def __new__(cls, name, bases, dct):
        clss = super(ChatModuleMeta, cls).__new__(cls, name, bases, dct)
        clss.command_functions = [x for x in dct.values() if hasattr(x, "command_grammars")]
        clss.overhear_functions = [x for x in dct.values() if hasattr(x, "overhear_res")]
        return clss


class ChatModule(object):
    '''
    Base class for a chat module. Every chat module must inherit from this class, and
    each subclass must specify a __module_name__ and __module_description__
    '''
    
    __metaclass__ = ChatModuleMeta

    __module_name__ = None
    __module_description__ = None
    __module_dependencies__ = []

    def __init__(self):
        self.bot = None

    def perform_command(self, user, command):
        '''
        This function is called on all chatmodules by the chatbot whenever it detects an incoming command.
        It runs through all registered commands and sees if the incoming message matches and of their syntaxes.
        If so, it runs that command function.
        '''
        hit = False
        storable = None
        for fun in self.command_functions:
            kwargs = match_grammars(command, fun.command_grammars)
            if kwargs is not False:
                self.bot.logger.info("Grammar Parsed:\n\t\t\t\tcommand: {0}\n\t\t\t\tmodule: {1}\n\t\t\t\targs: {2}".format(command, self.__module_name__ + " - " + fun.__name__, kwargs))
                fun(self, user, **kwargs)
                hit = True
                storable = fun.storable
        return hit, storable

    def overhear(self, user, message):
        '''
        This function is called on all chatmodules by the chatbot whenever it detects an incoming message that is not a command.
        It runs through all registered overhearing functions and sees if the incoming message matches and of their regular expressions.
        If so, it runs that overhearing function.
        '''
        hit = False
        for fun in self.overhear_functions:
            for regexp in fun.overhear_res:
                matched = regexp.search(message)
                if matched:
                    matched_groups = matched.groups()
                    self.bot.logger.info("Overheard Phrase:\n\t\t\t\tmessage: {0}\n\t\t\t\tmodule: {1}\n\t\t\t\targs: {2}".format(message, self.__module_name__ + " - " + fun.__name__, matched_groups))
                    fun(self, user, *matched_groups)
                    hit = True
        return hit

    def speak(self, user, message):
        return self.bot.speak(user, message)
