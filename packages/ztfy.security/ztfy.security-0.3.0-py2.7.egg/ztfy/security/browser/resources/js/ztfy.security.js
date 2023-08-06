(function($) {

	if (typeof($.ZTFY) == 'undefined') {
		$.ZTFY = {}
	}

	$.ZTFY.security = {

		json: {

			getAddr: function() {
				var href = window.location.href;
				var target = href.replace(/\+\+skin\+\+\w+\//, '');
				return target.substr(0, target.lastIndexOf("/")+1);
			},

			post: function(method, params, onsuccess, onerror, base) {
				var addr = $.ZTFY.security.json.getAddr();
				if (base) {
					addr += '/' + base;
				}
				var options = {
					url: addr,
					type: 'POST',
					method: method,
					params: params,
					success: onsuccess,
					error: onerror
				};
				$.jsonRpc(options);
			}

		},  /** $.ZTFY.security.json */

		findPrincipals: function(query) {
			var result;
			var options = {
				url: $.ZTFY.security.json.getAddr(),
				type: 'POST',
				method: 'findPrincipals',
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
		}
	}

})(jQuery);