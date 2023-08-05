from Products.Five import BrowserView

from collective.noindexing import patches


class Patch(BrowserView):

    def apply(self):
        patches.apply()
        return u"collective.noindexing patches applied"

    def unapply(self):
        patches.unapply()
        return u"collective.noindexing patches unapplied"
