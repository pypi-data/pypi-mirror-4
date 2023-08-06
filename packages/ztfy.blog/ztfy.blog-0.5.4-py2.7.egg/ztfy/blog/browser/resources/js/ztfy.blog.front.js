(function($) {

	if (typeof($.ZBlog) == 'undefined') {
		$.ZBlog = {};
	}

	/**
	 * Common actions
	 */
	$.ZBlog.actions = {

		showLoginForm: function(source) {
			var $inputs = $('SPAN.inputs', source);
			$inputs.parents('LI:first').addClass('selected');
			$inputs.show();
			$('INPUT', $inputs).get(0).focus();
		},

		login: function(form) {
			if (typeof(form) == 'undefined') {
				form = $('FORM[name="login_form"]');
			}
			$.ZTFY.form.check(function() {
				$.ZBlog.actions._login(form);
			});
			return false;
		},

		_login: function(form) {
			$.ZTFY.ajax.submit(form, $(form).attr('action') + '/@@ajax/login', {}, $.ZBlog.actions._loginCallback, $.ZBlog.actions._loginError, 'json');
		},

		_loginCallback: function(result, status) {
			if (status == 'success') {
				if (result == 'OK') {
					window.location.reload();
				} else {
					jAlert($.ZTFY.I18n.BAD_LOGIN_MESSAGE, $.ZTFY.I18n.BAD_LOGIN_TITLE, null);
				}
			}
		},

		_loginError: function(request, status) {
			jAlert(status, $.ZTFY.I18n.ERROR_OCCURED, null);
		},

		logout: function() {
			$.get(window.location.href + '/@@login.html/@@ajax/logout', $.ZBlog.actions._logoutCallback);
		},

		_logoutCallback: function(result, status) {
			window.location.reload();
		}

	}  /** $.ZBlog.actions */

	/**
	 * Codes samples handling
	 */
	$.ZBlog.code = {

		resizeFrame: function(frame) {
			$(frame).css('height', $('BODY', frame.contentDocument).height() + 20);
		}

	}  /** $.ZBlog.code */

})(jQuery);