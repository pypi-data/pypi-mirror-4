Watson
======

The Chatbot that won America's hearts in the 80's is back! And this time, he means business!

===

## What Is Watson?

Watson is a python package that allows you to write and host your very own chatbot that will listen to your chat conversations and perform tasks based on certain commands. Watson is based on [Hubot](http://hubot.github.com/) from GitHub, but done in Python. It's easy to install and add your own modules; you should be able to get set up in a matter of minutes!

Currently, Watson will chat over two networks: Google Talk (and other Jabber networks, but really who uses those?), and Campfire. We are working on an implementation for HipChat as well. Need Watson to work on another chat network? Let us know, or feel free to write your own and submit a pull request!

Watson takes simple commands, based on which chat modules you have installed on your particular bot. By default, Watson commands must be prefaced with the word "watson" as in the following examples:

	watson how was wreck it ralph?
	watson pugme
	watson help images

## Installation

Watson can be installed using pip, with the following command:

`TODO: Get Watson pip command once we're all official`

After that, it's a matter of simply importing watson. 

## Setting Up Your Watson

Watson runs on Twisted, and can be run as a Twisted Daemon. Several examples are included in the examples directory of how to set up bots for both Campfire and Jabber. We've even included the init.d files that you can modify to point to your code, so you can run your Watson as a service on your favorite Redhat-based server.

Once Watson is installed, All you need to do is create a .tac file (These are just Python files that Twisted uses to start Daemons). Assume we're creating a Campfire bot, we'll create campfire_bot.tac. To start up a basic bot, simply have the following in the file:

	from watson.firebot import Firebot
	
	from watson.modules.images import ImageModule
	from watson.modules.help import HelpModule
	
	SUBDOMAIN="SUBDOMAIN"
	AUTH_TOKEN="AUTHTOKEN"
	COMMAND_NAMES=("watson","watson,")
	NAME = "Watson"
	ROOM_NAME = "ROOMNAME"
	
	bot = Firebot(NAME,COMMAND_NAMES,AUTH_TOKEN,SUBDOMAIN,ROOM_NAME)
	bot.add_module(ImageModule())
	bot.add_module(HelpModule())
	application = bot.connect()

Note that every .tac file MUST have a variable named application, which is returned by the bot.connect() call. Twisted uses that to run the application, and will error without it.

With that file made, all you need to do to run it is the following command:

`twistd -ny campfire_bot.tac`

Note that the bot above only includes the Images module, and the Help module (It's always a good idea to include Help...), but you can see how to add the rest of our default modules in the examples directory.


## Writing Your Own Module

The fun part of a chatbot is modifying it to suit your own particular needs. We designed Watson to be easily extensible, and we welcome any submissions for default modules we can add to Watson!

So, if you're reading this, you probably want to write your own chat module. First, it would be a good idea to check out all our default chat modules under the "modules" directory, that we've included as basic examples of Watson's functionality.

Once you've done that, let's just write an example module. For this example, we'll create a module even simpler than any we've included with Watson, let's call it PingModule. In your project, create ping.py, that looks like the following:

	from watson.modules.chatmodule import ChatModule, command_function
	
	class PingModule(ChatModule):
    
    	__module_name__ = "ping"
    	__module_description__ = "Plays ping-pong"
	
	    @command_function("ping")
    	def ping(self,user):
    		'''
    		The game of ping pong.
    		'''
    		self.speak(user,"pong")

Note that the module name and description are required. You are free to have any functions within the class, but only functions that are decorated with @command_function will be registered as valid Watson commands.

The command_function takes a command syntax (to be discussed later), and it must take a user as its first argument. That is because the "speak" function requires a user, and you will almost always want to speak in every command (when Watson's silent it's hard to tell if he listened to you).

With this file saved, just go to your .tac file, import the PingModule class, and call .add_module(PingModule) on your bot you've created. There, it's all installed! Start up Watson, send him the command "watson ping" and he will play ping pong with you!

## Command Syntax

In the above example, we have a very simple command of "ping" which can be activated by the chat command "watson ping" but obviously that's not very useful or exciting. Don't worry, you can create much more complicated command syntaxes!

All commands are tokenized by whitespace, so no token can have any whitespace in it.

* __String Literals__: In the above example, "ping" is a string literal. The command must have that word in that exact spot. Simply write the word in the command, as in `command_function("show me the money")` Watson will only run that function once it gets the command, "watson show me the money"

* __String Literals With Multiple Values__: People always have different ways of phrasing things. When you write commands, you should be aware of this, and we've provided a way for your commands to give a little leeway. Simply add a forward slash between values a string literal can have. For example, `command_function("show me the money/monies/monkeys")` would work for any of the commands "watson show me the money" or "watson show me the monkeys" Note that the command "watson show me the money/monies/monkeys" will fail, and that you must send only one of the options

* __Variable__: Say you want to get a value from a command. We can do that! In the following command, "direction" is a variable that will get passed to the function:
  `command_function("go <direction>")
   def go(self, user, direction):`
   Note that the function must take an argument with the same name as each variable in the command. In this example, the command "watson go up" would pass the string "up" to the go() function.
   
* __Variable With Required Values__: In the above example, the command would accept "watson go fish" and "watson go fubar" as valid directions, but sometimes you want to limit choices. Check out the following command syntax: `command_function("go <direction=north/west/east/south/up/down>"` In this case, only those six directions would be considered valid, and the command "go fish" would not trigger this function.

* __Variables With Prefixes and/or Postfixes__: Variables don't have to be whole words. The following is completely valid: `command_function("deploy branch=<branch>")` Note, though, that any given token cannot have multiple variable tags. The following is INVALID: `command_function("deploy branch=<branch>&user=<user>")`

* __Optional Parts__: In the Watson command syntax, you can specify part of a command as optional. To do this, just surround it with square brackets. Like the following: `command_function("m[o]ustachify <actor>")` and `command_function("deploy <branch> [because <reason>]` In the first example, the "o" is optional, and the command will work with or without it. In the latter example, you can run it with or without adding a reason, but note that if no reason is supplied, your function will not be passed a "reason" variable, and you must provide a default value for it.

## Advanced Techniques

### Protect With Math

We've included a module, MathModule that does not seem that interesting on its own. But, it provides a potentially useful functionality of protecting a command with beer goggles. Every time someone performs the command, they are asked to solve a very simple algebra problem in order to ensure that they really mean to do what they're doing. This is useful in case (like us) you use Watson to control your infrastructure and project deployments. In order to accomplish this, write a module like the following:

	from watson.modules.chatmodule import ChatModule, command_function
	from watson.modules.mathchallenge import protect_with_math
	
	class SecretModule(ChatModule):
    
    	__module_name__ = "secret"
    	__module_description__ = "Tells a secret"
    	__module_dependencies__ = ["math challenge"]

	    @command_function("tell me a secret")
	    @protect_with_math()
    	def secret(self,user):
    		'''
    		Tells a secret
    		'''
    		self.speak(user,"It is a secret to everyone")

Note that the module has a dependency on the Math Challenge module, so the Math Challenge module must be added to the bot before the Secret Module is. Read the documentation on protect_with_math() for more information.

### Adventure Game

Watson can even be used to create a group-based text adventure game. We've included AdventureGameModule to illustrate this fact, and you can simply extend that to create your own adventure (that hopefully will be more exciting than ours...)


## Requirements

Watson requires Python 2.6+, and requires the following modules:
* Twisted >= 12.2.0
* Wokkel >= 0.7.0 (for the Google Talk bot)
* Pinder >= 1.0.1 (for the Campfire bot)