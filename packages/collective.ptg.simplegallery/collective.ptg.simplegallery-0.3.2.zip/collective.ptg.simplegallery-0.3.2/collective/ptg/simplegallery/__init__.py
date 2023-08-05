from collective.plonetruegallery.utils import createSettingsFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery.browser.views.display import \
    BatchingDisplayType
from collective.plonetruegallery.interfaces import IBaseSettings
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.ptg.simplegallery')

class ISimplegalleryDisplaySettings(IBaseSettings):
    simplegallery_columns = schema.Int(
        title=_(u"label_simplegallery_columns",
            default=u"Number of boxes before a forced new row (use a high "
                    u"number if you dont want this)"),
        default=3,
        min=1)
    simplegallery_boxwidth = schema.Int(
        title=_(u"label_simplegallery_boxwidth",
            default=u"Width of (each) box"),
        default=400,
        min=50)
    simplegallery_boxheight = schema.Int(
        title=_(u"label_simplegallery_boxheight",
            default=u"Height of (each) box"),
        default=260,
        min=50)
    simplegallery_use_icons = schema.Bool(
        title=_(u"label_simplegallery_use_icons",
            default=u"Use Thumbnail size instead of Size"),
        default=False)
    simplegallery_showtitle = schema.Bool(
        title=_(u"label_simplegallery_showtitle",
            default=u"Show the title?"),
        default=True)
    simplegallery_showdescription = schema.Bool(
        title=_(u"label_simplegallery_showdescription",
            default=u"Show the the description?"),
        default=True)
    simplegallery_style = schema.Choice(
        title=_(u"label_simplegallery_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_simplegallery_style_default",
                    default=u"Default")),
            SimpleTerm("small.css", "small.css",
                _(u"label_simplegallery_small",
                    default=u"Small text")),
            SimpleTerm("no_style.css", "no_style.css",
                _(u"label_simplegallery_style_no",
                    default=u"No style / css file")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_simplegallery_style_custom",
                    default=u"Custom css file")
            )
        ]))

    simplegallery_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")


class SimplegalleryDisplayType(BatchingDisplayType):
    name = u"simplegallery"
    schema = ISimplegalleryDisplaySettings
    description = _(u"label_simplegallery_display_type",
        default=u"Simplegallery")

    def javascript(self):
        return u"""
""" 

    def css(self):
        relpath = '++resource++ptg.simplegallery'
        style = '%s/%s/%s' % (self.portal_url, relpath,
            self.settings.simplegallery_style)

        if self.settings.simplegallery_style == 'custom_style':
            style = '%s/%s' % (self.portal_url,
                self.settings.simplegallery_custom_style)

        return u"""
        <style>
.simplegallery div {
    height: %(boxheight)ipx;
    width: %(boxwidth)ipx;
}

</style>
<link rel="stylesheet" type="text/css" href="%(style)s"/>
""" % {
        'columns': self.settings.simplegallery_columns,
        'boxwidth': self.settings.simplegallery_boxwidth,
        'boxheight': self.settings.simplegallery_boxheight,
        'style': style
       }
SimplegallerySettings = createSettingsFactory(SimplegalleryDisplayType.schema)
