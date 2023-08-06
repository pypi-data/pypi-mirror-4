(function($) {

	var loading = null;
	var loadingFrame = 1;
	var loadingTimer = null;
	var background_url = null;

	if (typeof($.ZBlog) == 'undefined') {
		$.ZBlog = {};
	}
	if (typeof($.ZBlog.gallery) == 'undefined') {
		$.ZBlog.gallery = {};
	}

	$.ZBlog.gallery.skin = {

		animateLoading: function() {
			if (!loading.is(':visible')){
				clearInterval(loadingTimer);
				return;
			}
			loading.css('background-position-y', (loadingFrame * -40) + 'px');
			loadingFrame = (loadingFrame + 1) % 12;
		},

		loadBackground: function() {
			loading = $('#banner DIV');
			loadingTimer = setInterval('$.ZBlog.gallery.skin.animateLoading();', 66);
			$.getJSON('getBackgroundURL.json', function(data) {
				if (data != 'none') {
					$('#legend SPAN').animate({
						opacity: 0
					}, 1000);
					$.get(data.url, function(img) {
						$('#banner').animate({
							opacity: 0
						}, 1000, function() {
							$('#banner').css('background', 'transparent url('+data.url+') scroll no-repeat left top')
										.animate({
											opacity: 1
										}, 1000);
							$('#legend SPAN').text(data.title).animate({
								opacity: 1
							}, 1000);
						});
						loading.hide();
					});
				} else {
					loading.hide();
				}
				setTimeout($.ZBlog.gallery.skin.loadBackground, 10000);
			});
		}
	}

	/**
	 * Disable options menu !!
	 */
	$(document).bind('contextmenu', function() {
		return false;
	});

})(jQuery);