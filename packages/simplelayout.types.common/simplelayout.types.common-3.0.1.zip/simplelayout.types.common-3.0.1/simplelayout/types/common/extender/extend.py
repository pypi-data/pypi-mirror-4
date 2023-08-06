from zope.component import adapts
from zope.interface import implements
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
#from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender

from Products.ATContentTypes.content.image import ATImage

from fields import image_alternative_text, show_image_title

class ImageExtender(object):
    adapts(ATImage)
    implements(IOrderableSchemaExtender)

    fields = [image_alternative_text, show_image_title]

    def __init__(self, context):
         self.context = context

    def getFields(self):
        return self.fields
        
    def getOrder(self, original):
        return original        