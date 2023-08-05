from Products.Five import BrowserView
from Acquisition import aq_inner

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

class View(BrowserView):

    def embedUrl(self):
        context = aq_inner(self.context)
        destUrl = self.context.getRemoteUrl()

        # http://vimeo.com/53370016
        # http://youtu.be/3X9LvC9WkkQ 
        if 'youtu' in destUrl or 'vimeo' in destUrl:
            movieCode = destUrl.split('/')[-1]

            if 'v=' in movieCode:
            
                # http://www.youtube.com/watch?v=3X9LvC9WkkQ&feature=youtu.be
                if '&' in movieCode: 
                    movieCode = find_between(movieCode, 'v=', '&')
            
                # http://www.youtube.com/watch?v=3X9LvC9WkkQ
                else: 
                    movieCode =  movieCode[8:]

            if 'youtu' in destUrl:
                transUrl = 'http://www.youtube.com/embed/' + movieCode
                return transUrl
            if 'vimeo' in destUrl:
                transUrl = 'http://player.vimeo.com/video/' + movieCode
                return transUrl
        else:
            return destUrl
