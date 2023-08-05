from collective.plonetruegallery.utils import createSettingsFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery.browser.views.display import \
    BatchingDisplayType, jsbool
from collective.plonetruegallery.interfaces import IBaseSettings
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.ptg.scrollable')

class IScrollableDisplaySettings(IBaseSettings):
    scrollable_imagewidth = schema.TextLine(
        title=_(u"label_scrollable_imagewidth",
            default=u"Width of image box"),
        default=u'400px')
    scrollable_imageheight = schema.TextLine(
        title=_(u"label_scrollable_imageheight",
            default=u"Height of image box"),
        default=u'260px')
    scrollable_carouselheight = schema.TextLine(
        title=_(u"label_scrollable_carouselheight",
            default=u"Height of carousel box"),
        default=u'100px')
    scrollable_itemwidth = schema.TextLine(
        title=_(u"label_scrollable_itemwidth",
            default=u"width of each box containing a thumbnail"),
        default=u'100px')
        
    scrollable_circular = schema.Bool(
        title=_(u"label_circular",
            default=u"Shoud carousel continue after last thumb?")
        )
        
    scrollable_effect = schema.Choice(
        title=_(u"label_scrollable_effect",
            default=u"Mouseover or click"),
        default="click",
        vocabulary=SimpleVocabulary([
            SimpleTerm("click", "click",
                _(u"label_scrollable_click", default=u"Click on image")),
            SimpleTerm("mouseenter", "mouseenter",
                _(u"label_scrollable_mouseover", default=u"Mouse enter")
            )
        ]))
    scrollable_overlay_opacity = schema.Choice(
        title=_(u"label_scrollable_overlay_opacity",
                default=u"Opacity on overlay"),
        default=0.9,
        vocabulary=SimpleVocabulary([
            SimpleTerm(0.1, 0.1,
                _(u"label_scrollable_overlay_opacity1",
                    default=u"0.1 Almost gone")),
            SimpleTerm(0.2, 0.2,
                _(u"label_scrollable_overlay_opacity2", default=u"0.2")),
            SimpleTerm(0.3, 0.3,
                _(u"label_scrollable_overlay_opacity3", default=u"0.3")),
            SimpleTerm(0.4, 0.4,
                _(u"label_scrollable_overlay_opacity4",
                    default=u"0.4 A bit more")),
            SimpleTerm(0.5, 0.5,
                _(u"label_scrollable_overlay_opacity5", default=u"0.5")),
            SimpleTerm(0.6, 0.6,
                _(u"label_scrollable_overlay_opacity6",
                    default=u"0.6")),
            SimpleTerm(0.7, 0.7,
                _(u"label_scrollable_overlay_opacity7",
                    default=u"0.7 Quite a bit")),
            SimpleTerm(0.8, 0.8,
                _(u"label_scrollable_overlay_opacity8",
                    default=u"0.8 A bit much")),
            SimpleTerm(0.9, 0.9,
                _(u"label_scrollable_overlay_opacity9",
                    default=u"0.9 Almost nothing")),
            SimpleTerm(1, 1,
                _(u"label_scrollable_overlay_opacity10",
                    default=u"1 Off")
            )
        ]))
    scrollable_margin = schema.TextLine(
        title=_(u"label_scrollable_margin",
            default=u"Margin around image"),
        default=u"5px 0px 5px 0")

    scrollable_arrows = schema.Bool(
        title=_(u"label_arrows",
            default=u"Show navigation arrows?")
        )
            
    scrollable_buttons = schema.Bool(
        title=_(u"label_buttons",
            default=u"Show navigation buttons?")
        )

    scrollable_title = schema.Bool(
        title=_(u"label_showtitle",
            default=u"Show Title on large image?")
        )
    
    scrollable_description = schema.Bool(
        title=_(u"label_showdescriptions",
            default=u"Show Description on large image?")
        )
    
    scrollable_showitemdescription = schema.Bool(
        title=_(u"label_showitemdescriptions",
            default=u"Show title and description on thumbnail?")
        )
    
    scrollable_scrollbar = schema.Bool(
        title=_(u"label_scrollbar",
            default=u"Show scrollbar?")
        )
        
    scrollable_steps = schema.Int(
        title=_(u"label_steps",
            default=u"Step arrows which moves forward by x slides. Use 0 for off"),
        default=3,
        min=-1)
        
    scrollable_style = schema.Choice(
        title=_(u"label_scrollable_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_scrollable_style_default",
                    default=u"Default")),
            SimpleTerm("no_style.css", "no_style.css",
                _(u"label_scrollable_style_no",
                    default=u"No style / css file")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_scrollable_style_custom",
                    default=u"Custom css file")
            )
        ]))

    scrollable_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")

class ScrollableDisplayType(BatchingDisplayType):
    name = u"scrollable"
    schema = IScrollableDisplaySettings
    description = _(u"label_scrollable_display_type",
        default=u"Scrollable")

    def javascript(self):
        return u"""
<script type="text/javascript"
    src="%(portal_url)s/++resource++plone.app.jquerytools.plugins.js">
</script>
<script>
$(document).ready(function() {
    var root = $("#autoscroll").scrollable({circular: %(scrollable_circular)s}).autoscroll({ autoplay: %(start_automatically)s });
    window.api = root.data("scrollable");
    
    $(".items img").%(scrollable_effect)s(function() {
	    // see if same thumb is being activated 
	    if ($(this).hasClass("active")) { return; }

        // calclulate large image's URL based on the thumbnail 
        var url = $(this).attr("alt");
        
        // get large image's title 
        var title = $(this).attr("title");
        
        // get large image's description 
        var description = $(this).attr("description");
    
        // get handle to element that wraps the image and make it semi-transparent
        var wrap = $("#image_wrap").fadeTo("medium", 0.5);
    
        // the large image 
        var img = new Image();
    
    
        // call this function after it's loaded
        img.onload = function() {
    
            // make wrapper fully visible
            wrap.fadeTo("fast", 1);
    
            // change the image
            wrap.find("img").attr("src", url);
            
            //change the title
            $("#image-title").html(title);
            
            //change the description
            $("#image-description").html(description);

	    };

	    // begin loading the image
	    img.src = url;

	    // activate item
	    $(".items img").removeClass("active");
    	$(this).addClass("active");

    // when page loads simulate a "click" on the first image
    }).filter(":first").%(scrollable_effect)s();
});
</script>
""" % {
    'speed': self.settings.duration,
    'portal_url': self.portal_url,
    'scrollable_effect' : self.settings.scrollable_effect,
    'scrollable_circular': jsbool(self.settings.scrollable_circular),
    'start_automatically': jsbool(self.settings.timed),
}

    def css(self):
        relpath = '++resource++ptg.scrollable'
        style = '%s/%s/%s' % (self.portal_url, relpath,
            self.settings.scrollable_style)

        if self.settings.scrollable_style == 'custom_style':
            style = '%s/%s' % (self.portal_url,
                self.settings.scrollable_custom_style)

        return u"""
        <style>

.scrollable_wrapper {
    width: %(boxwidth)s;
}

#image_wrap {
    height: %(boxheight)s;
    padding: %(scrollable_margin)s;
}

.scrollable {
    opcaity: %(overlay_opacity)s;
	height: %(carouselheight)s;
}

.item {
	width: %(itemwidth)s;
}

a.right { left: %(boxwidth)s;}

</style>
<link rel="stylesheet" type="text/css" href="%(style)s"/>
""" % {
        'boxheight': self.settings.scrollable_imageheight,
        'boxwidth': self.settings.scrollable_imagewidth,
        'itemwidth': self.settings.scrollable_itemwidth,
        'overlay_opacity': self.settings.scrollable_overlay_opacity,
        'scrollable_margin' : self.settings.scrollable_margin,
        'carouselheight' : self.settings.scrollable_carouselheight,
        'style': style
       }
ScrollableSettings = createSettingsFactory(ScrollableDisplayType.schema)
