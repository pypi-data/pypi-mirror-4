

class State(object):

    def __init__(self, bot):
        self.bot = bot
        self.answers = dict()

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
