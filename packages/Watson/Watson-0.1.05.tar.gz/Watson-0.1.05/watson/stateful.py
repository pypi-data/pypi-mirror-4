

COMMAND_HISTORY_LENGTH = 50

class State(object):
    '''
    This class represents the state of a bot. It can be used to register that the bot is 
    looking for an answer, and then the bot will check back with each subsequent response 
    to see if that's an answer it's waiting for from that user.
    
    TODO: Add retries, and global answers
    '''

    def __init__(self, bot):
        self.bot = bot
        self.answers = dict()
        self.command_history = [] # list of tuples like (username, command) that keeps track of the last commands

    def looking_for_answer(self, user, answer, answer_callback, incorrect_callback=None, args=[]):
        self.answers[user] = (answer, answer_callback, incorrect_callback, args)

    def incorrect_answer(self, user, *args):
        pass

    def check_answer(self, user, message):
        if user in self.answers:
            (answer, answer_callback, incorrect_callback, args) = self.answers[user]
            del self.answers[user]
            if str(message).lower() == str(answer).lower():
                answer_callback(*args)
            else:
                incorrect_callback(*args)

    def store_command(self, user, command):
        self.command_history.append((user, command))
        self.command_history = self.command_history[-1 * COMMAND_HISTORY_LENGTH:]
    
    def get_last_command(self, user):
        user_commands = [command for command_user, command in self.command_history if command_user == user]
        if user_commands:
            return user_commands[-1]
        
        return None