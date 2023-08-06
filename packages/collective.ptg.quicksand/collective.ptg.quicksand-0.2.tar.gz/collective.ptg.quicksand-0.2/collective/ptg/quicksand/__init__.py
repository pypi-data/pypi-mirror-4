from collective.plonetruegallery.utils import createSettingsFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from collective.plonetruegallery.browser.views.display import BaseDisplayType
from collective.plonetruegallery.interfaces import IBaseSettings
from zope import schema
from zope.i18nmessageid import MessageFactory
from sets import Set


from collective.plonetruegallery.utils import getGalleryAdapter


_ = MessageFactory('collective.ptg.quicksand')

class IQuicksandDisplaySettings(IBaseSettings):
    quicksand_boxwidth = schema.Int(
        title=_(u"label_quicksand_imagewidth",
            default=u"Width of (each) image"),
        default=400,
        min=50)
    quicksand_boxheight = schema.Int(
        title=_(u"label_quicksand_imageheight",
            default=u"Height of (each) image"),
        default=260,
        min=50)
    quicksand_use_icons = schema.Bool(
        title=_(u"label_quicksand_use_icons",
            default=u"Use Thumbnail size instead of Size"),
        default=False)
    quicksand_showtitle = schema.Bool(
        title=_(u"label_quicksand_showtitle",
            default=u"Show the title?"),
        default=True)
    quicksand_showdescription = schema.Bool(
        title=_(u"label_quicksand_showdescription",
            default=u"Show the the description?"),
        default=True)
    quicksand_linkable = schema.Bool(
        title=_(u"label_quicksand_linkable",
            default=u"Should the user go to the image he clicks on?"),
        default=True)
    quicksand_easing = schema.Choice(
        title=_(u"label_quicksand_easing",
                default=u"Which easing on the transitions"),
        default="easeInOutQuad",
        vocabulary=SimpleVocabulary([
            SimpleTerm("swing", "swing",
                _(u"label_quicksand_easing_swing",
                    default=u"swing")),
            SimpleTerm("easeInQuad", "easeInQuad",
                _(u"label_quicksand_easing_easeInQuad",
                    default=u"easeInQuad")),
            SimpleTerm("easeOutQuad", "easeOutQuad",
                _(u"label_quicksand_easing_easeOutQuad",
                    default=u"easeOutQuad")),
            SimpleTerm("easeInOutQuad", "easeInOutQuad",
                _(u"label_quicksand_easing_easeInOutQuad",
                    default=u"easeInOutQuad")),
            SimpleTerm("easeInCubic", "easeInCubic",
                _(u"label_quicksand_easing_easeInCubic",
                    default=u"easeInCubic")),
            SimpleTerm("easeOutCubic", "easeOutCubic",
                _(u"label_quicksand_easing_easeOutCubic",
                    default=u"easeOutCubic")),
            SimpleTerm("easeInOutCubic", "easeInOutCubic",
                _(u"label_quicksand_easing_easeInOutCubic",
                    default=u"easeInOutCubic")),
            SimpleTerm("easeInQuart", "easeInQuart",
                _(u"label_quicksand_easing_easeInQuart",
                    default=u"easeInQuart")),
            SimpleTerm("easeOutQuart", "easeOutQuart",
                _(u"label_quicksand_easing_easeOutQuart",
                    default=u"easeOutQuart")),
            SimpleTerm("easeInOutQuart", "easeInOutQuart",
                _(u"label_quicksand_easing_easeInOutQuart",
                    default=u"easeInOutQuart")),
            SimpleTerm("easeInSine", "easeInSine",
                _(u"label_quicksand_easing_easeInSine",
                    default=u"easeInSine")),
            SimpleTerm("easeInOutSine", "easeInOutSine",
                _(u"label_quicksand_easing_easeInOutSine",
                    default=u"easeInOutSine")),
            SimpleTerm("easeInExpo", "easeInExpo",
                _(u"label_quicksand_easing_easeInExpo",
                    default=u"easeInExpo")),
            SimpleTerm("easeInCirc", "easeInCirc",
                _(u"label_quicksand_easing_easeInCirc",
                    default=u"easeInCirc")),
            SimpleTerm("easeOutCirc", "easeOutCirc",
                _(u"label_quicksand_easing_easeOutCirc",
                    default=u"easeOutCirc")),
            SimpleTerm("easeInOutCirc", "easeInOutCirc",
                _(u"label_quicksand_easing_easeInOutCirc",
                    default=u"easeInOutCirc")),
            SimpleTerm("easeInElastic", "easeInElastic",
                _(u"label_quicksand_easing_easeInElastic",
                    default=u"easeInElastic")),
            SimpleTerm("easeOutElastic", "easeOutElastic",
                _(u"label_quicksand_easing_easeOutElastic",
                    default=u"easeOutElastic")),
            SimpleTerm("easeInBack", "easeInBack",
                _(u"label_quicksand_easing_easeInBack",
                    default=u"easeInBack")),
            SimpleTerm("easeOutBack", "easeOutBack",
                _(u"label_quicksand_easing_easeOutBack",
                    default=u"easeOutBack")),
            SimpleTerm("easeInOutBack", "easeInOutBack",
                _(u"label_quicksand_easing_easeInOutBack",
                    default=u"easeInOutBack")),
            SimpleTerm("easeInBounce", "easeInBounce",
                _(u"label_quicksand_easing_easeInBounce",
                    default=u"easeInBounce")),
            SimpleTerm("easeOutBounce", "easeOutBounce",
                _(u"label_quicksand_easing_easeOutBounce",
                    default=u"easeOutBounce")),                     
	        SimpleTerm("easeInOutBounce", "easeInOutBouncee",
                _(u"label_quicksand_easing_easeInOutBounce",
                    default=u"easeInOutBounce")
            )
        ]))
    quicksand_style = schema.Choice(
        title=_(u"label_quicksand_style",
                default=u"What stylesheet (css file) to use"),
        default="style.css",
        vocabulary=SimpleVocabulary([
            SimpleTerm("style.css", "style.css",
                _(u"label_quicksand_style_default",
                    default=u"Default")),
            SimpleTerm("boxstyle.css", "boxstyle.css",
                _(u"label_quicksand_boxstyle",
                    default=u"Box style")),
            SimpleTerm("no_style.css", "no_style.css",
                _(u"label_quicksand_style_no",
                    default=u"No style / css file")),
            SimpleTerm("custom_style", "custom_style",
                _(u"label_quicksand_style_custom",
                    default=u"Custom css file")
            )
        ]))

    quicksand_custom_style = schema.TextLine(
        title=_(u"label_custom_style",
            default=u"Name of Custom css file if you chose that above"),
        default=u"mycustomstyle.css")


class QuicksandDisplayType(BaseDisplayType):
    name = u"quicksand"
    schema = IQuicksandDisplaySettings
    description = _(u"label_quicksand_display_type",
        default=u"Quicksand")
    
    def all_keywords(self):
        #finding unique keywords
        #must be a faster way to do this
        objects = self.adapter.cooked_images
        uniques = ""
        for item in objects:
            uniques += " "
            uniques += (item['keywords'])
        tags = uniques.split()
        tags = set(tags)
        return sorted(tags)
        #Need to fix this for keywords containing spaces

    def javascript(self):
        return u"""
<script type="text/javascript"
src="%(portal_url)s/++resource++ptg.quicksand/jquery.quicksand.js">
</script>
<script type="text/javascript"
src="%(portal_url)s/++resource++ptg.quicksand/jquery.easing.1.3.js">
</script>
<script type="text/javascript">
  // Custom sorting plugin
  (function($) {
	$.fn.sorted = function(customOptions) {
		var options = {
			by: function(a) { return a.text(); }
		};
		$.extend(options, customOptions);
		$data = $(this);
		arr = $data.get();
		return $(arr);
	};
  });

  // DOMContentLoaded
  $(function() {
  
	// bind radiobuttons in the form
	var $filterType = $('#filter input[name="type"]');
	var $filterSort = '';
	
	// get the first collection
	var $quicksandbox = $('#quicksandbox');
	
	// clone quicksandbox to get a second collection
	var $data = $quicksandbox.clone();

	// attempt to call Quicksand on every form change
	$filterType.add($filterSort).change(function(e) {
		if ($($filterType+':checked').val() == 'all') {
			var $filteredData = $data.find('li');
		} else {
			var $filteredData = $data.find('.' + $($filterType+":checked").val());
		}
	
	  // no sorting
		var $sortedData = $filteredData; 

		
		// finally, call quicksand
		$quicksandbox.quicksand($sortedData, {
			duration: %(speed)i,
			easing: '%(easing)s'
		});
	});
  });
</script>
""" % {
    'speed': self.settings.duration,
    'portal_url': self.portal_url,
    'easing': self.settings.quicksand_easing,
}

    def css(self):
        relpath = '++resource++ptg.quicksand'
        style = '%s/%s/%s' % (self.portal_url, relpath,
            self.settings.quicksand_style)

        if self.settings.quicksand_style == 'custom_style':
            style = '%s/%s' % (self.portal_url,
                self.settings.quicksand_custom_style)

        return u"""
<style>
.image-grid li {
    width: %(boxwidth)ipx;
    height: %(boxheight)ipx;
}
</style>
<link rel="stylesheet" type="text/css" href="%(style)s"/>
""" % {
        'boxheight': self.settings.quicksand_boxheight,
        'boxwidth': self.settings.quicksand_boxwidth,
        'style': style
       }
QuicksandSettings = createSettingsFactory(QuicksandDisplayType.schema)
