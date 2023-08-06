from Products.Five import BrowserView

class Search(BrowserView):

    def __call__(self):
        return self.context.restrictedTraverse("search")()

