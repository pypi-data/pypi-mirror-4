""" Edit facet
"""
from zope.formlib.form import Fields
from eea.app.visualization.facets.list.interfaces import IExhibitListFacetEdit
from eea.app.visualization.facets.edit import EditForm

class Edit(EditForm):
    """ Edit list facet
    """
    form_fields = Fields(IExhibitListFacetEdit)
