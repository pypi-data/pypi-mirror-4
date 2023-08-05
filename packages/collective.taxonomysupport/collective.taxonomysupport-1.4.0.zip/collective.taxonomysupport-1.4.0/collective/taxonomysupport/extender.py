from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender, IOrderableSchemaExtender    
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes.atapi import LinesField,MultiSelectionWidget
from Products.ATContentTypes.interface.interfaces import IATContentType

from collective.taxonomysupport.interfaces import ITaxonomyLayer
from collective.taxonomysupport import taxonomysupportMessageFactory as _


class siteAreasField(ExtensionField, LinesField):
    """Extension field for siteAreas"""


class TaxonomyArchetypesExtender(object):

    adapts(IATContentType)

    implements(IOrderableSchemaExtender,IBrowserLayerAwareExtender)
    layer = ITaxonomyLayer

    fields = [siteAreasField(name='siteAreas',
                               vocabulary_factory = 'collective.taxonomyvocab',
                               default_method="getDefaultTaxonomy",
                               schemata='categorization',
                               widget=MultiSelectionWidget(label=_(u'label_site_areas', default=u'Site areas'),
                                                           description=_(u'help_site_areas',
                                                                         default=u'Select some site areas.'),
                                                           condition="object/showAreas",
                               ),
            
            )]

    def __init__(self, context):
         self.context = context

    def getFields(self):
        return self.fields

    def getOrder(self, original):
            return original
