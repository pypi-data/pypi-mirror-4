from zope.interface import implements
from zope.component import adapts
from zope.i18nmessageid import MessageFactory

from archetypes.schemaextender.interfaces import ISchemaExtender, IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField

from archetypes.markerfield.field import InterfaceMarkerField
from Products.Archetypes.public import BooleanField

from Products.ATContentTypes.interface import IATContentType
from Products.Archetypes.atapi import BooleanWidget


from medialog.hidetitle.interfaces import ITitleFlaggableObject

_ = MessageFactory('medialog.hidetitle')


class _BooleanExtensionField(ExtensionField, BooleanField):
	pass

class ContentTypeExtender(object):
    """Adapter that adds custom metadata used for hiding title and description."""
    adapts(IATContentType)
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = ITitleFlaggableObject
    _fields = [
        _BooleanExtensionField("titleflaggedobject",
            schemata = "settings",
            interfaces = (ITitleFlaggableObject,),
            languageIndependent = True,
            widget = BooleanWidget(
                label = _(u"label_titleflaggedobject_title",
                    default=u"Hide title and description"),
                description = _(u"help_titleflaggedobject",
                    default=u"Should the title and description for this item be hidden?"),
                ),
            ),
        ]
        
    def __init__(self, context):
    	self.context = context

    def getFields(self):
        return self._fields

#    def __init__(self, contentType):
#        pass