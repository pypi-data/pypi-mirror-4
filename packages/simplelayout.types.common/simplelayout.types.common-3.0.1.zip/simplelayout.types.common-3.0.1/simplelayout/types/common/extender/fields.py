from Products.Archetypes.public import StringField, StringWidget
from Products.Archetypes.public import BooleanField, BooleanWidget
from archetypes.schemaextender.field import ExtensionField
from simplelayout.types.common import websiteMessageFactory as _

class imageAlternativeTextField(ExtensionField,StringField):
    """
    """

class showImageTitle(ExtensionField, BooleanField):
    """
    """

image_alternative_text = imageAlternativeTextField('imageAlternativeText',
                                  schemata='default',
                                  widget=StringWidget(label=_('Image Alternative Text'),
                                                      description=_('image_help_image_alternative_text'),
                                                      ),
                                  required=1
                                  )

show_image_title = showImageTitle ('showImageTitle',
                schemata='default',
                default=0,
                widget=BooleanWidget(label = _('Show image title'),
                                     description = _('image_help_show_image_title'),
                                     ),
                )

