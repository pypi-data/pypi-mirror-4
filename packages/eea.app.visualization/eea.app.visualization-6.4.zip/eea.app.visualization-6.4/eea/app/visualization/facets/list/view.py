""" List facets view module
"""
from zope.interface import implements
from eea.app.visualization.facets.list.interfaces import IExhibitListFacet
from Products.Five.browser import BrowserView

class View(BrowserView):
    """ list facets BrowserView
    """
    implements(IExhibitListFacet)

    label = 'List'

    def __init__(self, context, request):
        """ List facets BrowserView init
        """
        self.context = context
        self.request = request
        self._data = {}

    def set_data(self, data):
        """ Set facets data
        """
        self._data = data

    def get_data(self):
        """ Get facets data
        """
        return self._data

    data = property(get_data, set_data)

    def gett(self, key, default=None):
        """ Getter facets data
        """
        return self.data.get(key, default)
