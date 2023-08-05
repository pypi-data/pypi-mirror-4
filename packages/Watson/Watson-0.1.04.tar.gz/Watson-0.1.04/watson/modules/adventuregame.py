from watson.modules.chatmodule import ChatModule, command_function


class AdventureRoom(object):
    '''
    Represents a room in an adventure game. It keeps track of the rooms relative to it, as well as the game it's from.
    '''

    def __init__(self, game, description, look_description, north=None, east=None, south=None, west=None, up=None, down=None):
        self.game = game
        self.description = description
        self.look_description = look_description
        self.north = north
        self.east = east
        self.south = south
        self.west = west
        self.up = up
        self.down = down

    def look(self, user):
        '''
        Describes the room
        '''
        self.game.speak(user, self.look_description + "\n" + self.exits())

    def arrive(self, user):
        '''
        This is the function that gets called upon arrival to this room
        '''
        self.game.speak(user, self.description + "\n" + self.exits())

    def exits(self):
        '''
        Provides a list of the possible exits from this room
        '''
        valid_exits = zip(["North", "East", "South", "West", "Down", "Up"],
                          [self.north, self.east, self.south, self.west, self.down, self.up])
        valid_exits = [k for k, v in valid_exits if v is not None]
        if not valid_exits:
            return "There are no exits from here! Game over, man! Game over!"
        return "Exits are: " + ", ".join(valid_exits)

    def _go(self, user, direction):
        self.game.location = direction
        self.game.rooms[self.game.location].arrive(user)

    def go(self, user, direction):
        '''
        Moves the game state from this room to whichever room is in the direction provided
        '''
        if direction == "north" and self.north is not None:
            self._go(user, self.north)
        elif direction == "south" and self.south is not None:
            self._go(user, self.south)
        elif direction == "east" and self.east is not None:
            self._go(user, self.east)
        elif direction == "west" and self.west is not None:
            self._go(user, self.west)
        elif direction == "up" and self.up is not None:
            self._go(user, self.up)
        elif direction == "down" and self.down is not None:
            self._go(user, self.down)
        else:
            self.game.speak(user, "You cannot go that way")


class AdventureGameModule(ChatModule):
    '''
    This module represents an adventure game, which keeps track of its own state (across all users).
    
    During construction it generates a list of its own rooms, and it handles the commands to move around them and interact with them.
    
    TODO: Add inventory system as well as the associated commands
    '''

    __module_name__ = "adventure game"
    __module_description__ = "It's an adventure! Go explore!"

    def __init__(self):
        self.location = 0
        self.rooms = []

        self._add_room("You are in an office cubicle.", "The walls are grey and drab. Nothing is here but a stapler. You cannot take the stapler.", north=1)
        self._add_room("You find yourself standing in a hallway.", "The hall is lined with cubicles on either side but you'd best stay clear of them.", south=0, north=2)
        self._add_room("Now you're in a lobby! Hooray!", "There's a desk for a security guard, and everything. Quite the lobby.", east=3, south=1)
        self._add_room("You have made it outside. Good for you! Now watch a bird or something.", "It's kind of cold out. You wish you brought a jacket.")

    def _add_room(self, description, look_description, north=None, east=None, south=None, west=None, up=None, down=None):
        self.rooms.append(AdventureRoom(self, description, look_description, north, east, south, west, up, down))

    @command_function("look")
    def look(self, user):
        '''
        Check out the room you're in. Get a detailed view of your surroundings.
        '''
        self.rooms[self.location].look(user)

    @command_function("go <direction>")
    def go(self, user, direction):
        '''
        Go somewhere, explore something new.
        '''
        self.rooms[self.location].go(user, direction)
