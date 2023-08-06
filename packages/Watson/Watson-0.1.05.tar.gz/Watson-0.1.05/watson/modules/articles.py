import urllib2, re

from watson.modules.chatmodule import ChatModule, command_function


class ArticleModule(ChatModule):
    '''
    This module provides access to articles from Wikipedia
    '''

    __module_name__ = "articles"
    __module_description__ = "Module that provides interactions with Wikipedia."

    @command_function("[random] wikipedia")
    def wikipedia(self, user):
        '''
        Displays the title, summary, and link to a random Wikipedia article.
        '''
        req = urllib2.Request('http://en.wikipedia.org/wiki/Special:Random', headers={'User-Agent': "Magic Browser"})
        response = urllib2.urlopen(req)
        page = response.read()

        title = re.search('<h1 id="firstHeading" class="firstHeading"><span dir="auto"*>(.*?)</span></h1>', page).groups()[0]

        summary = re.search('<p*>(.*?)</p>', page).groups()[0]
        killtags = re.compile(r'<[^<]*?>')
        summary = killtags.sub('', summary)

        article_url = response.url

        self.speak(user, "\n".join([x.decode('UTF-8') for x in [title, summary, article_url] if x]))
