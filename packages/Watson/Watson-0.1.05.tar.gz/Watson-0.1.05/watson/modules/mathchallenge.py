import random
from functools import wraps

from watson.modules.chatmodule import ChatModule, command_function


def protect_with_math(check_if_protected=None):
    '''
    This function acts as a wrapper for any chat module command. Instead of the command being run directly, the user will be asked an algebraic question.
    When that user answers correctly, the command will be run.
    
    ARGUMENTS
        check_if_protected (optional) - a function that is passed in all the arguments of the wrapped function, and returns True or False based on whether the command should be protected with math
    
    RETURNS
        A wrapper function to wrap the command that should be protected with math
        
    EXAMPLES
        @command_function("tell me the secret")
        @protect_with_math()
        def secret(self, user):
            self.speak(user, "It is a secret to everyone.")
            
        > watson tell me the secret
        Answer me this math problem: 8 - 5
        > 3
        It is a secret to everyone.

        @command_function("show me the way to <city>")
        @protect_with_math(lambda self, user ,city: return city == "santa fe")
        def secret(self, user):
            self.speak(user, "No.")
        
        > watson show me the way to santa fe
        Answer me this math problem: 2 * 1
        > 2
        No.
        
        > watson show me the way to berkeley
        No.
        
    '''
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
    '''
    This chat module allows for the users to ask for math challenges, and it also provides the ability for other chat modules to use protect_with_math
    
    It uses state to remember which user was given the math problem, and will only take the correct answer from that user.
    '''

    __module_name__ = "math challenge"
    __module_description__ = "This module will allow people to ask for an arithmetic question which they must answer. Also, it allows for the use of the protect_with_math decorator."

    def _determine_math_challenge(self):
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

    def incorrect_math(self,user,*args):
        self.speak(user,"Nope, you've been publically shamed about your algebra skills. I don't have retries implemented yet so you'll have to repeat the last command.")

    def correct_math(self,user,*args):
        self.speak(user,"Good job!")

    @command_function("mathme")
    def math_challenge(self, user, answer_callback = None, args = []):
        '''
        Asks a simple arithmetic problem of the user, then logs that the chatbot should be listening for the correct answer from that user only
        '''
        if not answer_callback:
            answer_callback = self.correct_math
            args = [user]
        problem, answer = self._determine_math_challenge()
        self.speak(user,"Answer me this math problem: " + problem)
        self.bot.state.looking_for_answer(user, answer, answer_callback, self.incorrect_math, args)
