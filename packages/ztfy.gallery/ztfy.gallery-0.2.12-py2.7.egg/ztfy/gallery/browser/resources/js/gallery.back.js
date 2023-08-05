(function($) {

	$.ZBlog.gallery = {

		sort_options: {
			handle: 'DIV.image',
			containment: 'parent',
			placeholder: 'sorting-holder',
			stop: function(event, ui) {
				var ids = new Array();
				$('FIELDSET.gallery DIV.image').each(function (i) {
					ids[ids.length] = $(this).attr('id');
				});
				var data = {
					ids: ids
				}
				$.ZTFY.ajax.post(window.location.href + '/@@ajax/ajaxUpdateOrder', data, null, function(request, status, error) {
					jAlert(request.responseText, $.ZTFY.I18n.ERROR_OCCURED, window.location.reload);
				});
			}
		},

		remove: function(oid, source) {
			jConfirm($.ZTFY.I18n.CONFIRM_REMOVE, $.ZTFY.I18n.CONFIRM, function(confirmed) {
				if (confirmed) {
					var data = {
						id: oid
					}
					$.ZTFY.form.ajax_source = $('DIV[id='+source+']');
					$.ZTFY.ajax.post(window.location.href + '/@@ajax/ajaxRemove', data, $.ZBlog.gallery._removeCallback, null, 'text');
				}
			});
		},

		_removeCallback: function(result, status) {
			if ((status == 'success') && (result == 'OK')) {
				$($.ZTFY.form.ajax_source).parents('DIV.image_wrapper').remove();
			}
		},

		paypal_switch: function(name) {
			var href = window.location.href;
			var addr = href.substr(0, href.lastIndexOf('/'));
			var target = addr + '/++gallery++/' + name + '/++paypal++/@@switch.html';
			var link = $('A.paypal', $('DIV[id='+name+']').parents('DIV.image_wrapper'));
			$.ZTFY.form.ajax_source = name;
			if (link.hasClass('disabled')) {
				$.ZTFY.ajax.post(target, {}, $.ZBlog.gallery._paypalEnableCallback, function(request, status, error) {
					jAlert(request.responseText, $.ZTFY.I18n.ERROR_OCCURED, window.location.reload);
				}, 'json');
			} else {
				$.ZTFY.dialog.open(target);
			}
		},

		paypal_edit: function(form, base) {
			$.ZTFY.form.edit(form, base, $.ZBlog.gallery._editCallback);
		},

		_editCallback: function(result, status) {
			$.ZTFY.form._editCallback(result, status);
			if ((status == 'success') && (result.output == 'OK')) {
				var name = $.ZTFY.form.ajax_source;
				var link = $('A.paypal', $('DIV[id='+name+']').parents('DIV.image_wrapper'));
				if (result.enabled) {
					link.removeClass('disabled').addClass('enabled');
					$('IMG', link).attr('src', '/--static--/ztfy.gallery.back/img/paypal-enabled.png');
				} else {
					link.removeClass('enabled').addClass('disabled');
					$('IMG', link).attr('src', '/--static--/ztfy.gallery.back/img/paypal-disabled.png');
				}
			}
		},

		_paypalEnableCallback: function(result, status) {
			if ((status == 'success') && (result.output == 'OK')) {
				var name = $.ZTFY.form.ajax_source;
				var link = $('A.paypal', $('DIV[id='+name+']').parents('DIV.image_wrapper'));
				if (link.hasClass('disabled')) {
					link.removeClass('disabled').addClass('enabled');
					$('IMG', link).attr('src', '/--static--/ztfy.gallery.back/img/paypal-enabled.png');
				}
			}
		}
	}

})(jQuery);