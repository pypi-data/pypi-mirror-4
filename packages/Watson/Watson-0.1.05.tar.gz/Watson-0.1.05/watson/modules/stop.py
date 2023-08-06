from watson.modules.chatmodule import ChatModule, command_function


class StopModule(ChatModule):
    '''
    This module simple provides a stop command to shut down the bot. Not very useful in production environments.
    '''

    __module_name__ = "stop"
    __module_description__ = "Provides commands to stop the bot."

    @command_function("stop/die/exit/quit", "kill thyself/thineself/yourself")
    def stop(self, user):
        '''
        Kills the bot
        '''
        self.bot.disconnect()
