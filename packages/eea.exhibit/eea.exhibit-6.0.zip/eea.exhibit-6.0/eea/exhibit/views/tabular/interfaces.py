""" Tabular views interfaces
"""
from zope import schema
from zope.interface import Interface
from eea.app.visualization.views.interfaces import IVisualizationView

class IExhibitTabularView(IVisualizationView):
    """ Exhibit tabular view
    """

class IExhibitTabularEdit(Interface):
    """ Exhibit tabular edit
    """
    columns = schema.List(
        title=u'Columns',
        description=u'Select columns to be shown in table view',
        required=False, unique=True,
        value_type=schema.Choice(
            vocabulary="eea.daviz.vocabularies.FacetsVocabulary")
    )
    details = schema.Bool(
        title=u'Display details column',
        description=(u"Select this if you want to display a column with "
                     "a 'more' link to item details"),
        required=False
    )
    lens = schema.Text(
        title=u"Lens template",
        description=(u""
            "Edit custom exhibit lens. Leave it blank to use the default one. "
            "See more details "
            "http://www.simile-widgets.org/wiki/Exhibit/Lens_Templates"),
        required=False
    )
