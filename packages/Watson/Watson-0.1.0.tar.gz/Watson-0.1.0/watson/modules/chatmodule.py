from watson.grammar import create_grammars, match_grammars
import re

def command_function(*syntaxes):
    def g(f):
        if not syntaxes:
            raise ValueError("Must provide at least one valid syntax for each command")
        f.command_syntaxes = syntaxes
        f.command_grammars = []
        for syntax in syntaxes:
            f.command_grammars += create_grammars(syntax)
        return f
    return g

def overhear_function(*res):
    def g(f):
        if not res:
            raise ValueError("Must provide at least one valid syntax for each command")
        f.overhear_res = [re.compile(r) for r in res]
        return f
    return g

class ChatModuleMeta(type):
    def __new__(cls, name, bases, dct):
        clss = super(ChatModuleMeta, cls).__new__(cls, name, bases, dct)
        clss.command_functions = [x for x in dct.values() if hasattr(x, "command_grammars")]
        clss.overhear_functions = [x for x in dct.values() if hasattr(x, "overhear_res")]
        return clss


class ChatModule(object):
    __metaclass__ = ChatModuleMeta

    __module_name__ = None
    __module_description__ = None
    __module_dependencies__ = []

    def __init__(self):
        self.bot = None

    def perform_command(self, user, command):
        hit = False
        for fun in self.command_functions:
            kwargs = match_grammars(command, fun.command_grammars)
            if kwargs is not False:
                self.bot.logger.info("Grammar Parsed:\n\t\t\t\tcommand: {0}\n\t\t\t\tmodule: {1}\n\t\t\t\targs: {2}".format(command, self.__module_name__ + " - " + fun.__name__, kwargs))
                fun(self, user, **kwargs)
                hit = True
        return hit

    def overhear(self, user, message):
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
