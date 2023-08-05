from collective.plonetruegallery.utils import createSettingsFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery.browser.views.display import \
    BatchingDisplayType
from collective.plonetruegallery.interfaces import IBaseSettings
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.ptg.sheetgallery')

class ISheetgalleryDisplaySettings(IBaseSettings):
    sheetgallery_columns = schema.Int(
        title=_(u"label_sheetgallery_columns",
            default=u"Number of images before a forced new row (use a high "
                    u"number if you dont want this)"),
        default=3,
        min=1)
    sheetgallery_effectcount = schema.Choice(
        title=_(u"label_sheetgallery_effectcount",
                default=u"How many slide in effects (4 is from all sides)"),
        default=4,
        vocabulary=SimpleVocabulary([
            SimpleTerm(1, 1,
                _(u"label_sheetgallery_effectcount1",
                    default=u"1 (left)")),
            SimpleTerm(2, 2,
                _(u"label_sheetgallery_effectcount2", default=u"2 (left, top)")),
            SimpleTerm(3, 3,
                _(u"label_sheetgallery_effectcount3", default=u"3 (left, top, right)")),
            SimpleTerm(4, 4,
                _(u"label_sheetgallery_effectcount4",
                    default=u"4 (left, top, right, bottom)")
            )
        ]))
    sheetgallery_imagewidth = schema.Int(
        title=_(u"label_sheetgallery_imagewidth",
            default=u"Width of (each) image"),
        default=400,
        min=50)
    sheetgallery_imageheight = schema.Int(
        title=_(u"label_sheetgallery_imageheight",
            default=u"Height of (each) image"),
        default=260,
        min=50)
    sheetgallery_use_icons = schema.Bool(
        title=_(u"label_sheetgallery_use_icons",
            default=u"Use Thumbnail size instead of Size"),
        default=False)
    sheetgallery_downloadlink = schema.Bool(
        title=_(u"label_sheetgallery_downloadlink",
            default=u"Show download link"),
        default=False)
    sheetgallery_overlay_opacity = schema.Choice(
        title=_(u"label_sheetgallery_overlay_opacity",
                default=u"Opacity on mouse over"),
        default=0.3,
        vocabulary=SimpleVocabulary([
            SimpleTerm(0, 0,
                _(u"label_sheetgallery_overlay_opacity0",
                    default=u"0 Hide it completely")),
            SimpleTerm(0.1, 0.1,
                _(u"label_sheetgallery_overlay_opacity1",
                    default=u"0.1 Almost gone")),
            SimpleTerm(0.2, 0.2,
                _(u"label_sheetgallery_overlay_opacity2", default=u"0.2")),
            SimpleTerm(0.3, 0.3,
                _(u"label_sheetgallery_overlay_opacity3", default=u"0.3")),
            SimpleTerm(0.4, 0.4,
                _(u"label_sheetgallery_overlay_opacity4",
                    default=u"0.4 A bit more")),
            SimpleTerm(0.5, 0.5,
                _(u"label_sheetgallery_overlay_opacity5", default=u"0.5")),
            SimpleTerm(0.6, 0.6,
                _(u"label_sheetgallery_overlay_opacity6",
                    default=u"0.6")),
            SimpleTerm(0.7, 0.7,
                _(u"label_sheetgallery_overlay_opacity7",
                    default=u"0.7 Quite a bit")),
            SimpleTerm(0.8, 0.8,
                _(u"label_sheetgallery_overlay_opacity8",
                    default=u"0.8 A bit much")),
            SimpleTerm(0.9, 0.9,
                _(u"label_sheetgallery_overlay_opacity9",
                    default=u"0.9 Almost nothing")),
            SimpleTerm(1, 1,
                _(u"label_sheetgallery_overlay_opacity10",
                    default=u"1 Off")
            )
        ]))
    sheetgallery_toppadding = schema.TextLine(
        title=_(u"label_sheetgallery_toppadding",
            default=u"Padding above imagetitle"),
        default=u"90px")
    sheetgallery_bottompadding = schema.TextLine(
        title=_(u"label_sheetgallery_bottompadding",
            default=u"Padding below imagedescription"),
        default=u"70px")

    sheetgallery_style = schema.Choice(
        title=_(u"label_sheetgallery_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_sheetgallery_style_default",
                    default=u"Default")),
            SimpleTerm("no_style.css", "no_style.css",
                _(u"label_sheetgallery_style_no",
                    default=u"No style / css file")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_sheetgallery_style_custom",
                    default=u"Custom css file")
            )
        ]))

    sheetgallery_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")


class SheetgalleryDisplayType(BatchingDisplayType):
    name = u"sheetgallery"
    schema = ISheetgalleryDisplaySettings
    description = _(u"label_sheetgallery_display_type",
        default=u"Sheetgallery")

    def javascript(self):
        return u"""
<script type="text/javascript">
$(document).ready(function() {
    //funny things first
    $('.imagebox').animate({'margin-top': '0px', 'margin-left': '0px' }, 1500);
        
    //then, when mouse enters
    $('.sheetgallery > div').mouseenter(function() {
        $('.imagebox').fadeTo('fast', 1);
        $('h3.image-title, p.image-desc, .downloadlink').hide();    
        $(this).find('.imagebox').fadeTo(100, %(overlay_opacity)s);
        $(this).find('.image-title, .image-desc, .downloadlink').slideDown(%(speed)i);
    });
});
</script>
""" % {
    'speed': self.settings.duration,
    'overlay_opacity': self.settings.sheetgallery_overlay_opacity,
}

    def css(self):
        relpath = '++resource++ptg.sheetgallery'
        style = '%s/%s/%s' % (self.portal_url, relpath,
            self.settings.sheetgallery_style)

        if self.settings.sheetgallery_style == 'custom_style':
            style = '%s/%s' % (self.portal_url,
                self.settings.sheetgallery_custom_style)

        return u"""
        <style>
.sheetgallery div {
    height: %(boxheight)ipx;
    width: %(boxwidth)ipx;
}

.sheetgallery h3.image-title {
    padding-top: %(toppadding)s;
}

.sheetgallery p.image-desc {
    padding-bottom: %(bottompadding)s;
}

.imagebox:hover {
    opcaity: %(overlay_opacity)s);
}

</style>
<link rel="stylesheet" type="text/css" href="%(style)s"/>
""" % {
        'columns': self.settings.sheetgallery_columns,
        'boxheight': self.settings.sheetgallery_imageheight,
        'boxwidth': self.settings.sheetgallery_imagewidth,
        'overlay_opacity': self.settings.sheetgallery_overlay_opacity,
        'bottompadding' : self.settings.sheetgallery_bottompadding,
        'toppadding' : self.settings.sheetgallery_toppadding,
        'style': style
       }
SheetgallerySettings = createSettingsFactory(SheetgalleryDisplayType.schema)
