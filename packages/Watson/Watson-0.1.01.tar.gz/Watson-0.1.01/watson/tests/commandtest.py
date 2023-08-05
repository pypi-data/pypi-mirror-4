import unittest, re

from watson.chatbot import Chatbot
from watson.modules.images import ImageModule
from watson.modules.help import HelpModule
from watson.modules.articles import ArticleModule
from watson.modules.mathchallenge import MathChallengeModule
from watson.modules.adventuregame import AdventureGameModule
from watson.modules.quips import QuipsModule
from watson.modules.rottentomatoes import RottenTomatoesModule


class TestCommands(unittest.TestCase):

    def setUp(self):
        self.bot = Chatbot(command_names=("testbot",))

        def speak(user, message):
            self.saved_messages.append(message)
        self.bot.speak = speak

        self.bot.add_module(HelpModule())
        self.bot.add_module(MathChallengeModule())
        self.bot.add_module(ImageModule())
        self.bot.add_module(ArticleModule())
        self.bot.add_module(AdventureGameModule())
        self.bot.add_module(QuipsModule())
        self.bot.add_module(RottenTomatoesModule("ddagdga"))

    def _test_command(self, command, expectations):

        self.saved_messages = []
        self.bot.perform_action("", "testbot " + command)

        count_got = len(self.saved_messages)
        count_expected = len(expectations)
        self.assertEqual(count_got, count_expected, "Got different number of outputs than expected for \"{0}\". Got {1} expected {2}".format(command, count_got, count_expected))

        for i, exp in enumerate(expectations):
            message = self.saved_messages[i]
            self.assertTrue(re.match(exp, message), "Message \"{0}\" did not match pattern \"{1}\" for command \"{2}\"".format(message, exp, command))

    def _test_commands(self, commands):
        for command, expectations in commands:
            self._test_command(command, expectations)

    def test_images(self):
        self._test_commands([("xkcdme", ["^http://imgs.xkcd.com", ".*"]),
                            ("xkcd me", ["^http://imgs.xkcd.com", ".*"]),
                            ("xkcd", ["^http://imgs.xkcd.com", ".*"]),
                            ])

    def test_quips(self):
        self._test_commands([("what time is it", ["Hammer time, of course"]),
                            ])


if __name__ == '__main__':
    unittest.main()
