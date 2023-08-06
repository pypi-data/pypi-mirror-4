import urllib, urllib2, json

from watson.modules.chatmodule import ChatModule, command_function


class RottenTomatoesModule(ChatModule):
    '''
    This chat module is intended to allow chat bots to provide succinct movie reviews via the use of a Rotten Tomatoes API Key that must be passed in upon construction
    '''

    __module_name__ = "rotten tomatoes"
    __module_description__ = "Provides movie reviews from Rotten Tomatoes"

    def __init__(self, api_key):
        self.api_key = api_key

    def report_rotten_tomatoes(self, user, movie_data):
        percent = movie_data['ratings']['critics_score']
        if percent <= 60:
            self.speak(user, "Ewww it was certified {0}%. Pretty rotten!".format(percent))
        else:
            self.speak(user, "It was certified {0}% fresh!".format(percent))

    @command_function("how is/was <movie>[?]")
    def rotten_tomatoes(self, user, movie):
        '''
        Determines what Rotten Tomatoes thought of a movie.
        '''

        params = urllib.urlencode({"apikey": self.api_key,
                                   "q": movie,
                                   "page_limit": 10})

        response = urllib2.urlopen("http://api.rottentomatoes.com/api/public/v1.0/movies.json?" + params)
        data = json.load(response)

        if data['total'] == 1:
            self.report_rotten_tomatoes(user, data['movies'][0])
            return
        elif data['total'] > 1:
            for movie_data in data['movies']:
                if movie_data['title'].lower() == movie:
                    self.report_rotten_tomatoes(user, movie_data)
                    return
            self.speak(user, "Well, I couldn't find what you're looking for, but I did find these!\n" + "\n".join([m['title'] + ": " + str(m['ratings']['critics_score']) + "%" for m in data['movies']]))
            return
        self.speak(user, "No, you should ask about a movie name, nothing came up with that name!")
