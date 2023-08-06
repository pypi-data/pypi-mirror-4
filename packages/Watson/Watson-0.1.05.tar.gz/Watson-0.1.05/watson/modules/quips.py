import datetime

from watson.modules.chatmodule import ChatModule, command_function
from watson.modules.mathchallenge import protect_with_math


class QuipsModule(ChatModule):
    '''
    This module contains commands for silly one-liners. Because it has a function that uses protect_with_math,
    it must be added to the chatbot after the math challenge module.
    '''

    __module_name__ = "quips"
    __module_description__ = "A bunch of one-liners"
    __module_dependencies__ = ["math challenge"]

    @command_function("what's brown and sounds like a bell[?]")
    def joke(self, user):
        self.speak(user, "Dung!")

    @command_function("what time is it[?]")
    def whattime(self, user):
        self.speak(user, "Hammer time, of course")

    @command_function("seriously[,] what time is it[?]")
    def whattimereally(self, user):
        self.speak(user, datetime.datetime.utcnow().strftime("%m/%d/%y %H:%M GMT"))

    @command_function("what are the rules[?]")
    def rules(self, user):
        self.speak(user, "I'll be honest, I can't bring myself to actually make the Fight Club joke.")

    @command_function("status")
    def status(self, user):
        self.speak(user, "believe me I am still alive. I'm doing Science and I'm still alive. I feel FANTASTIC and I'm still alive. While you're dying I'll be still alive. And when you're dead I will be still alive.")

    @command_function("[<sudo=sudo>] make me a sandwich")
    def sandwich(self, user, sudo=""):
        if sudo == "sudo":
            self.speak(user, "Okay.")
        else:
            self.speak(user, "No, make it yourself.")

    @command_function("tell me the secret")
    @protect_with_math()
    def secret(self, user):
        self.speak(user, "It is a secret to everyone.")

    @command_function("be <emotion=creepy/happy/sad>")
    def emotional(self, user, emotion):
        gif = ""
        if emotion == "sad":
            gif = "http://media.tumblr.com/tumblr_m7qvh0HmjW1r63r28.gif"
        elif emotion == "creepy":
            gif = "http://gifsforum.com/images/gif/happy/grand/Ill-eat-your-childern.gif"
        elif emotion == "happy":
            gif = "http://www.reactiongifs.com/wp-content/gallery/yes/tumblr_lm11bt4OaK1qe6xr2.gif"
        self.speak(user, gif)
