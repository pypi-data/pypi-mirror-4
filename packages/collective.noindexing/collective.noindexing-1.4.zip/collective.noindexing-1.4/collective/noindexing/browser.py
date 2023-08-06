from Products.Five import BrowserView

from collective.noindexing import patches


class Patch(BrowserView):

    def apply(self):
        reindex = False
        index = False
        unindex = False
        # in no index give select all
        if 'no-reindex' not in self.request and \
                'no-index' not in self.request and \
                'no-unindex' not in self.request:
            reindex = True
            index = True
            unindex = True
        # otherwise select one or more
        if 'no-reindex' in self.request:
            reindex = True
        if 'no-index' in self.request:
            index = True
        if 'no-unindex' in self.request:
            unindex = True

        patches.apply(reindex, index, unindex)
        return u"collective.noindexing patches applied"

    def unapply(self):
        patches.unapply()
        return u"collective.noindexing patches unapplied"
