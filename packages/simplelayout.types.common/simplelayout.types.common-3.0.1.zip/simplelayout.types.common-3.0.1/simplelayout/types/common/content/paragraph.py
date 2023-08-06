from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import getToolByName
from simplelayout.base.interfaces import ISimpleLayoutBlock
from simplelayout.types.common import config
from simplelayout.types.common.interfaces import IParagraph
from simplelayout_schemas import textSchema, imageSchema, finalize_simplelayout_schema
from zope.interface import implements


from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone import public as atapi
else:
    from Products.Archetypes import atapi


schema = atapi.Schema((
     atapi.BooleanField('showTitle',
                schemata='default',
                default=0,
                widget=atapi.BooleanWidget(description = "Show title",
                                             description_msgid = "simplelayout_help_showtitle",
                                             label = "Show Title",
                                             label_msgid = "simplelayout_label_showtitle",
                                             i18n_domain = "simplelayout",
                                             )),
     atapi.BooleanField('imageClickable',
                schemata='image',
                default=0,
                widget=atapi.BooleanWidget(description = "imageClickable",
                                             description_msgid = "simplelayout_help_imageClickable",
                                             label = "Image Clickable",
                                             label_msgid = "simplelayout_label_imageClickable",
                                             i18n_domain = "simplelayout",
                                             )),

     atapi.BooleanField('teaserblock',
                schemata='settings',
                default=0,
                widget=atapi.BooleanWidget(description = "teaser blocks shows their related items (ex. for frontpage)",
                                             description_msgid = "simplelayout_help_teaserblock",
                                             label = "Tick if this block is a teaser",
                                             label_msgid = "simplelayout_label_teaserblock",
                                             i18n_domain = "simplelayout",
                                             )),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

paragraph_schema = ATContentTypeSchema.copy() + \
    schema.copy() + textSchema.copy() + imageSchema.copy()

paragraph_schema['excludeFromNav'].default = True
paragraph_schema['title'].required = False
finalize_simplelayout_schema(paragraph_schema)
paragraph_schema['description'].widget.visible = {'edit': 0, 'view': 0}
paragraph_schema['title'].searchable = 0
paragraph_schema.moveField('teaserblock',before="relatedItems")
paragraph_schema['text'].widget.filter_buttons = ('image', )

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Paragraph(ATDocumentBase):
    """
    """
    security = ClassSecurityInfo()
    implements(IParagraph, ISimpleLayoutBlock)
    schema = paragraph_schema

    # Methods

    #XXX we should use eventhandler
    #special workarround for empty titles, otherwise we have "[...]"
    #results in the search function
    def setTitle(self, value):
        portal_transforms = getToolByName(self, 'portal_transforms')
        field = self.schema['title']
        if not value:
            #XXX use crop function
            new_value = self.REQUEST.get('text',None)
            if new_value is not None:
                formatted = portal_transforms.convertTo('text/plain', new_value).getData().replace('\r','').replace('\n','')
                cropped = len(formatted) > 30 and formatted[:30] or formatted
                last_space = cropped.rfind(' ')
                if last_space == -1:
                    pass
                else:
                    cropped = cropped[:last_space]
                field.set(self,cropped.lstrip())
        else:
            field.set(self,value)


    security.declareProtected(View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        if 'title' not in kwargs:
            if self.getImageAltText():
                kwargs['title'] = self.getImageAltText()
            elif self.getImageCaption():
                kwargs['title'] = self.getImageCaption()
            else:
                kwargs['title'] = self.Title()
        if 'alt' not in kwargs:
            kwargs['alt'] = self.getImageAltText()
        return self.getField('image').tag(self, **kwargs)

atapi.registerType(Paragraph, config.PROJECTNAME)
