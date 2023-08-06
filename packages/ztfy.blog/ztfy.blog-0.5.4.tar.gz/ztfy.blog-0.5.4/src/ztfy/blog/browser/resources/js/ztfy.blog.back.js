(function($) {

	if (typeof($.ZBlog) == 'undefined') {
		$.ZBlog = {};
	}

	/**
	 * ZBlog tree view management
	 */
	$.ZBlog.treeview = {

		init: function(parent) {
			$('TABLE.treeview TR.section TD.title, TABLE.treeview TR.topic TD.title', parent).draggable({
				helper: 'clone',
				opacity: .75,
				revert: 'invalid',
				revertDuration: 300,
				scroll: true,
				containment: 'TABLE.treeview'
			});
			$('TABLE.treeview TR.site', parent).droppable({
				accept: 'TR.section TD.title',
				hoverClass: 'accept',
				over: function(event,ui) {
					if(this.id != $(ui.draggable.parents("TR")[0]).id && !$(this).is(".expanded")) {
						$(this).expand();
					}
				},
				drop: $.ZTFY.treeview.changeParent
			});
			$('TABLE.treeview TR.section', parent).droppable({
				accept: 'TR.section TD.title, TR.topic TD.title',
				hoverClass: 'accept',
				over: function(event,ui) {
					if(this.id != $(ui.draggable.parents("TR")[0]).id && !$(this).is(".expanded")) {
						$(this).expand();
					}
				},
				drop: $.ZTFY.treeview.changeParent
			});
		}

	}  /** $.ZBlog.treeview */

	/**
	 * Internal references management
	 */
	$.ZBlog.reference = {

		activate: function(selector) {
			$('INPUT[name='+selector+']').attr('readonly','')
										 .val('')
										 .focus();
			$('INPUT[name='+selector+']').prev().val('');
		},

		keyPressed: function(event) {
			if (event.which == 13) {
				$.ZBlog.reference.search(this);
				return false;
			}
		},

		search: function(query) {
			var result;
			var options = {
				url: $.ZTFY.ajax.getAddr(),
				type: 'POST',
				method: 'search',
				async: false,
				params: {
					query: query
				},
				success: function(data, status) {
					result = data.result;
				},
				error: function(request, status, error) {
					jAlert(request.responseText, "Error !", window.location.reload);
				}
			}
			$.jsonRpc(options);
			return result;
		},

		select: function(oid, title) {
			var source = $.ZBlog.reference.source;
			$(source).prev().val(oid);
			$(source).val(title + ' (OID: ' + oid + ')')
					 .attr('readonly', 'readonly');
			$('#selector').overlay().close();
			$('#selector').remove();
			return false;
		}

	}  /** $.ZBlog.reference */

	/**
	 * Topics management
	 */
	$.ZBlog.topic = {

		remove: function(form) {
			$.ZTFY.ajax.post($(form).attr('action') + '/@@ajax/ajaxDelete', {}, $.ZBlog.topic.removeCallback, null, 'json');
			return false;
		},

		removeCallback: function(result, status) {
			if (status == 'success') {
				window.location = result.url;
			}
		}

	}  /** $.ZBlog.topic */

})(jQuery);