from collective.plonetruegallery.utils import createSettingsFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery.browser.views.display import \
    BatchingDisplayType
from collective.plonetruegallery.interfaces import IBaseSettings
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.ptg.garagedoor')

class IGaragedoorDisplaySettings(IBaseSettings):
    garagedoor_columns = schema.Int(
        title=_(u"label_garagedoor_columns",
            default=u"Number of images before a forced new row (use a high "
                    u"number if you dont want this)"),
        default=3,
        min=1)
    garagedoor_imagewidth = schema.Int(
        title=_(u"label_garagedoor_imagewidth",
            default=u"Width of (each) image"),
        default=400,
        min=50)
    garagedoor_imageheight = schema.Int(
        title=_(u"label_garagedoor_imageheight",
            default=u"Height of (each) image"),
        default=260,
        min=50)
    garagedoor_effectcount = schema.Int(
        title=_(u"label_garagedoor_effectcount",
                default=u"How many effects?"),
        default=8,
        max=8,
        min=1)  
    garagedoor_effectoffset = schema.Int(
        title=_(u"label_garagedoor_effectoffset",
                default=u"Offset effects by"),
        default=0,
        max=7,
        min=0)  
        
    garagedoor_use_icons = schema.Bool(
        title=_(u"label_garagedoor_use_icons",
            default=u"Use Thumbnail size instead of Size"),
        default=False)

    garagedoor_style = schema.Choice(
        title=_(u"label_garagedoor_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_garagedoor_style_default",
                    default=u"Default")),
            SimpleTerm("styleII.css", "styleII.css",
                _(u"label_garagedoor_styleII",
                    default=u"Black Style")),
            SimpleTerm("no_style.css", "no_style.css",
                _(u"label_garagedoor_style_no",
                    default=u"No style / css file")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_garagedoor_style_custom",
                    default=u"Custom css file")
            )
        ]))

    garagedoor_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")


class GaragedoorDisplayType(BatchingDisplayType):
    name = u"garagedoor"
    schema = IGaragedoorDisplaySettings
    description = _(u"label_garagedoor_display_type",
        default=u"Garagedoor")

    def javascript(self):
	
        return u"""
<script type="text/javascript">
$(document).ready(function() {
    $('.effect0').hover(function() {
        $('.imagebox', $(this)).stop().animate({top: '%(boxheight)ipx'}, %(speed)i);
    },function() {
        $('.imagebox', $(this)).stop().animate({top: '0'}, %(speed)i);
    });
    
    $('.effect1').hover(function() {
        $('.imagebox', $(this)).stop().animate({left: '-%(boxwidth)ipx'}, %(speed)i);
    },function() {
        $('.imagebox', $(this)).stop().animate({left: '0'}, %(speed)i);
    });
    
    $('.effect2').hover(function() {
        $('.imagebox', $(this)).stop().animate({left: '-%(boxwidth)ipx', top: '%(boxheight)ipx'}, %(speed)i);
    },function() {
        $('.imagebox', $(this)).stop().animate({left: '0', top: '0'}, %(speed)i);
    });
    
    $('.effect3').hover(function() {
        $('.imagebox', $(this)).stop().animate({top: '-%(boxheight)ipx'}, %(speed)i);
    },function() {
        $('.imagebox', $(this)).stop().animate({top: '0'}, %(speed)i);
    });
    
    $('.effect4').hover(function() {
        $('.imagebox', $(this)).stop().animate({left: '%(boxwidth)ipx'}, %(speed)i);
    },function() {
        $('.imagebox', $(this)).stop().animate({left: '0'}, %(speed)i);
    });
    
    $('.effect5').hover(function() {
        $('.imagebox', $(this)).stop().animate({left: '%(boxwidth)ipx', top: '%(boxheight)ipx'}, %(speed)i);
    },function() {
        $('.imagebox', $(this)).stop().animate({left: '0', top: '0'}, %(speed)i);
    });   
    $('.effect6').hover(function() {
        $('.imagebox', $(this)).stop().animate({left: '%(boxwidth)ipx', top: '-%(boxheight)ipx'}, %(speed)i);
    },function() {
        $('.imagebox', $(this)).stop().animate({left: '0', top: '0'}, %(speed)i);
    });   
    
    $('.effect7').hover(function() {
        $('.imagebox', $(this)).stop().animate({left: '-%(boxwidth)ipx', top: '-%(boxheight)ipx'}, %(speed)i);
    },function() {
        $('.imagebox', $(this)).stop().animate({left: '0', top: '0'}, %(speed)i);
    });   
});

</script>
""" % {
    'speed': self.settings.duration,
    'effect': self.settings.garagedoor_effect,
    'path' : self.portal_url + '/++resource++ptg.garagedoor',
    'boxheight': self.settings.garagedoor_imageheight,
    'boxwidth': self.settings.garagedoor_imagewidth,
}

    def css(self):
        relpath = '++resource++ptg.garagedoor'
        style = '%s/%s/%s' % (self.portal_url, relpath,
            self.settings.garagedoor_style)

        if self.settings.garagedoor_style == 'custom_style':
            style = '%s/%s' % (self.portal_url,
                self.settings.garagedoor_custom_style)

        return u"""
        <style>
.garagedoor div {
    height: %(boxheight)ipx;
    width: %(boxwidth)ipx;
}

</style>
<link rel="stylesheet" type="text/css" href="%(style)s"/>
""" % {
        'columns': self.settings.garagedoor_columns,
        'boxheight': self.settings.garagedoor_imageheight,
        'boxwidth': self.settings.garagedoor_imagewidth,
        'style': style
       }
GaragedoorSettings = createSettingsFactory(GaragedoorDisplayType.schema)
