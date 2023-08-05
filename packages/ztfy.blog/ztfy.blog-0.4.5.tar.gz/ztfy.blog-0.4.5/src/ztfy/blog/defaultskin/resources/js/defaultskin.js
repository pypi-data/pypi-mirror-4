(function($) {

	/**
	 * String prototype extensions
	 */
	String.prototype.startsWith = function(str) {
		var slen = this.length;
		var dlen = str.length;
		if (slen < dlen) {
			return false;
		}
		return (this.substr(0,dlen) == str);
	}

	String.prototype.endsWith = function(str) {
		var slen = this.length;
		var dlen = str.length;
		if (slen < dlen) {
			return false;
		}
		return (this.substr(slen-dlen) == str);
	}

	/**
	 * Override Chromium opacity bug on Linux !
	 */
	if ($.browser.safari) {
		$.support.opacity = true;
	}

	/**
	 * Automatically redirect 'external' links to blank page
	 */
	$(document).ready(function() {
		$('A[rel=external]').attr('target', '_blank');
	});

	/**
	 * Automatically handle images properties download links
	 */
	if ($.fn.fancybox) {
		$(document).ready(function() {
			$('IMG.illustration').parents('A.zoom').each(function() {
				$(this).fancybox({
					type: 'image',
					overlayOpacity: 0.7,
					title: $(this).attr('title'),
					titleShow: true,
					titlePosition: 'over',
					titleFormat: function(title, array, index, opts) {
						if (title && title.length) {
							return '<span id="fancybox-title-over"><strong>' + title + '</strong><br />' + $(array[index]).attr('description') + '</span>';
						} else {
							return null;
						}
					},
					transitionIn: 'elastic',
					transitionOut: 'elastic',
					hideOnContentClick: true,
					onComplete: function() {
						$("#fancybox-wrap").hover(function() {
							$("#fancybox-title").slideDown('slow');
						}, function() {
							$("#fancybox-title").slideUp('slow');
						});
					}
				});
			});
		});
	}

})(jQuery);