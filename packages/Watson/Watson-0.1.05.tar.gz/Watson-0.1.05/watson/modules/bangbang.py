from watson.modules.chatmodule import ChatModule, command_function


class BangBangModule(ChatModule):
    '''
    This is a module to contain the "!!" command, which repeats the last command a user gave
    '''

    __module_name__ = "bangbang"
    __module_description__ = "Allows users to repeat their last command"

    @command_function("!!", storable = False)
    def bangbang(self, user):
        '''
        Repeats the last command the user gave, if there was one
        '''
        
        command = self.bot.state.get_last_command(user)
        if command:
            self.bot.do_command(user, command)
            self.bot.state.store_command(user, command)
        else:
            self.speak(user, "You have no previous commands for me to repeat")
            
