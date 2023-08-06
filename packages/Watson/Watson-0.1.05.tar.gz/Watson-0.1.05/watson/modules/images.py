import urllib, urllib2, json, random

from watson.modules.chatmodule import ChatModule, command_function, overhear_function


class ImageModule(ChatModule):
    '''
    This chat module simply contains commands and overhear functions that return silly images. It should not be taken seriously.
    '''

    __module_name__ = "images"
    __module_description__ = "Displays often-humorous images to chat"

    @command_function("m[o]ustachify <name>")
    def moustachify(self, user, name):
        '''
        Displays a picture of the named celebrity with a mustache on their face.
        '''
        params = {"q": name,
                  "v": "1.0",
                  "safe": "active",
                  "imgtype": "face"}
        response = urllib2.urlopen("http://ajax.googleapis.com/ajax/services/search/images?" + urllib.urlencode(params))
        data = json.load(response)
        try:
            images = data['responseData']['results']
            if not images:
                self.speak(user, "Some things just cannot be moustachified...")
            else:
                url = images[0]['unescapedUrl']
                self.speak(user, "http://mustachify.me/?src=" + url)
        except:
            self.speak(user, "Looks like I couldn't find any images of that person. You may want to try again, since I'm really bad at finding images sometimes.")

    @command_function("xkcd [me]", "xkcdme")
    def xkcd(self, user):
        '''
        Displays a random xkcd comic
        '''
        result = json.load(urllib2.urlopen("http://xkcd.com/info.0.json"))
        comic = random.randint(1, result['num'])
        result = json.load(urllib2.urlopen("http://xkcd.com/{0}/info.0.json".format(comic)))
        self.speak(user, result["img"])
        self.speak(user, result["alt"])

    @command_function("pugme")
    def pugme(self, user):
        '''
        Displays a random pug picture
        '''
        response = urllib2.urlopen("http://pugme.herokuapp.com/random")
        pugs = json.load(response)
        self.speak(user, pugs["pug"])



    alot_images = [
              "http://4.bp.blogspot.com/_D_Z-D2tzi14/S8TRIo4br3I/AAAAAAAACv4/Zh7_GcMlRKo/s400/ALOT.png",
              "http://3.bp.blogspot.com/_D_Z-D2tzi14/S8TTPQCPA6I/AAAAAAAACwA/ZHZH-Bi8OmI/s1600/ALOT2.png",
              "http://2.bp.blogspot.com/_D_Z-D2tzi14/S8TiTtIFjpI/AAAAAAAACxQ/HXLdiZZ0goU/s320/ALOT14.png",
              "http://1.bp.blogspot.com/_D_Z-D2tzi14/S8TZcKXqR-I/AAAAAAAACwg/F7AqxDrPjhg/s320/ALOT13.png",
              "http://2.bp.blogspot.com/_D_Z-D2tzi14/S8Tdnn-NE0I/AAAAAAAACww/khYjZePN50Y/s400/ALOT4.png",
              "http://3.bp.blogspot.com/_D_Z-D2tzi14/S8TffVGLElI/AAAAAAAACxA/trH1ch0Y3tI/s320/ALOT6.png",
              ]
        
    @overhear_function("alot")
    def alot(self, user):
        self.speak(user,random.choice(self.alot_images))



    ackbar_images = [
                  "http://i1.wp.com/laughingsquid.com/wp-content/uploads/its-a-trap-20100127-143341.jpg",
                  "http://www.ackbar.org/images/ackbarSitting.jpg",
                  "http://profile.ak.fbcdn.net/hprofile-ak-snc6/276396_527984296_668286021_n.jpg",
                  ]
        
    @overhear_function("it's a trap")
    def ackbar(self, user):
        self.speak(user,random.choice(self.ackbar_images))