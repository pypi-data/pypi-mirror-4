

class Constant(object):
    '''
    A token object that represents a string literal. The literal may have a / in it to 
    denote multiple values
    '''

    def __init__(self, name):
        self.values = name.split("/")

    def match(self, word):
        '''
        Returns whether or not the word matches this constant's patterns
        '''
        return word in self.values

    def __repr__(self):
        return "/".join(self.values)


class Variable(object):
    '''
    A token object that represents a variable. All variables must contain < and >, and 
    can have a prefix and/or suffix
    '''

    def __init__(self, name):
        i = name.find("<")
        j = name.find(">")
        inner = name[i + 1:j]
        if not inner:
            raise Exception
        parts = inner.split("=")
        if len(parts) == 1:
            self.name = parts[0]
            self.options = []
        else:
            # they put in some options we should save
            self.name = parts[0]
            self.options = parts[1].split("/")

        self.prefix = name[:i]
        self.postfix = name[j + 1:]
        self.value = None

    def match(self, word):
        '''
        Returns whether or not the given word matches this variable's pattern, and sets 
        its value if there is a match
        '''
        if word.startswith(self.prefix) and word.endswith(self.postfix):
            value = word[len(self.prefix):len(word) - len(self.postfix)]
            if not self.options or value in self.options:
                self.value = value
                return True
        return False

    def __repr__(self):
        return self.prefix + "<" + self.name + ">" + self.postfix


def _create_options(string):
    '''
    Takes a syntax string and parses out all matching square brackets, and returns a list 
    of all combinations of syntaxes that could be formed if the brackets were there or not
    
    ARGUMENTS
        string - the syntax string
    
    RETURNS
        a list of syntax strings that match whether the optional pieces may be present or not
        
    EXAMPLES
        _create_options("cow") -> ["cow"]
        _create_options("cow [or lamb]") -> ["cow","cow or lamb"]
        _create_options("cow [or lamb[ada]]") -> ["cow","cow or lamb", "cow or lambada"]
    '''
    count = 0
    had_counted = False
    i = 0
    options = []

    for j in range(len(string)):
        if string[j] == "[":
            count += 1
            if not had_counted:
                i = j
            had_counted = True
        if string[j] == "]":
            count -= 1
            if not had_counted:
                raise Exception
        if count == 0 and had_counted:
            if not options:
                options = [_create_options(string[:i] + string[i + 1:j] + string[j + 1:]),
                           _create_options(string[:i] + string[j + 1:])]
                options = [x for y in options for x in y]
    if count != 0:
        raise Exception

    if not options:
        options = [string]
    return options


def _populate_results(grammar):
    '''
    Takes a grammar that has been matched, and returns the values of its variables
    '''
    result = dict()
    for node in grammar:
        if isinstance(node, Variable):
            result[node.name] = node.value
    return result


def _create_grammar(grammar_string):
    '''
    Creates a grammar construct from a string by tokenizing by whitespace, then creating 
    Constants and Variables for each token
    '''
    grammar = []

    words = grammar_string.split()

    for word in words:
        if word.find("<") >= 0 or word.find(">") >= 0:
            if not (word.count("<") == 1 and word.count(">") == 1 and word.find(">") > word.find("<")):
                raise Exception
            node = Variable(word)
        else:
            node = Constant(word)
        grammar.append(node)
    return grammar


def create_grammars(grammar_string):
    '''
    Creates a list of all possible grammar objects from a string that may contain 
    optional parts
    '''
    options = _create_options(grammar_string)
    return [_create_grammar(option) for option in options]


def _match_grammar(string, grammar):
    '''
    Determines if a string is a match for a grammar construct
    '''
    words = string.split()

    last = len(grammar) - 1
    for i, node in enumerate(grammar):
        if i > len(words) - 1:
            return False

        if i == last:
            return _populate_results(grammar) if node.match(" ".join(words[i:])) else False

        if not node.match(words[i]):
            return False


def match_grammars(string, grammars):
    '''
    Takes a string and an iterable of grammars, and returns True if any of the grammars 
    are matched by the string
    
    ARGUMENTS
        string - the input string we're matching against
        grammars - an iterable of grammars to check against
    
    RETURNS
        True if any of the grammars matched, False if not
    '''
    for grammar in grammars:
        result = _match_grammar(string, grammar)
        if result is not False:
            return result
    return False
