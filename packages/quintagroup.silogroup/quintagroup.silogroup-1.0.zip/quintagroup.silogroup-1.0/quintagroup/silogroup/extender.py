from zope.interface import implements
from zope.component import adapts

from Products.Archetypes.public import StringField, StringWidget

from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import (IOrderableSchemaExtender,
                                                  IBrowserLayerAwareExtender)

from quintagroup.silogroup import silogroupMessageFactory as _
from quintagroup.silogroup.interfaces import (IQuintagroupSilogroupLayer,
                                              IQuintagroupSilogroupProvider)


class SiloField(ExtensionField, StringField):
    pass


class SiloExtender(object):
    adapts(IQuintagroupSilogroupProvider)
    implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)

    layer = IQuintagroupSilogroupLayer

    fields = [
        SiloField("silo",
                  widget=StringWidget(
                      label=_(u"Silo Title"),
                      description=_(u"Title for silo navigation."),
                  ),
                  ),
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        """ Manipulate the order in which fields appear.

        @param schematas: Dictonary of schemata name -> field lists

        @return: Dictionary of reordered field lists per schemata.
        """
        schematas["default"].remove("silo")
        schematas["default"].insert(schematas[
                                    "default"].index("title")+1, "silo")
        return schematas

    def getFields(self):
        return self.fields
