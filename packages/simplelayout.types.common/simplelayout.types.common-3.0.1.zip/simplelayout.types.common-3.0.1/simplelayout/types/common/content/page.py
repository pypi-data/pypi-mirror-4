from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from simplelayout.base.interfaces import ISimpleLayoutCapable
from simplelayout.types.common.config import PROJECTNAME
from simplelayout.types.common.interfaces import IPage
from simplelayout_schemas import finalize_simplelayout_schema
from zope.interface import implements
from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget

from Products.ATContentTypes.config import HAS_LINGUA_PLONE

if HAS_LINGUA_PLONE:
    from Products.LinguaPlone import public as atapi
else:
    from Products.Archetypes import atapi



schema = atapi.Schema((
        atapi.ReferenceField('relatedItems',
           relationship = 'relatesTo',
           schemata='settings',
           multiValued = True,
           isMetadata = True,
           languageIndependent = False,
           index = 'KeywordIndex',
           write_permission = ModifyPortalContent,
           widget = ReferenceBrowserWidget(
                 allow_search = True,
                 allow_browse = True,
                 show_indexes = False,
                 force_close_on_insert = True,
                 i18n_domain="plone",
                 label="Related Items",
                 label_msgid="label_related_items",
                 description="",
                 description_msgid="",
                 visible = {'edit' : 'visible', 'view' : 'invisible' }
                 )
           )
),
)

page_schema = ATFolder.schema.copy() + ConstrainTypesMixinSchema.copy() \
    + schema.copy()

finalize_simplelayout_schema(page_schema, folderish=True)


class Page(ATFolder):
    """
    """
    implements(IPage, ISimpleLayoutCapable)
    security = ClassSecurityInfo()

    schema = page_schema

    def getPageTypes(self):
        catalog = getToolByName(self, "portal_catalog")
        return catalog.uniqueValuesFor("page_types")

atapi.registerType(Page, PROJECTNAME)
