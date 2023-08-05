from zope.i18nmessageid import MessageFactory
from collective.plonetruegallery.utils import createSettingsFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery.browser.views.display import BaseDisplayType
from collective.plonetruegallery.interfaces import IBaseSettings
from zope import schema

_ = MessageFactory('collective.ptg.shufflegallery')

class IShufflegalleryDisplaySettings(IBaseSettings):
    shufflegallery_width = schema.Int(
        title=_(u"label_shufflegallery_width",
            default=u"Width of the gallery in pixels"),
        default=600)
    shufflegallery_height = schema.Int(
        title=_(u"label_shufflegallery_height",
            default=u"Height of the gallery in pixels"),
        default=500)
    shufflegallery_rows = schema.Int(
        title=_(u"label_shufflegallery_rows",
            default=u"Number of rows"),
        default=3)
    shufflegallery_columns = schema.Int(
        title=_(u"label_shufflegallery_rows",
            default=u"Number of columns"),
        default=3)    
    shufflegallery_pages = schema.Bool(
        title=_(u"label_shufflegallery_pages",
            default=u"Pages?"),
        default=True)
    shufflegallery_showtext = schema.Bool(
        title=_(u"label_shufflegallery_showtext",
            default=u"Show text?"),
        default=False)
    shufflegallery_direction = schema.Choice(
        title=_(u"label_shufflegallery_direction",
                default=u"Show thumbs in direction"),
        default="horizontal",
        vocabulary=SimpleVocabulary([
            SimpleTerm("horizontal", "horizontal",
                _(u"label_shufflegallery_horizontal",
                    default=u"Horizontal")),
            SimpleTerm("vertical", "vertical",
                _(u"label_shufflegallery_vertical",
                    default=u"Vertical")
            )
        ]))
    shufflegallery_inertia = schema.Int(
        title=_(u"label_shufflegallery_inertia",
            default=u"Inertia"),
        default=200)         
    shufflegallery_style = schema.Choice(
        title=_(u"label_shufflegallery_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_shufflegallery_style_default",
                    default=u"Default")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_shufflegallery_style_custom",
                    default=u"Custom css file")
            )
        ]))
    shufflegallery_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")


class ShufflegalleryDisplayType(BaseDisplayType):
    """ A gallery with a 'phone' feel """
    name = u"shufflegallery"
    schema = IShufflegalleryDisplaySettings
    description = _(u"label_shufflegallery_display_type",
        default=u"shufflegallery")

    def javascript(self):
        return u"""
<script type="text/javascript" src="++resource++ptg.shufflegallery/jquery.promptu-menu.js"></script>
<script type="text/javascript">
$(function(){
    $('ul.promptu-menu').promptumenu({width: %(width)i, height: %(height)i, rows: %(rows)i, columns: %(columns)i});
	$('ul.promptu-menu a').click(function(e) {
        e.preventDefault();
    });
    $('ul.promptu-menu a').dblclick(function(e) {
        window.location.replace($(this).attr("href"));
    });
});
</script>
        """  % {
        'columns': self.settings.shufflegallery_columns,
		'rows': self.settings.shufflegallery_rows,
		'direction': self.settings.shufflegallery_direction,
		'width': self.settings.shufflegallery_width,
		'height': self.settings.shufflegallery_height,
		'duration': self.settings.delay,
		'pages': self.settings.shufflegallery_pages,
		'inertia': self.settings.shufflegallery_inertia,
        }

    def css(self):
        base = '%s/++resource++ptg.shufflegallery' % (
            self.portal_url)
        style = '%(base)s/%(style)s' % {
                'base': base,
                'style': self.settings.shufflegallery_style}

        if self.settings.shufflegallery_style == 'custom_style':
            style = '%(url)s/%(style)s' % {
                'url': self.portal_url,
                'style': self.settings.shufflegallery_custom_style}

        return u"""
        <style>
</style>
<link rel="stylesheet" type="text/css" href="%(style)s"/>
""" % {
        'staticFiles': self.staticFiles,
        'style': style
       }
ShufflegallerySettings = createSettingsFactory(ShufflegalleryDisplayType.schema)