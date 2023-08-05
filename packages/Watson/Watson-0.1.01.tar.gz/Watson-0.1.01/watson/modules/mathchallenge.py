import random
from functools import wraps

from watson.modules.chatmodule import ChatModule, command_function


def protect_with_math(check_if_protected=None):
    def inner_wrapper(f):
        @wraps(f)
        def g(*args):
            if not callable(check_if_protected) or check_if_protected(*args):
                module = args[0]  # all command_functions must have self as their first argument
                user = args[1]  # all command_functions must have user as their second argument
                return module.bot.get_module(MathChallengeModule.__module_name__).math_challenge(user, f, args=args)
            else:
                return f(*args)
        return g
    return inner_wrapper


class MathChallengeModule(ChatModule):

    __module_name__ = "math challenge"
    __module_description__ = "This module will allow people to ask for an arithmetic question which they must answer. Also, it allows for the use of the protect_with_math decorator."

    def determine_math_challenge(self):
        nums      = range(1, 11)
        operators = ['+', '-', '*']
        first     = random.choice(nums)
        second    = random.choice(nums)
        operator  = random.choice(operators)

        if operator == '-':
            (second, first) = sorted((first,second))

        problem   = '%i %s %i' % (first, operator, second)
        answer    = eval(problem)

        return problem, answer

    def incorrect_math(self,module,user,*args):
        self.speak(user,"Nope, you've been publically shamed about your algebra skills. I don't have retries implemented yet so you'll have to repeat the last command.")

    def correct_math(self,user,*args):
        self.speak(user,"Good job!")

    @command_function("mathme")
    def math_challenge(self, user, answer_callback = None, args = []):
        if not answer_callback:
            answer_callback = self.correct_math
            args = [user]
        problem, answer = self.determine_math_challenge()
        self.speak(user,"Answer me this math problem: " + problem)
        self.bot.state.looking_for_answer(user, answer, answer_callback, self.incorrect_math, args)
