""" List facet
"""
from zope.interface import Interface
from zope.schema import TextLine, Bool
from eea.app.visualization.facets.interfaces import IVisualizationFacet

class IExhibitListFacet(IVisualizationFacet):
    """ Exhibit list facet
    """
    def gett(key, default):
        """ Get data property
        """

class IExhibitListFacetEdit(Interface):
    """ Exhibit list facet edit
    """
    label = TextLine(title=u'Friendly name',
                     description=u'Label for exhibit facet')
    show = Bool(title=u'Visible', description=u'Is this facet visible?',
            required=False)
