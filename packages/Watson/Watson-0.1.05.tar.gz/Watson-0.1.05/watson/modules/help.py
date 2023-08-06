from watson.modules.chatmodule import ChatModule, command_function


class HelpModule(ChatModule):
    '''
    This module provides the help information for modules and/or commands. Note that it 
    ignores overhear functions, as those are never intended to be triggered intentionally.
    This module can be added to a chatbot at any time and will still provide information 
    about all chat modules added to that bot, before or after it.
    
    When using this chat module, all other modules must have __module_description__ defined.
    '''

    __module_name__ = "help"
    __module_description__ = "Displays help information about modules and commands."

    def _get_module_help(self, module):
        module_help = "Module {0} - {1}".format(module.__module_name__.title(), module.__module_description__)
        command_help = "\n".join(["\t" + self._get_command_help(command).replace("\n", "\n\t") for command in module.command_functions])
        return module_help + ("\n" + u"\u23AF" * 80 + "\n" + command_help if command_help else "")

    def _get_command_help(self, command):
        prefix = '{0} - '.format(command.__name__.title())
        syntaxes = ", ".join(['"{0}"'.format(syntax) for syntax in command.command_syntaxes])
        return prefix + syntaxes + (u"\n\t\u2022 " + command.__doc__.strip() if command.__doc__ is not None else "")

    @command_function("help [<name>]")
    def help(self, user, name=None):
        '''
        Shows help text for the given module or function name, or all modules if no name is supplied.
        '''
        if name:
            module = self.bot.get_module(name)
            if module:
                self.speak(user, self._get_module_help(module))
                return

            command = self.bot.get_command(name)
            if command:
                self.speak(user, self._get_command_help(command))
                return

            self.speak(user, "Couldn't find a module or command of that name. Try again!")

        else:
            self.speak(user, "\n\n\n".join([self._get_module_help(module) for module in self.bot.get_all_modules()]))
