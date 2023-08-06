from Acquisition import aq_inner, aq_parent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from simplelayout.base.interfaces import IBlockConfig, IScaleImage
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryMultiAdapter



#dummy for refactoring
_ = lambda x: x

class DownloadImage(BrowserView):

    def __call__(self):
        if 'image' in self.context.Schema():
            image = self.context.getWrappedField('image')
            return image.download(self.context)
        return None


class paragraphView(BrowserView):
    template = ViewPageTemplateFile('paragraph_version_view.pt')

    def __call__(self):
        context = aq_inner(self.context).aq_explicit
        #auto redirect to the anchor
        param = '/#%s' % context.id

        return self.context.REQUEST.RESPONSE.redirect(
            context.aq_parent.absolute_url() + param)

    @property
    def macros(self):
        return {'main': self.template.macros['main']}


class FileView(BrowserView):

    def __init__(self, context, request):
        super(FileView, self).__init__(context, request)
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.sl_portal_url = self.portal_state.portal_url()
        self.parent = aq_parent(aq_inner(self.context))


class BlockView(BrowserView):

    def __init__(self, context, request):
        super(BlockView, self).__init__(context, request)
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.sl_portal_url = self.portal_state.portal_url()
        self.blockconf = IBlockConfig(self.context)
        self.image_layout = self.blockconf.image_layout

    def getCSSClass(self):
        layout = self.image_layout
        if layout is None:
            return 'sl-img-no-image'
        cssclass = 'sl-img-'+layout
        return cssclass

    def checkForImage(self):
        #check for a 'image' field in schemata
        if getattr(self.context.aq_explicit, 'getImage', False):
            if self.context.getImage():
                return True
        return False

    def getImageTag(self):
        alt = unicode(self.context.getImageAltText(),
                      self.context.getCharset())
        title = unicode(self.context.getImageCaption(),
                        self.context.getCharset())

        if not title:
            title = alt

        image_util = getUtility(
            IScaleImage,
            name='simplelayout.image.scaler')
        img_attrs = image_util.get_image_attributes(self.context)
        scales = queryMultiAdapter((self.context, self.request), name="images")

        if self.context.getField('image'):
            if img_attrs['width'] == 0 and img_attrs['height'] == 0:
                # either there is no image or we use a layout such as
                # "no-image" which does not show the image - we do not
                # need to create a scale in this case nor to return a
                # <img> HTML tag.
                return ''

            return scales.scale(
                'image',
                width=img_attrs['width'],
                height=img_attrs['height']).tag(title=title, alt=alt)

        return ''

    def image_wrapper_style(self):
        """ sets width of the div wrapping the image, so the
        caption linebreaks
        """

        image_util = getUtility(
            IScaleImage,
            name='simplelayout.image.scaler')
        img_attrs = image_util.get_image_attributes(self.context)
        return "width: %spx" % img_attrs['width']

    def getBlockHeight(self):
        height = self.blockconf.block_height
        return  height and '%spx' % height or ''

    @property
    def wtool(self):
        return getToolByName(self.context, 'portal_workflow')

    def related_items(self):
        """Shows related items if it behaves like a teaser-block"""

        context = aq_inner(self.context)
        res = ()
        if base_hasattr(context, 'getRawRelatedItems'):
            catalog = getToolByName(context, 'portal_catalog')
            related = context.getRawRelatedItems()
            if not related:
                return ()
            brains = catalog(UID=related)
            if brains:
                # build a position dict by iterating over the items once
                positions = dict([(v, i) for (i, v) in enumerate(related)])
                # We need to keep the ordering intact
                res = list(brains)

                def _key(brain):
                    return positions.get(brain.UID, -1)

                res.sort(key=_key)
        return res


class ImageView(BrowserView):

    def __init__(self, context, request):
        super(BrowserView, self).__init__(context, request)
        blockconf = IBlockConfig(self.context)
        self.image_layout = blockconf.image_layout

    def getCSSClass(self):
        layout = self.image_layout
        if layout is None:
            return 'sl-img-no-image'
        cssclass = 'sl-img-'+layout
        return cssclass

    def getImageTag(self):
        """Use plone.app.imaging to scale and display the right image
        """
        title = hasattr(self.context, 'imageAlternativeText') and \
            self.context.imageAlternativeText or ''
        alt = title

        image_util = getUtility(
            IScaleImage,
            name='simplelayout.image.scaler')

        img_attrs = image_util.get_image_attributes(self.context)
        scales = queryMultiAdapter((self.context, self.request), name="images")
        if self.context.getField('image'):
            if img_attrs['width'] == 0 and img_attrs['height'] == 0:
                # either there is no image or we use a layout such as
                # "no-image" which does not show the image - we do not
                # need to create a scale in this case nor to return a
                # <img> HTML tag.
                return ''

            return scales.scale(
                'image',
                width=img_attrs['width'],
                height=img_attrs['height']).tag(title=title, alt=alt)

        return ''

    def showTitleOfImage(self):
        show_image_title = hasattr(self.context, 'showImageTitle') and \
            self.context.showImageTitle or False
        return show_image_title
