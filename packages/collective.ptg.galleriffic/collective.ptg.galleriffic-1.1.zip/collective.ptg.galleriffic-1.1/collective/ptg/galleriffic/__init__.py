from zope.i18nmessageid import MessageFactory
from collective.plonetruegallery.utils import createSettingsFactory
from collective.plonetruegallery.browser.views.display import \
    BaseDisplayType, jsbool
from collective.plonetruegallery.browser.views.display import jsbool
from collective.plonetruegallery.interfaces import IBaseSettings
#from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope import schema

_ = MessageFactory('collective.ptg.galleriffic')

class IGallerifficDisplaySettings(IBaseSettings):
    gallerific_showthumbs = schema.Bool(
        title=_(u"label_gallerific_showthumbs",
            default=u"Show thumbnails"),
        default=True)
        
    gallerific_toppager = schema.Bool(
        title=_(u"label_gallerific_toppager",
            default=u"Show top pager"),
        default=True)
        
    ggallerific_bottompager = schema.Bool(
        title=_(u"label_gallerific_bottompager",
            default=u"Show bottom pager"),
        default=True)
        
    gallerific_sscontrols = schema.Bool(
        title=_(u"label_gallerific_sscontrols",
            default=u"Show sscontrols"),
        default=True)
        
    gallerific_navcontrols = schema.Bool(
        title=_(u"label_gallerific_navcontrols",
            default=u"Show navcontrols"),
        default=True)
        
    
class GallerifficDisplayType(BaseDisplayType):

    name = u"galleriffic"
    schema = IGallerifficDisplaySettings
    description = _(u"label_galleriffic_display_type",
        default=u"Galleriffic")

    def css(self):
        return u"""
<link rel="stylesheet" type="text/css"
    href="%(portal_url)s/++resource++ptg.galleriffic/css/style.css" />

<style>
div.slideshow-container,div.loader,div.slideshow a.advance-link{
    height: %(height)ipx;
    width: %(box_width)ipx;
}
span.image-caption {
    width: %(width)ipx;
}
div.slideshow a.advance-link{
    line-height: %(height)ipx;
}
div.slideshow span.image-wrapper a img{
    max-width: %(width)ipx;
    max-height: %(height)ipx;
}

ul.thumbs li{
    height: %(thumbnail_height)ipx;
}
</style>
""" % {
            'portal_url': self.portal_url,
            'height': self.height,
            'width': self.width,
            'box_width': self.width + 10,
            'thumbnail_height': self.adapter.sizes['thumb']['height']
        }

    def javascript(self):
        return u"""
<script type="text/javascript"
    src="%(portal_url)s/++resource++ptg.galleriffic/jquery.galleriffic.js"></script>
<script type="text/javascript"
    src="%(portal_url)s/++resource++ptg.galleriffic/jquery.opacityrollover.js"></script>
<script type="text/javascript">
    document.write('<style>.noscript { display: none; }</style>');

(function($){
$(document).ready(function() {

    // Initially set opacity on thumbs and add
    // additional styling for hover effect on thumbs
    var onMouseOutOpacity = 0.67;
    var captionOpacity = 0.7;
    $('#thumbs ul.thumbs li').opacityrollover({
        mouseOutOpacity:   onMouseOutOpacity,
        mouseOverOpacity:  1.0,
        fadeSpeed:         'fast',
        exemptionSelector: '.selected'
    });
    // Initialize Advanced Galleriffic Gallery
    var gallery = $('#thumbs').galleriffic({
        delay:                     %(delay)i,
        numThumbs:                 %(batch_size)i,
        preloadAhead:              10,
        enableTopPager:            %(toppager)s,
        enableBottomPager:         %(bottompager)s,
        maxPagesToShow:            7,
        imageContainerSel:         '#slideshow',
        controlsContainerSel:      '#controls',
        captionContainerSel:       '#caption',
        loadingContainerSel:       '#loading',
        renderSSControls:          %(sscontrols)s,
        renderNavControls:         %(navcontrols)s,
        playLinkText:              'Play Slideshow',
        pauseLinkText:             'Pause Slideshow',
        prevLinkText:              '&lsaquo; Previous Photo',
        nextLinkText:              'Next Photo &rsaquo;',
        nextPageLinkText:          'Next &rsaquo;',
        prevPageLinkText:          '&lsaquo; Prev',
        enableHistory:             true,
        autoStart:                 %(timed)s,
        syncTransitions:           true,
        defaultTransitionDuration: %(duration)i,
        onSlideChange:             function(prevIndex, nextIndex) {
            this.find('ul.thumbs').children()
                .eq(prevIndex).fadeTo('fast', onMouseOutOpacity).end()
                .eq(nextIndex).fadeTo('fast', 1.0);
        },
        onTransitionOut:           function(slide, caption, isSync, callback) {
            slide.fadeTo(this.getDefaultTransitionDuration(isSync), 0.0,
                         callback);
            caption.fadeTo(this.getDefaultTransitionDuration(isSync), 0.0);
        },
        onTransitionIn:            function(slide, caption, isSync) {
            var duration = this.getDefaultTransitionDuration(isSync);
            slide.fadeTo(duration, 1.0);
            var slideImage = slide.find('img');
            caption.width(slideImage.width())
                .css({
                    'bottom' : Math.floor((slide.height() -
                                           slideImage.outerHeight()) / 2),
                    'left' : Math.floor((slide.width() -
                                         slideImage.width()) / 2) +
                                slideImage.outerWidth() - slideImage.width()
                })
                .fadeTo(duration, captionOpacity);
        },
        onPageTransitionOut:       function(callback) {
            this.fadeTo('fast', 0.0, callback);
        },
        onPageTransitionIn:        function() {
            this.fadeTo('fast', 1.0);
        },
        onImageAdded:              function(imageData, $li) {
            $li.opacityrollover({
                mouseOutOpacity:   onMouseOutOpacity,
                mouseOverOpacity:  1.0,
                fadeSpeed:         'fast',
                exemptionSelector: '.selected'
            });
        }
    });
});
})(jQuery);

</script>
""" % {
    'portal_url': self.portal_url,
    'timed': jsbool(self.settings.timed),
    'delay': self.settings.delay,
    'duration': self.settings.duration,
    'batch_size': self.settings.batch_size,
    'toppager' :   jsbool(self.settings.gallerific_toppager),
    'bottompager': jsbool(self.settings.gallerific_bottompager),
    'sscontrols':   jsbool(self.settings.gallerific_sscontrols),
    'navcontrols':  jsbool(self.settings.gallerific_navcontrols), 
}
GallerifficSettings = createSettingsFactory(GallerifficDisplayType.schema)