from collective.plonetruegallery.utils import createSettingsFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery.browser.views.display import BaseDisplayType
from collective.plonetruegallery.interfaces import IBaseSettings
from collective.plonetruegallery.browser.views.display import jsbool
from zope import schema
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.ptg.easyslider')

class IEasysliderDisplaySettings(IBaseSettings):
    easyslider_imagewidth = schema.Int(
        title=_(u"label_easyslider_imagewidth",
            default=u"Width"),
        default=400,
        min=50)
    easyslider_imageheight = schema.Int(
        title=_(u"label_easyslider_imageheight",
            default=u"Height"),
        default=260,
        min=50)
    easyslider_lis = schema.Int(
        title=_(u"label_easyslider_lis",
            default=u"How many slides to show at the same time"),
        default=1,
        min=1)

    easyslider_use_icons = schema.Bool(
        title=_(u"label_easyslider_use_icons",
            default=u"Use Thumbnail size instead of Size"),
        default=False)
        
    easyslider_vertical = schema.Bool(
        title=_(u"label_easyslider_vertical",
            default=u"Vertical sliding?"),
        default=False)

    easyslider_continuous = schema.Bool(
        title=_(u"label_easyslider_continuous",
            default=u"Continuous? (You probably only want to use this when showing one slide at a time)"),
        default=False)

    easyslider_overlay_opacity = schema.Choice(
        title=_(u"label_easyslider_overlay_opacity",
                default=u"Opacity on text overlay"),
        default=0.3,
        vocabulary=SimpleVocabulary([
            SimpleTerm(0, 0,
                _(u"label_easyslider_overlay_opacity0",
                    default=u"0 Off")),
            SimpleTerm(0.1, 0.1,
                _(u"label_easyslider_overlay_opacity1",
                    default=u"0.1 Light")),
            SimpleTerm(0.2, 0.2,
                _(u"label_easyslider_overlay_opacity2", default=u"0.2")),
            SimpleTerm(0.3, 0.3,
                _(u"label_easyslider_overlay_opacity3", default=u"0.3")),
            SimpleTerm(0.4, 0.4,
                _(u"label_easyslider_overlay_opacity4",
                    default=u"0.4 Medium")),
            SimpleTerm(0.5, 0.5,
                _(u"label_easyslider_overlay_opacity5", default=u"0.5")),
            SimpleTerm(0.6, 0.6,
                _(u"label_easyslider_overlay_opacity6",
                    default=u"0.6")),
            SimpleTerm(0.7, 0.7,
                _(u"label_easyslider_overlay_opacity7",
                    default=u"0.7 Dark")),
            SimpleTerm(0.8, 0.8,
                _(u"label_easyslider_overlay_opacity8",
                    default=u"0.8 Very Dark")),
            SimpleTerm(0.9, 0.9,
                _(u"label_easyslider_overlay_opacity9",
                    default=u"0.9 Almost Black")),
            SimpleTerm(1, 1,
                _(u"label_easyslider_overlay_opacity10",
                    default=u"1 Pitch Dark")
            )
        ]))

        
    easyslider_controlsShow = schema.Bool(
        title=_(u"label_easyslider_controlsShow",
            default=u"""Show Controls? 
                        If this is disabled, the next 4 settings does not matter"""),
        default=True)
        
    easyslider_controlsFade = schema.Bool(
        title=_(u"label_easyslider_controlsFade",
            default=u"Fade Controls?"),
        default=True)
    
    easyslider_firstShow = schema.Bool(
        title=_(u"label_easyslider_firstShow",
            default=u"Show (go to) first button (rewind)?"),
        default=False)
    
    easyslider_lastShow = schema.Bool(
        title=_(u"label_easyslider_lastShow",
            default=u"Show (go to) last button?"),
        default=False)
        

    easyslider_numeric = schema.Bool(
        title=_(u"label_easyslider_numeric",
            default=u"Use numeric buttons instead of prev, next. first, last?"),
        default=False)
 

    easyslider_style = schema.Choice(
        title=_(u"label_easyslider_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_easyslider_style_default",
                    default=u"Default")),
            SimpleTerm("styleIII.css", "styleIII.css",
                _(u"label_easyslider_styleIII",
                    default=u"Alternative style")),
            SimpleTerm("styleII.css", "styleII.css",
                _(u"label_easyslider_styleII",
                    default=u"News Layout style")),
            SimpleTerm("styleIV.css", "styleIV.css",
                _(u"label_easyslider_styleIV",
                    default=u"News Layout style, version 2")),
            SimpleTerm("styleV.css", "styleV.css",
                _(u"label_easyslider_styleV",
                    default=u"News Layout style, version 3")),
            SimpleTerm("no_style.css", "no_style.css",
                _(u"label_easyslider_style_no",
                    default=u"No style / css file")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_easyslider_style_custom",
                    default=u"Custom css file")
            )
        ]))

    easyslider_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")


class EasysliderDisplayType(BaseDisplayType):
    name = u"easyslider"
    schema = IEasysliderDisplaySettings
    description = _(u"label_easyslider_display_type",
        default=u"Easyslider")

    def javascript(self):
        return u"""
<script type="text/javascript"
src="%(portal_url)s/++resource++ptg.easyslider/easySlider.js">
</script>
     <script type="text/javascript">
$(document).ready(function(){	
	$("#slider").easySlider({
		prevId: 		'prevBtn',
		prevText: 		'Previous',
		nextId: 		'nextBtn',	
		nextText: 		'Next',
		controlsShow:	%(controlsShow)s,
		controlsBefore:	'',
		controlsAfter:	'',	
		controlsFade:	%(controlsFade)s,
		firstId: 		'firstBtn',
		firstText: 		'First',
		firstShow:		%(firstShow)s,
		lastId: 		'lastBtn',	
		lastText: 		'Last',
		lastShow:		%(lastShow)s,				
		vertical:		%(vertical)s,
		speed: 			%(speed)i,
		auto:			%(auto)s,
		pause:			%(pause)s,
		continuous:		%(continuous)s, 
		numeric: 		%(numeric)s,
		numericId: 		'controls',
		lis: %(easyslider_lis)i,
	});
});
</script>

""" % {
        'speed':        self.settings.duration,
        'portal_url':   self.portal_url,
        'controlsShow':	jsbool(self.settings.easyslider_controlsShow),
		'controlsFade':	jsbool(self.settings.easyslider_controlsFade),
		'firstShow':	jsbool(self.settings.easyslider_firstShow),
		'lastShow':		jsbool(self.settings.easyslider_lastShow),				
		'vertical':		jsbool(self.settings.easyslider_vertical),
		'auto':			jsbool(self.settings.timed),
		'pause':		jsbool(self.settings.delay),
		'continuous':	jsbool(self.settings.easyslider_continuous), 
		'numeric': 		jsbool(self.settings.easyslider_numeric),
		'easyslider_lis': self.settings.easyslider_lis
	}

    def css(self):
        relpath = '++resource++ptg.easyslider'
        style = '%s/%s/%s' % (self.portal_url, relpath,
            self.settings.easyslider_style)

        if self.settings.easyslider_style == 'custom_style':
            style = '%s/%s' % (self.portal_url,
                self.settings.easyslider_custom_style)

        return u"""
        <style>
#slider-wrapper {
    height: %(boxheight)ipx;
    width: %(boxwidth)ipx;
}

#slider{
    height: %(boxheight)ipx !important;
    width: %(boxwidth)ipx !important;
}

#slider ul,
#slider li {
    height: %(boxheight)ipx;
}

#slider-wrapper li {
    width: %(liwidth)ipx;
}

.slider-text {
    background-color: rgba(15, 15, 15, %(overlay_opacity)f);
}

#nextBtn, #lastBtn { 
    left: %(boxwidth)ipx;
}


</style>
<link rel="stylesheet" type="text/css" href="%(style)s"/>
""" % {
        'columns': self.settings.easyslider_columns,
        'boxheight': self.settings.easyslider_imageheight,
        'boxwidth': self.settings.easyslider_imagewidth,
        'liwidth': self.settings.easyslider_imagewidth / self.settings.easyslider_lis,
        'boxwidth': self.settings.easyslider_imagewidth,
        'overlay_opacity': self.settings.easyslider_overlay_opacity,
        'style': style
       }
EasysliderSettings = createSettingsFactory(EasysliderDisplayType.schema)
