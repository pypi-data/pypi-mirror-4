from zope.interface import implements
from zope.component import adapts
from zope.i18nmessageid import MessageFactory

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.markerfield.field import InterfaceMarkerField

from Products.ATContentTypes.interface import IATContentType
from Products.Archetypes.atapi import BooleanWidget

# from Products.ATContentTypes.interface.document import IATDocument

from adi.workingcopyflag.interfaces import IWorkingcopyFlaggableObject

_ = MessageFactory('adi.workingcopyflag')

class ContentTypeExtender(object):
    """Adapter that adds custom metadata."""
    adapts(IATContentType)

    implements(ISchemaExtender)

    _fields = [
        InterfaceMarkerField("workingcopyflag",
            schemata = "settings",
            interfaces = (IWorkingcopyFlaggableObject,),
            languageIndependent = True,#
            visible = {'edit':'hidden', 'view':'hidden'},
            widget = BooleanWidget(
                label = _(u"label_workingcopyflag_title",
                    default=u"Has a workingcopy"),
                description = _(u"help_workingcopyflag",
                    default=u"If this field is marked, this item does have a working copy."),
                ),
            ),
        ]
    
    def __init__(self, contentType):
        pass

    def getFields(self):
        return self._fields
