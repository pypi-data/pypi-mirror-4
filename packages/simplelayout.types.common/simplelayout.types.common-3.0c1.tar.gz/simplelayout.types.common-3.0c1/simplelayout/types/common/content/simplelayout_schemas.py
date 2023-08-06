from simplelayout.types.common.config import ORIGINAL_SIZE
from Products.ATContentTypes import ATCTMessageFactory as _
from Products.CMFCore.permissions import ManagePortal
from Products.validation import ValidationChain
from Products.ATContentTypes.content.schemata import finalizeATCTSchema, marshall_register
from plone.app.blob.field import ImageField


from Products.ATContentTypes.config import HAS_LINGUA_PLONE
if HAS_LINGUA_PLONE:
    from Products.LinguaPlone import public as atapi
else:
    from Products.Archetypes import atapi


imageSchema = atapi.Schema((
    ImageField('image',
        required = False,
        original_size = ORIGINAL_SIZE,
        schemata='image',
        widget = atapi.ImageWidget(
            description = 'Choose an Image from Filesystem',
            description_msgid='simplelayout_help_image',
            label= 'Image',
            label_msgid='simplelayout_label_image',
            show_content_type = False,
            i18n_domain='simplelayout')
        ),

    atapi.StringField('imageCaption',
        required = False,
        searchable = True,
        schemata='image',
        widget = atapi.StringWidget(
            description = '',
            label = _(u'label_image_caption', default=u'Image Caption'),
            size = 40)
        ),

    atapi.StringField('imageAltText',
            schemata='image',
            required=False,
            widget=atapi.StringWidget(description='Enter a value for imageAltText.',
                description_msgid='plone_help_imageAltText',
                i18n_domain='simplelayout',
                label='Alternativ Text',
                label_msgid='plone_label_imageAltText',
            ),
        ),
),
)


textSchema = atapi.Schema((
    atapi.TextField('text',
              required=False,
              searchable=True,
              default_input_type = 'text/html',
              default_output_type = 'text/html',
              widget = atapi.RichWidget(
                        description = '',
                        label = _(u'label_body_text', default=u'Body Text'),
                        rows = 25,),
    ),
),
)



def finalize_simplelayout_schema(schema, folderish=False, moveDiscussion=True):

    finalizeATCTSchema(schema,folderish,moveDiscussion)

    # Categorization
    if schema.has_key('subject'):
        schema.changeSchemataForField('subject', 'settings')
    if schema.has_key('relatedItems'):
        schema.changeSchemataForField('relatedItems', 'settings')
    if schema.has_key('location'):
        schema.changeSchemataForField('location', 'settings')
        schema['location'].widget.visible = -1
    if schema.has_key('language'):
        schema.changeSchemataForField('language', 'settings')
        schema['language'].widget.visible = -1

    # Dates
    if schema.has_key('effectiveDate'):
        schema.changeSchemataForField('effectiveDate', 'default')
    if schema.has_key('expirationDate'):
        schema.changeSchemataForField('expirationDate', 'default')
    if schema.has_key('creation_date'):
        schema.changeSchemataForField('creation_date', 'settings')
    if schema.has_key('modification_date'):
        schema.changeSchemataForField('modification_date', 'settings')

    # Ownership
    if schema.has_key('creators'):
        schema.changeSchemataForField('creators', 'settings')
    if schema.has_key('contributors'):
        schema.changeSchemataForField('contributors', 'settings')
        schema['contributors'].widget.visible = -1
    if schema.has_key('rights'):
        schema.changeSchemataForField('rights', 'settings')
        schema['rights'].widget.visible = -1

    # Settings
    if schema.has_key('allowDiscussion'):
        schema.changeSchemataForField('allowDiscussion', 'settings')
    if schema.has_key('excludeFromNav'):
        schema.changeSchemataForField('excludeFromNav', 'settings')
    if schema.has_key('nextPreviousEnabled'):
        schema.changeSchemataForField('nextPreviousEnabled', 'settings')
        schema['nextPreviousEnabled'].widget.visible = -1

    if schema.has_key('text'):
        schema['text'].validators = ValidationChain('Validator_text',validators=('handleEmptyTextField',))

    marshall_register(schema)


    #set permissions for settings schemata

    settings_fields = [schema[key] for key in schema.keys() if schema[key].schemata == 'settings']
    for field in settings_fields:
        field.write_permission = ManagePortal



    return schema
