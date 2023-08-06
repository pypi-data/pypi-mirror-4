from zope.interface import implements
from zope.component import adapts
from zope.i18nmessageid import MessageFactory

from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField

from archetypes.markerfield.field import InterfaceMarkerField
from Products.Archetypes.public import BooleanField

from Products.ATContentTypes.interface import IATContentType
from Products.Archetypes.atapi import BooleanWidget


from medialog.summaryview.interfaces import ISummaryHiddenObject

_ = MessageFactory('medialog.summaryview')


class _BooleanExtensionField(ExtensionField, BooleanField):
	pass

class ContentTypeExtender(object):
    """Adapter that adds custom field used for hiding it from showing in summary view."""
    adapts(IATContentType)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = ISummaryHiddenObject
    _fields = [
        _BooleanExtensionField("summaryview_hidden_object",
            schemata = "settings",
            interfaces = (ISummaryHiddenObject,),
            languageIndependent = True,
            widget = BooleanWidget(
                label = _(u"label_summaryview_hidden_object_title",
                    default=u"Hide Object from summary view"),
                description = _(u"help_summaryview_hidden_object",
                    default=u"Should the item be hidden from summaryview?"),
                ),
            ),
        ]
        
    def __init__(self, context):
    	self.context = context

    def getFields(self):
        return self._fields

#    def __init__(self, contentType):
#        pass