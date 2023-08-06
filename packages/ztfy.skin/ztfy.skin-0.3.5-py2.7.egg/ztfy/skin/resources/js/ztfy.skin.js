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
	 * Array prototype extensions
	 */
	if (!Array.prototype.indexOf) {
		Array.prototype.indexOf = function(elt /*, from*/) {
			var len = this.length;

			var from = Number(arguments[1]) || 0;
			from = (from < 0) ? Math.ceil(from) : Math.floor(from);
			if (from < 0)
				from += len;

			for (; from < len; from++) {
				if (from in this &&
					this[from] === elt)
					return from;
			}
			return -1;
		};
	}

	/**
	 * JQuery 'econtains' expression
	 * Case insensitive contains expression
	 */
	$.expr[":"].econtains = function(obj, index, meta, stack) {
		return (obj.textContent || obj.innerText || $(obj).text() || "").toLowerCase() == meta[3].toLowerCase();
	}

	/**
	 * JQuery 'withtext' expression
	 * Case sensitive exact search expression
	 */
	$.expr[":"].withtext = function(obj, index, meta, stack) {
		return (obj.textContent || obj.innerText || $(obj).text() || "") == meta[3];
	}

	/**
	 * UTF-8 encoding class
	 * Mainly used by IE...
	 */
	$.UTF8 = {

		// public method for url encoding
		encode : function (string) {
			string = string.replace(/\r\n/g,"\n");
			var utftext = "";
	 
			for (var n = 0; n < string.length; n++) {
	 
				var c = string.charCodeAt(n);
	 
				if (c < 128) {
					utftext += String.fromCharCode(c);
				}
				else if((c > 127) && (c < 2048)) {
					utftext += String.fromCharCode((c >> 6) | 192);
					utftext += String.fromCharCode((c & 63) | 128);
				}
				else {
					utftext += String.fromCharCode((c >> 12) | 224);
					utftext += String.fromCharCode(((c >> 6) & 63) | 128);
					utftext += String.fromCharCode((c & 63) | 128);
				}
			}
			return utftext;
		},

		// public method for url decoding
		decode : function (utftext) {
			var string = "";
			var i = 0;
			var c = c1 = c2 = 0;
	 
			while ( i < utftext.length ) {
	 
				c = utftext.charCodeAt(i);
	 
				if (c < 128) {
					string += String.fromCharCode(c);
					i++;
				}
				else if((c > 191) && (c < 224)) {
					c2 = utftext.charCodeAt(i+1);
					string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
					i += 2;
				}
				else {
					c2 = utftext.charCodeAt(i+1);
					c3 = utftext.charCodeAt(i+2);
					string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
					i += 3;
				}
			}
			return string;
		}
	} /** $.UTF8 */

	/**
	 * ZTFY.skin extensions to JQuery
	 */
	if (typeof($.ZTFY) == 'undefined') {
		$.ZTFY = {};
	}

	/**
	 * Extract parameter value from given query string
	 */
	$.ZTFY.getQueryVar = function(src, varName) {
		// Check src
		if (src.indexOf('?') < 0)
			return false;
		if (!src.endsWith('&'))
			src += '&';
		// Dynamic replacement RegExp
		var regex = new RegExp('.*?[&\\?]' + varName + '=(.*?)&.*');
		// Apply RegExp to the query string
		var val = src.replace(regex, "$1");
		// If the string is the same, we didn't find a match - return false
		return val == src ? false : val;
	},

	/**
	 * Color conversion function
	 */
	$.ZTFY.rgb2hex = function(color) {
		return "#" + $.map(color.match(/\b(\d+)\b/g), function(digit) {
			return ('0' + parseInt(digit).toString(16)).slice(-2)
		}).join('');
	}

	/**
	 * Generic ZTFY functions
	 */
	$.ZTFY.skin = {

		/**
		 * Events management
		 */
		stopEvent: function(event) {
			if (!event) {
				var event = window.event;
			}
			if (event) {
				if (event.stopPropagation) {
					event.stopPropagation();
					event.preventDefault();
				} else {
					event.cancelBubble = true;
					event.returnValue = false;
				}
			}
		},

		getCSS: function(resource, id, callback) {
			var head = $('HEAD');
			var check = $('style[ztfy_id='+id+']', head);
			if (check.length == 0) {
				$.get(resource, function(data) {
					var style = $('<style></style>').attr('type','text/css')
													.attr('ztfy_id', id)
													.text(data);
					head.prepend(style);
					if (callback) {
						callback();
					}
				});
			}
		},

		switcher: function(div) {
			$(div).toggle();
		}

	}

	/**
	 * AJAX management
	 */
	$.ZTFY.ajax = {

		check: function(checker, source, callback) {
			if (typeof(checker) == 'undefined') {
				$.getScript(source, callback)
			} else {
				callback();
			}
		},

		getAddr: function(addr) {
			var href = addr || window.location.href;
			var target = href.replace(/\+\+skin\+\+\w+\//, '');
			return target.substr(0, target.lastIndexOf("/")+1);
		},

		post: function(url, data, onsuccess, onerror, datatype) {
			if (url.startsWith('http://')) {
				var addr = url;
			} else {
				var addr = $.ZTFY.ajax.getAddr() + url;
			}
			var options = {
				url: addr,
				type: 'post',
				cache: false,
				data: $.param(data, true),  /* use traditional JQuery params decoding */
				dataType: datatype || 'json',
				success: onsuccess,
				error: onerror || $.ZTFY.ajax.error
			};
			$.ajax(options);
		},

		submit: function(form, url, data, onsuccess, onerror, datatype) {
			$.ZTFY.ajax.check($.progressBar, '/--static--/ztfy.jqueryui/js/jquery-progressbar.min.js', function() {
				var uuid = $.progressBar.submit(form);
				if (url.startsWith(window.location.protocol)) {
					var addr = url;
				} else {
					var addr = $.ZTFY.ajax.getAddr() + url;
				}
				if (uuid && (addr.indexOf('X-Progress-ID') < 0)) {
					addr += "?X-Progress-ID=" + uuid;
				}
				var options = {
					url: addr,
					type: 'post',
					iframe: true,
					data: data,
					dataType: datatype || 'json',
					success: onsuccess,
					error: onerror || $.ZTFY.ajax.error
				};
				$(form).ajaxSubmit(options);
			});
		},

		error: function(request, status, error) {
			$.ZTFY.ajax.check(jAlert, '/--static--/ztfy.jqueryui/js/jquery-alerts.min.js', function() {
				jAlert(status + ':\n\n' + error, $.ZTFY.I18n.ERROR_OCCURED, null);
			});
		}

	}  /** $.ZTFY.ajax */

	/**
	 * JSON management
	 */
	$.ZTFY.json = {

		getAddr: function(addr) {
			return $.ZTFY.ajax.getAddr(addr);
		},

		getQuery: function(method, query, callback) {
			var result;
			var async = typeof(callback) == 'undefined' ? false : true;
			var options = {
				url: $.ZTFY.json.getAddr(),
				type: 'POST',
				method: method,
				async: async,
				params: {
					query: query
				},
				complete: callback,
				success: function(data, status) {
					result = data.result
				},
				error: function(request, status, error) {
					jAlert(request.responseText, "Error !", window.location.reload);
				}
			}
			$.jsonRpc(options);
			return result
		},

		post: function(method, params, onsuccess, onerror, base) {
			var addr = $.ZTFY.json.getAddr();
			if (base) {
				addr += '/' + base;
			}
			var options = {
				url: addr,
				type: 'post',
				cache: false,
				method: method,
				params: params,
				success: onsuccess,
				error: onerror
			};
			$.jsonRpc(options);
		}

	}  /** $.ZTFY.json */

	/**
	 * Loading management
	 */
	$.ZTFY.loader = {

		div: null,

		start: function(parent) {
			parent.empty();
			var $div = $('<div class="loader"></div>').appendTo(parent);
			var $img = $('<img class="loading" src="/--static--/ztfy.skin/img/loading.gif" />').appendTo($div);
			$.ZTFY.loader.div = $div;
		},

		stop: function() {
			if ($.ZTFY.loader.div != null) {
				$.ZTFY.loader.div.replaceWith('');
				$.ZTFY.loader.div = null;
			}
		}

	}  /** $.ZTFY.loader */

	/**
	 * Dialogs management
	 */
	$.ZTFY.dialog = {

		switchGroup: function(source, target) {
			var target = $('DIV[id=group_' + target + ']');
			if ($(source).attr('src').endsWith('pl.png')) {
				target.show();
				$(source).attr('src', '/--static--/ztfy.skin/img/mi.png');
			} else {
				target.hide();
				$(source).attr('src', '/--static--/ztfy.skin/img/pl.png');
			}
			$(source).parents('FIELDSET:first').toggleClass('switched');
		},

		options: {
			expose: {
				maskId: 'mask',
				color: '#444',
				opacity: 0.6,
				zIndex: 1000
			},
			top: '5%',
			api: true,
			oneInstance: false,
			closeOnClick: false,
			onBeforeLoad: function() {
				var wrapper = this.getOverlay();
				$.ZTFY.loader.start(wrapper);
				wrapper.load($.ZTFY.dialog.dialogs[$.ZTFY.dialog.getCount()-1].src);
				if ($.browser.msie && ($.browser.version < '7')) {
					$('select').css('visibility', 'hidden');
				}
			},
			onClose: function() {
				$.ZTFY.dialog.onClose();
				if ($.browser.msie && ($.browser.version < '7')) {
					$('select').css('visibility', 'hidden');
				}
			}
		},

		dialogs: [],

		getCount: function() {
			return $.ZTFY.dialog.dialogs.length;
		},

		getCurrent: function() {
			var count = $.ZTFY.dialog.getCount();
			return $('#dialog_' + count);
		},

		open: function(src, event) {
			/* Stop event ! */
			var src = src.replace(/ /g, '%20');
			var event = typeof(window.event) != 'undefined' ? window.event : event;
			$.ZTFY.skin.stopEvent(event);
			/* Init dialogs array */
			if (!$.ZTFY.dialog.dialogs) {
				$.ZTFY.dialog.dialogs = new Array();
			}
			var index = $.ZTFY.dialog.getCount() + 1;
			var id = 'dialog_' + index;
			var options = {}
			var expose_options = {
				maskId: 'mask_' + id,
				color: '#444',
				opacity: 0.6,
				zIndex: $.ZTFY.dialog.options.expose.zIndex + index
			};
			$.extend(options, $.ZTFY.dialog.options, { expose: expose_options });
			$.ZTFY.dialog.dialogs.push({
				src: src,
				body: $('<div class="overlay"></div>').attr('id', id)
													  .css('z-index', expose_options.zIndex+1)
													  .appendTo($('body'))
			});
			$('#' + id).empty()
					   .overlay(options)
					   .load();
		},

		close: function() {
			$('#dialog_' + $.ZTFY.dialog.getCount()).overlay().close();
		},

		onClose: function() {
			if (typeof(tinyMCE) != 'undefined') {
				if (tinyMCE.activeEditor) {
					tinyMCE.execCommand('mceRemoveControl', false, tinyMCE.activeEditor.id);
				}
			}
			var count = $.ZTFY.dialog.getCount();
			var id = 'dialog_' + count;
			$('#' + id).remove();
			$('#mask_' + id).remove();
			$.ZTFY.dialog.dialogs.pop();
		}

	}  /** $.ZTFY.dialog */

	/**
	 * Forms managements
	 */
	$.ZTFY.form = {

		check: function(callback) {
			$.ZTFY.ajax.check($.fn.ajaxSubmit, '/--static--/ztfy.jqueryui/js/jquery-form.min.js', callback);
		},

		hideStatus: function() {
			$('DIV.form DIV.status').animate({
				'opacity': 0,
				'height': 0,
				'margin-top': 0,
				'margin-bottom': 0,
				'padding-top': 0,
				'padding-bottom': 0
			}, 2000, function() {
				$(this).remove();
			});
		},

		reset: function(form) {
			form.reset();
			$('input:first', form).focus();
		},

		add: function(form, parent, callback, data) {
			$.ZTFY.form.check(function() {
				if (typeof(tinyMCE) != 'undefined') {
					tinyMCE.triggerSave();
				}
				if (parent) {
					data.parent = parent;
				}
				var action = $(form).attr('action').replace(/\?X-Progress-ID=.*/, '');
				$($.ZTFY.form).data('add_action', action);
				var dataType = $.browser.msie ? 'text' : 'json';
				$.ZTFY.ajax.submit(form, action + '/@@ajax/ajaxCreate', data || {}, callback || $.ZTFY.form._addCallback, null, dataType);
			});
			return false;
		},

		_addCallback: function(result, status) {
			if (status == 'success') {
				if ($.browser.msie) {
					result = $.parseJSON($(result).text());
				}
				var output = result.output;
				if (output == 'ERRORS') {
					var dialog = $.ZTFY.dialog.getCurrent();
					$('DIV.status', dialog).remove();
					$('DIV.error', dialog).remove();
					var status = $('<div></div>').addClass('status');
					$('<div></div>').addClass('summary')
									.text(result.errors.status)
									.appendTo(status);
					var errors = $('<ul></ul>').appendTo(status);
					if (result.errors.errors) {
						for (var i=0; i < result.errors.errors.length; i++) {
							var error = result.errors.errors[i];
							if (error.widget) {
								$('<li></li>').text(error.widget + ' : ' + error.message)
											  .appendTo(errors);
								var widget = $('[id=' + error.id + ']', dialog).parents('DIV.widget');
								var row = $(widget).parents('DIV.row');
								$('<div></div>').addClass('error')
												.append($('<div></div>').addClass('error')
														 				.text(error.message))
												.insertBefore(widget);
							} else {
								$('<li></li>').text(error.message)
											  .appendTo(errors);
							}
						}
					}
					$('FORM', dialog).before(status);
				} else if (output == 'OK') {
					$.ZTFY.dialog.close();
					$('DIV.status').remove();
					$('DIV.required-info').after('<div class="status"><div class="summary">' + $.ZTFY.I18n.DATA_UPDATED + '</div></div>');
				} else if (output == 'NONE') {
					$.ZTFY.dialog.close();
					$('DIV.status').remove();
					$('DIV.required-info').after('<div class="status"><div class="summary">' + $.ZTFY.I18n.NO_UPDATE + '</div></div>');
				} else if (output == 'PASS') {
					$.ZTFY.dialog.close();
					$('DIV.status').remove();
				} else if (output == 'RELOAD') {
					window.location.href = window.location.href;
				} else if (output == 'REDIRECT') {
					window.location.href = result.target;
				} else if (output == 'CALLBACK') {
					eval(result.callback);
				} else if (output && output.startsWith('<!-- OK -->')) {
					$.ZTFY.dialog.close();
					$('DIV.form').replaceWith(output);
				} else {
					var dialog = $.ZTFY.dialog.getCurrent();
					$('DIV.dialog', dialog).replaceWith(output);
					$('FORM', dialog).attr('action', $($.ZTFY.form).data('add_action'));
					$('#form-buttons-add', dialog).bind('click', function(event) {
						$.ZTFY.form.add(this.form, result.parent);
					});
					$('#form-buttons-cancel', dialog).bind('click', function(event) {
						$.ZTFY.dialog.close();
					});
					$('#tabforms UL.tabs', dialog).tabs($(dialog).selector + ' DIV.panes > DIV');
				}
				if (output != 'ERRORS') {
					setTimeout('$.ZTFY.form.hideStatus();', 2000);
				}
			}
		},

		edit: function(form, base, callback, data) {
			$.ZTFY.form.check(function() {
				if (typeof(tinyMCE) != 'undefined') {
					tinyMCE.triggerSave();
				}
				var action = $(form).attr('action').replace(/\?X-Progress-ID=.*/, '');
				$($.ZTFY.form).data('edit_action', action);
				var dataType = $.browser.msie ? 'text' : 'json';
				$.ZTFY.ajax.submit(form, action + '/@@ajax/ajaxEdit', data || {}, callback || $.ZTFY.form._editCallback, null, dataType);
			});
			return false;
		},

		_editCallback: function(result, status, response) {
			if (status == 'success') {
				if ($.browser.msie) {
					result = $.parseJSON($(result).text());
				}
				var output = result.output;
				if (output == 'ERRORS') {
					var dialog = $.ZTFY.dialog.getCurrent();
					$('DIV.status', dialog).remove();
					$('DIV.error', dialog).remove();
					var status = $('<div></div>').addClass('status');
					$('<div></div>').addClass('summary')
									.text(result.errors.status)
									.appendTo(status);
					var errors = $('<ul></ul>').appendTo(status);
					if (result.errors.errors) {
						for (var i=0; i < result.errors.errors.length; i++) {
							var error = result.errors.errors[i];
							if (error.widget) {
								$('<li></li>').text(error.widget + ' : ' + error.message)
											  .appendTo(errors);
								var widget = $('[id=' + error.id + ']', dialog).parents('DIV.widget');
								var row = $(widget).parents('DIV.row');
								$('<div></div>').addClass('error')
												.append($('<div></div>').addClass('error')
														 				.text(error.message))
												.insertBefore(widget);
							} else {
								$('<li></li>').text(error.message)
											  .appendTo(errors);
							}
						}
					}
					$('FORM', dialog).before(status);
				} else if (output == 'OK') {
					$.ZTFY.dialog.close();
					$('DIV.status').remove();
					$('DIV.required-info').after('<div class="status"><div class="summary">' + $.ZTFY.I18n.DATA_UPDATED + '</div></div>');
				} else if (output == 'NONE') {
					$.ZTFY.dialog.close();
					$('DIV.status').remove();
					$('DIV.required-info').after('<div class="status"><div class="summary">' + $.ZTFY.I18n.NO_UPDATE + '</div></div>');
				} else if (output == 'PASS') {
					$.ZTFY.dialog.close();
					$('DIV.status').remove();
				} else if (output == 'RELOAD') {
					window.location.href = window.location.href;
				} else if (output == 'REDIRECT') {
					window.location.href = result.target;
				} else if (output == 'CALLBACK') {
					eval(result.callback);
				} else  if (output && output.startsWith('<!-- OK -->')) {
					$.ZTFY.dialog.close();
					$('DIV.form').replaceWith(output);
				} else {
					var dialog = $.ZTFY.dialog.getCurrent();
					$('DIV.dialog', dialog).replaceWith(output);
					var form = $('FORM', dialog);
					form.attr('action', $($.ZTFY.form).data('edit_action'));
					$('#'+form.attr('id')+'-buttons-dialog_submit', dialog).bind('click', function(event) {
						$.ZTFY.form.edit(this.form);
					});
					$('#'+form.attr('id')+'form-buttons-dialog_cancel', dialog).bind('click', function(event) {
						$.ZTFY.dialog.close();
					});
					$('#tabforms UL.tabs', dialog).tabs($(dialog).selector + ' DIV.panes > DIV');
				}
				if (output != 'ERRORS') {
					setTimeout('$.ZTFY.form.hideStatus();', 2000);
				}
			}
		},

		remove: function(oid, source, callback) {
			jConfirm($.ZTFY.I18n.CONFIRM_REMOVE, $.ZTFY.I18n.CONFIRM, function(confirmed) {
				if (confirmed) {
					var data = {
						id: oid
					}
					$.ZTFY.form.ajax_source = source;
					$.ZTFY.ajax.post(window.location.href + '/@@ajax/ajaxRemove', data, callback || $.ZTFY.form._removeCallback, null, 'text');
				}
			});
		},

		_removeCallback: function(result, status) {
			if ((status == 'success') && (result == 'OK')) {
				$($.ZTFY.form.ajax_source).parents('TR').remove();
			}
		},

		update: function(form, callback) {
			$.ZTFY.form.check(function() {
				if (typeof(tinyMCE) != 'undefined') {
					tinyMCE.triggerSave();
				}
				var data = $(form).formToArray(true);
				$.ZTFY.ajax.post($(form).attr('action') + '/@@ajax/ajaxUpdate', data, callback || $.ZTFY.form._updateCallback, null, 'text');
			});
			return false;
		},

		_updateCallback: function(result, status) {
			if ((status == 'success') && (result == 'OK')) {
				$('DIV.status').remove();
				$('LEGEND').after('<div class="status"><div class="summary">' + $.ZTFY.I18n.DATA_UPDATED + '</div></div>');
			}
		}

	}  /** $.ZTFY.form */

	/**
	 * Container management
	 */
	$.ZTFY.container = {

		remove: function(oid, source, addr) {
			var options = {
				_source: source,
				url: $.ZTFY.json.getAddr(addr),
				type: 'POST',
				method: 'remove',
				params: {
					id: oid
				},
				success: function(data, status) {
					$(this._source).parents('BODY').css('cursor', 'default');
					$(this._source).parents('TR').remove();
				},
				error: function(request, status, error) {
					jAlert(request.responseText, $.ZTFY.I18n.ERROR_OCCURED, window.location.reload);
				}
			}
			jConfirm($.ZTFY.I18n.CONFIRM_REMOVE, $.ZTFY.I18n.CONFIRM, function(confirmed) {
				if (confirmed) {
					$(source).parents('BODY').css('cursor', 'wait');
					$.jsonRpc(options);
				}
			});
		}

	}  /** $.ZTFY.container */

	/**
	 * Sortables management
	 */
	$.ZTFY.sortable = {

		options: {
			handle: 'IMG.handler',
			axis: 'y',
			containment: 'parent',
			placeholder: 'sorting-holder',
			stop: function(event, ui) {
				var ids = new Array();
				$('TABLE.orderable TD.id').each(function (i) {
					ids[ids.length] = $(this).text();
				});
				var data = {
					ids: ids
				}
				$.ZTFY.ajax.post(window.location.href + '/@@ajax/ajaxUpdateOrder', data, null, function(request, status, error) {
					jAlert(request.responseText, $.ZTFY.I18n.ERROR_OCCURED, window.location.reload);
				});
			}
		}

	}  /** $.ZTFY.sortable */

	/**
	 * Treeviews management
	 */
	$.ZTFY.treeview = {

		changeParent: function(event,ui) {
			var $dragged = $(ui.draggable.parents('TR'));
			if ($dragged.appendBranchTo(this)) {
				var source = $dragged.attr('id').substr('node-'.length);
				var target = $(this).attr('id').substr('node-'.length);
				var options = {
					url: $.ZTFY.json.getAddr(),
					type: 'POST',
					method: 'changeParent',
					params: {
						source: parseInt(source),
						target: parseInt(target)
					},
					error: function(request, status, error) {
						jAlert(request.responseText, $.ZTFY.I18n.ERROR_OCCURED, window.location.reload);
					}
				}
				$.jsonRpc(options);
			}
		}

	}  /** $.ZTFY.treeview */

	var lang = $('HTML').attr('lang') || $('HTML').attr('xml:lang') || 'en';
	$.getScript('/--static--/ztfy.skin/js/i18n/' + lang + '.js');

	/**
	 * Override Chromium opacity bug on Linux !
	 */
	if ($.browser.safari) {
		$.support.opacity = true;
	}

	/**
	 * Automatically handle images properties download links
	 */
	if ($.fn.fancybox) {
		$(document).ready(function() {
			$('DIV.download-link IMG').parents('A').fancybox({
				type: 'image',
				titleShow: false,
				hideOnContentClick: true
			});
		});
	}

})(jQuery);