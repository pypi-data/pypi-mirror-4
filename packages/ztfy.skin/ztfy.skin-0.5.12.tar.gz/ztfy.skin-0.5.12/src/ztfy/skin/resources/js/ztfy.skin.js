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
	 * JQuery 'scrollbarWidth' function
	 * Get width of vertical scrollbar
	 */
	if ($.scrollbarWidth === undefined) {
		$.scrollbarWidth = function() {
			var parent,
				child,
				width;
			if (width === undefined) {
				parent = $('<div style="width:50px;height:50px;overflow:auto"><div/></div>').appendTo('body');
				child = parent.children();
				width = child.innerWidth() - child.height(99).innerWidth();
				parent.remove();
			}
			return width;
		}
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
	if ($.ZTFY === undefined) {
		$.ZTFY = {};
	}

	/**
	 * Get script using browser cache
	 */
	$.ZTFY.getScript = function(url, callback, use_cache) {
		var options = {
			dataType: 'script',
			url: url,
			success: callback,
			cache: use_cache === undefined ? true : use_cache
		};
		return $.ajax(options);
	}

	/**
	 * Get and execute a function given by name
	 * Small piece of code by Jason Bunting
	 */
	$.ZTFY.getFunctionByName = function(functionName, context) {
		var namespaces = functionName.split(".");
		var func = namespaces.pop();
		var context = (context === undefined || context === null) ? window : context;
		for (var i = 0; i < namespaces.length; i++) {
			context = context[namespaces[i]];
		}
		return context[func];
	}

	$.ZTFY.executeFunctionByName = function(functionName, context /*, args */) {
		var func = $.ZTFY.getFunctionByName(functionName, context);
		var args = Array.prototype.slice.call(arguments, 2);
		return func.apply(context, args);
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
	}

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
			var check = $('style[ztfy_id="'+id+'"]', head);
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
				$.ZTFY.getScript(source, callback);
			} else {
				callback();
			}
		},

		getAddr: function(addr) {
			var href = addr || $('HTML HEAD BASE').attr('href') || window.location.href;
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

		getQuery: function(query, method, callback, params) {
			var result;
			if ((callback === null) || (callback === '') || (callback === 'null'))
				callback = undefined;
			else if (typeof(callback) == 'string')
				callback = $.ZTFY.getFunctionByName(callback);
			var async = $.isFunction(callback);
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
			options.params = $.extend(options.params, params || {});
			$.jsonRpc(options);
			return result;
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
	 * Plug-ins management
	 * 
	 * Plug-ins are registered on page startup and re-applied automatically
	 * in each dialog.
	 * An entry point is also available for custom plug-ins not handled by
	 * default ZTFY package
	 */
	$.ZTFY.plugins = {

		_registry: null,

		register: function(callback, context, options) {
			if (this._registry == null) {
				this._registry = new Array()
			}
			this._registry.push([callback, context, options]);
		},

		callAndRegister: function(callback, context, parent, options) {
			callback.call(context, parent, options);
			if (this._registry == null) {
				this._registry = new Array()
			}
			this._registry.push([callback, context, options]);
		},

		call: function(parent) {
			var registry = this._registry;
			if (registry == null) {
				return;
			}
			for (var index in registry) {
				if (!$.isNumeric(index))  // IE indexOf !
					continue;
				var callback = registry[index][0];
				var context = registry[index][1];
				var options = registry[index][2];
				callback.call(context, parent, options);
			}
		},

		callCustomPlugins: function(parent) {
			$('[data-ztfy-plugin]', parent).each(function() {
				var element = this;
				var plugins = $(this).data('ztfy-plugin').split(/\s+/);
				$(plugins).each(function() {
					var funct = $.ZTFY.getFunctionByName(this);
					funct.call(window, element);
				});
			});
		}

	}  /** $.ZTFY.plugins */

	/**
	 * Widgets management
	 * 
	 * This is a small set of "standard" ZTFY widgets handled by custom packages
	 * but for which javascript code is defined into ZTFY.skin
	 */
	$.ZTFY.widgets = {

		initTabs: function(parent) {
			if (typeof($.fn.tabs) == 'undefined')
				return;
			$('DIV.form #tabforms UL.tabs', parent).tabs('DIV.panes > DIV');
		},

		// Dates input plug-in
		initDates: function(parent) {
			if (typeof($.fn.dynDateTime) == 'undefined')
				return;
			if ($.i18n_calendar === undefined) {
				var lang = $('html').attr('lang') || $('html').attr('xml:lang');
				$.i18n_calendar = lang;
				if (lang) {
					if (lang == 'en')
						$.ZTFY.getScript('/--static--/ztfy.jqueryui/js/lang/calendar-' + lang + '.min.js');
					else
						$.ZTFY.getScript('/--static--/ztfy.jqueryui/js/lang/calendar-' + lang + '-utf8.js');
				}
			}
			$('[data-ztfy-widget="datetime"]', parent).each(function() {
				var $this = $(this);
				$this.dynDateTime({
					showsTime: $this.data('datetime-showtime'),
					ifFormat: $this.data('datetime-format')
				});
			});
		},

		// Multi-select input plug-in
		initMultiselect: function(parent) {
			if (typeof($.fn.multiselect) == 'undefined')
				return;
			$('[data-ztfy-widget="multiselect"]', parent).each(function() {
				var $this = $(this);
				var data = $this.data();
				var references = data.multiselectReferences || '{}';
				if (typeof(references) == 'string') {
					references = $.parseJSON(references.replace(/'/g, '"'));
				}
				$this.multiselect({
					readonly: data.multiselectReadonly,
					input_class: data.multiselectClass,
					separator: data.multiselectSeparator || ',',
					min_query_length: data.multiselectMinLength || 3,
					input_references: references,
					on_search: function(query) {
						if (data.multiselectSearchCallback) {
							var callback = $.ZTFY.getFunctionByName(data.multiselectSearchCallback);
							var args = (data.multiselectSearchArgs || '').split(';');
							if (args.length > 2) {
								var index = args.length - 1;
								var value = args[index];
								if (value)
									args[index] = $.parseJSON(value.replace(/'/g, '"'));
							}
							args.splice(0, 0, query);
							return callback.apply(window, args);
						} else
							return '';
					},
					on_search_timeout: data.multiselectSearchTimeout || 300,
					max_complete_results: data.multiselectMaxResults || 20,
					enable_new_options: data.multiselectEnableNew,
					complex_search: data.multiselectComplexSearch,
					max_selection_length: data.multiselectMaxSelectionLength
				});
			});
		},

		// Color input plug-in
		initColors: function(parent) {
			if (typeof($.fn.ColorPicker) == 'undefined')
				return;
			$('[data-ztfy-widget="color-selector"]', parent).each(function() {
				var $this = $(this);
				var $input = $('INPUT', $this);
				$('DIV', $this).css('background-color', '#' + $input.val());
				if ($this.data('readonly') === undefined) {
					$this.ColorPicker({
						color: '#' + $input.val(),
						onShow: function(picker) {
							$(picker).fadeIn(500);
							return false;
						},
						onHide: function(picker) {
							$(picker).fadeOut(500);
							return false;
						},
						onChange: function(hsb, hex, rgb) {
							var element = $(this).data().colorpicker.el;
							$('INPUT', element).val(hex);
							$('DIV', element).css('background-color', '#' + hex);
						},
						onSubmit: function() {
							$(this).ColorPickerHide();
						}
					});
				}
			});
		},

		// Info hints plug-in
		initHints: function(parent) {
			$.ZTFY.ajax.check($.fn.tipsy, '/--static--/ztfy.jqueryui/js/jquery-tipsy.min.js', function() {
				var $form = $('DIV.form', $(parent));
				if ($form.data('ztfy-inputs-hints') == true) {
					$('INPUT[type!="hidden"]:not(.nohint), SELECT, TEXTAREA', $form).each(function(index, item) {
						$(item).tipsy({
							html: true,
							fallback: $('A.hint', $(item).closest('DIV.row')).attr('title'),
							gravity: 'nw'
						});
						$('A.hint:not(.nohide)', $(item).closest('DIV.row')).hide();
					});
				}
				$('A.hint', $form).tipsy({
					gravity: function(element) {
						return $(this).data('ztfy-hint-gravity') || 'sw';
					},
					offset: function(element) {
						return $(this).data('ztfy-hint-offset') || 0;
					}
				});
			});
		},

		// TinyMCE HTML editor plug-in
		initTinyMCE: function(parent) {
			if (typeof(tinyMCE) == 'undefined')
				return;
			$('[data-ztfy-widget="TinyMCE"]', parent).each(function() {
				var data = $(this).data();
				var options = {
					script_url: '/--static--/ztfy.jqueryui/js/tiny_mce/tiny_mce.js'
				}
				var new_options = data.tinymceOptions.split(';');
				for (var index in new_options) {
					if (!$.isNumeric(index))  // IE indexOf !
						continue;
					var new_option = new_options[index].split('=');
					switch (new_option[1]) {
						case 'true':
							options[new_option[0]] = true;
							break;
						case 'false':
							options[new_option[0]] = false;
							break;
						default:
							options[new_option[0]] = new_option[1];
					}
				}
				if (!tinyMCE.settings) {
					tinyMCE.init(options);
				}
			});
			$('[data-ztfy-widget="TinyMCE"]', parent).click(function(element) {
				if (element instanceof $.Event) {
					element  = element.srcElement || element.target;
				}
				if (tinyMCE.activeEditor) {
					tinyMCE.execCommand('mceRemoveControl', false, tinyMCE.activeEditor.id);
				}
				tinyMCE.execCommand('mceAddControl', false, $(element).attr('id'));
			});
		},

		// Fancybox plug-in
		initFancybox: function(parent) {
			if (typeof($.fn.fancybox) == 'undefined')
				return;
			$('[data-ztfy-widget="fancybox"]', parent).each(function() {
				var data = $(this).data();
				var elements = $(data.fancyboxSelector || 'IMG', this);
				if (data.fancyboxParent !== undefined)
					elements = elements.parents(data.fancyboxParent);
				var options = {
					type: data.fancyboxType || 'image',
					titleShow: data.fancyboxShowTitle,
					titlePosition: data.fancyboxTitlePosition || 'outside',
					hideOnContentClick: data.fancyboxClickHide === undefined ? true : data.fancyboxClickHide,
					overlayOpacity: data.fancyboxOverlayOpacity || 0.5,
					padding: data.fancyboxPadding || 10,
					margin: data.fancyboxMargin || 20,
					transitionIn: data.fancyboxTransitionIn || 'elastic',
					transitionOut: data.fancyboxTransitionOut || 'elastic'
				}
				if (data.fancyboxTitleFormat)
					options.titleFormat = $.ZTFY.getFunctionByName(data.fancyboxTitleFormat);
				else
					options.titleFormat = function(title, array, index, opts) {
						if (title && title.length) {
							var result = '<span id="fancybox-title-over"><strong>' + title + '</strong>';
							var description = $(array[index]).data('fancybox-description');
							if (description)
								result += '<br />' + description;
							result += '</span>';
							return result;
						} else
							return null;
					}
				if (data.fancyboxComplete)
					options.onComplete = $.ZTFY.getFunctionByName(data.fancyboxComplete);
				else
					options.onComplete = function() {
						$("#fancybox-wrap").hover(function() {
							$("#fancybox-title").slideDown('slow');
						}, function() {
							$("#fancybox-title").slideUp('slow');
						});
					}
				elements.fancybox(options);
			});
		}

	}  /** $.ZTFY.widgets */

	/**
	 * Dialogs management
	 */
	$.ZTFY.dialog = {

		switchGroup: function(source, target) {
			var target = $('DIV[id="group_' + target + '"]');
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
				var dialog = $.ZTFY.dialog.dialogs[$.ZTFY.dialog.getCount()-1];
				wrapper.load(dialog.src, dialog.callback);
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

		open: function(src, event, callback) {
			if (typeof($.fn.overlay) == 'undefined') {
				jAlert($.ZTFY.I18n.MISSING_OVERLAY, $.ZTFY.I18n.ERROR_OCCURED);
				return;
			}
			var src = src.replace(/ /g, '%20');
			/* Check for callback argument */
			if ($.isFunction(event)) {
				callback = event;
				event = null;
			}
			/* Stop event ! */
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
				callback: callback || $.ZTFY.dialog.openCallback,
				body: $('<div class="overlay"></div>').attr('id', id)
													  .css('z-index', expose_options.zIndex+1)
													  .appendTo($('body'))
			});
			var dialog = $('#' + id);
			dialog.empty()
				  .overlay(options)
				  .load();
			dialog.draggable({ handle: 'DIV[id="osx-container"], H1',
							   containment: 'window' });
		},

		openCallback: function(response, status, result) {
			if (status == 'error') {
				$(this).html(response);
			} else {
				var dialog = $.ZTFY.dialog.getCurrent();
				$.ZTFY.plugins.call(dialog);
				$.ZTFY.plugins.callCustomPlugins(dialog);
				var viewspace = $('DIV.viewspace', dialog);
				var help = $('DIV.form > FIELDSET > DIV.help', dialog);
				if (viewspace.length > 0) {
					var maxheight = $(window).height() - help.height() - 260;
					var position = viewspace.position();
					var barWidth = $.scrollbarWidth()
					viewspace.css('max-height', maxheight);
					if (viewspace.get(0).scrollHeight > maxheight) {
						$('<div></div>').addClass('scrollmarker')
										.addClass('top')
										.css('width', viewspace.width() - barWidth/2)
										.css('top', position.top)
										.hide()
										.appendTo(viewspace);
						$('<div></div>').addClass('scrollmarker')
										.addClass('bottom')
										.css('width', viewspace.width() - barWidth/2)
										.css('top', position.top + maxheight - 10)
										.appendTo(viewspace);
						viewspace.scroll(function(event) {
							var source = event.srcElement || event.target;
							var element = $(source);
							var scroll_top = $('DIV.scrollmarker.top', element);
							var top = element.scrollTop();
							if (top > 0) {
								scroll_top.show();
							} else {
								scroll_top.hide();
							}
							var scroll_bottom = $('DIV.scrollmarker.bottom', element);
							var maxheight = parseInt(element.css('max-height'));
							var target = maxheight + top - 10;
							if (target >= source.scrollHeight-20) {
								scroll_bottom.hide();
							} else {
								scroll_bottom.show();
							}
						});
					}
				}
			}
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
			$('DIV.tipsy').remove();
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

		getSubmitCallbacks: function(form) {
			var $form = $(form);
			var callbacks = new Array();
			var cb = $form.data('ztfy-submit-callback');
			if (cb)
				callbacks.push([$form, cb]);
			$('[data-ztfy-submit-callback]', $(form)).each(function() {
				var input = $(this);
				callbacks.push([input, input.data('ztfy-submit-callback')]);
			})
			return callbacks;
		},

		checkSubmitCallbacks: function(form) {
			var callbacks = $.ZTFY.form.getSubmitCallbacks(form);
			if (!callbacks.length)
				return true;
			var output = new Array();
			var callbacks_result = true;
			for (var index in callbacks) {
				if (!$.isNumeric(index))  // IE indexOf !
					continue;
				var callback = callbacks[index]
				var input = callback[0];
				var funct = callback[1];
				var result = $.ZTFY.executeFunctionByName(funct, undefined, form, input);
				if ((result !== undefined) && (result !== true)) {
					if (result === false) {
						callbacks_result = false;
					} else if (typeof(result) == 'string') {
						output.push(result);
					} else if (result.length && (result.length > 0)) {
						output = output.concat(result);
					}
				}
			}
			if (output.length > 1) {
				jAlert($.ZTFY.I18n.ERRORS_OCCURED + '\n' + output.join('\n'), $.ZTFY.I18n.WARNING);
				return false;
			} else if (output.length == 1) {
				jAlert($.ZTFY.I18n.ERROR_OCCURED + '\n' + output.join('\n'), $.ZTFY.I18n.WARNING);
				return false;
			} else
				return callbacks_result;
		},

		submit: function(event) {
			var $form = $(this);
			if ($form.data('submitted') || !$.ZTFY.form.checkSubmitCallbacks(this)) {
				$.ZTFY.skin.stopEvent(event);
				return false;
			}
			$form.data('submitted', true);
			$.ZTFY.ajax.check($.progressBar, '/--static--/ztfy.jqueryui/js/jquery-progressbar.min.js', function() {
				if ($.progressBar) {
					$.progressBar.submit($form);
				}
			});
		},

		reset: function(form) {
			form.reset();
			$('input:first', form).focus();
		},

		showErrors: function(result) {
			var dialog = $.ZTFY.dialog.getCurrent();
			var prev_height = $('DIV.status', dialog).outerHeight(true);
			$('DIV.status', dialog).remove();
			$('DIV.error', dialog).each(function(index, item) {
				$('DIV.widget', $(item)).detach()
										.insertAfter($(item));
				$(item).remove();
			});
			var status = $('<div></div>').addClass('status error');
			$('<div></div>').addClass('summary')
							.text(result.errors.status)
							.appendTo(status);
			var errors = $('<ul></ul>').appendTo(status);
			if (result.errors.errors) {
				for (var i in result.errors.errors) {
					if (!$.isNumeric(i))  // IE indexOf !
						continue;
					var error = result.errors.errors[i];
					if (error.widget) {
						$('<li></li>').text(error.widget + ' : ' + error.message)
									  .appendTo(errors);
						var widget = $('[id="' + error.id + '"]', dialog).parents('DIV.widget');
						var row = $(widget).parents('DIV.row');
						var div = $('<div></div>').addClass('error')
												  .append($('<div></div>').addClass('error')
																		  .text(error.message))
												  .insertBefore(widget);
						widget.detach().appendTo(div);
					} else {
						$('<li></li>').text(error.message)
									  .appendTo(errors);
					}
				}
			}
			$('FORM', dialog).before(status)
							 .data('submitted', false);
			var new_height = status.outerHeight(true);
			if (new_height != prev_height) {
				$('DIV.scrollmarker', dialog).each(function(index, item) {
					$(item).css('top', parseInt($(item).css('top')) - prev_height + new_height);
				});
			}
		},

		add: function(form, parent, callback, data) {
			var $form = $(form);
			if ($form.data('submitted') || !$.ZTFY.form.checkSubmitCallbacks(form)) {
				return false;
			}
			$form.data('submitted', true);
			$.ZTFY.form.check(function() {
				if (typeof(tinyMCE) != 'undefined') {
					tinyMCE.triggerSave();
				}
				if (parent) {
					data.parent = parent;
				}
				var action = $form.attr('action').replace(/\?X-Progress-ID=.*/, '');
				$($.ZTFY.form).data('add_action', action);
				$.ZTFY.ajax.submit(form, action + '/@@ajax/ajaxCreate', data || {}, callback || $.ZTFY.form._addCallback, null, 'json');
			});
			return false;
		},

		_addCallback: function(result, status) {
			if (status == 'success') {
				if (typeof(result) == "string")
					result = $.parseJSON(result);
				var output = result.output;
				switch (output) {
					case 'ERRORS':
						$.ZTFY.form.showErrors(result);
						break;
					case 'OK':
						$.ZTFY.dialog.close();
						$('DIV.status').remove();
						var message = result.message || $.ZTFY.I18n.DATA_UPDATED;
						$('DIV.required-info').after('<div class="status success"><div class="summary">' + message + '</div></div>');
						break;
					case 'NONE':
						$.ZTFY.dialog.close();
						$('DIV.status').remove();
						var message = result.message || $.ZTFY.I18n.NO_UPDATE;
						$('DIV.required-info').after('<div class="status warning"><div class="summary">' + message + '</div></div>');
						break;
					case 'PASS':
						$.ZTFY.dialog.close();
						$('DIV.status').remove();
						break;
					case 'RELOAD':
						window.location.href = window.location.href;
						break;
					case 'REDIRECT':
						window.location.href = result.target;
						break;
					case 'CALLBACK':
						if (result.close_dialog)
							$.ZTFY.dialog.close();
						$.ZTFY.executeFunctionByName(result.callback, undefined, result.options);
						break;
					default:
						if (output && output.startsWith('<!-- OK -->')) {
							$.ZTFY.dialog.close();
							$('DIV.form').replaceWith(output);
						} else {
							var dialog = $.ZTFY.dialog.getCurrent();
							$('DIV.dialog', dialog).replaceWith(output);
							var form = $('FORM', dialog);
							form.attr('action', $($.ZTFY.form).data('add_action'));
							$('INPUT[id="'+form.attr('id')+'-buttons-add"]', dialog).bind('click', function(event) {
								$.ZTFY.form.add(this.form, result.parent);
							});
							$('INPUT[id="'+form.attr('id')+'-buttons-cancel"]', dialog).bind('click', function(event) {
								$.ZTFY.dialog.close();
							});
							$('#tabforms UL.tabs', dialog).tabs($(dialog).selector + ' DIV.panes > DIV');
						}
				}
				if (output != 'ERRORS') {
					setTimeout('$.ZTFY.form.hideStatus();', 2000);
				}
			}
		},

		edit: function(form, base, callback, data) {
			var $form = $(form);
			if ($form.data('submitted') || !$.ZTFY.form.checkSubmitCallbacks(form)) {
				return false;
			}
			$form.data('submitted', true);
			$.ZTFY.form.check(function() {
				if (typeof(tinyMCE) != 'undefined') {
					tinyMCE.triggerSave();
				}
				var action = $form.attr('action').replace(/\?X-Progress-ID=.*/, '');
				$($.ZTFY.form).data('edit_action', action);
				$.ZTFY.ajax.submit(form, action + '/@@ajax/ajaxEdit', data || {}, callback || $.ZTFY.form._editCallback, null, 'json');
			});
			return false;
		},

		_editCallback: function(result, status, response) {
			if (status == 'success') {
				if (typeof(result) == "string")
					result = $.parseJSON(result);
				var output = result.output;
				switch (output) {
					case 'ERRORS':
						$.ZTFY.form.showErrors(result);
						break;
					case 'OK':
						$.ZTFY.dialog.close();
						$('DIV.status').remove();
						var message = result.message || $.ZTFY.I18n.DATA_UPDATED;
						$('DIV.required-info').after('<div class="status success"><div class="summary">' + message + '</div></div>');
						break;
					case 'NONE':
						$.ZTFY.dialog.close();
						$('DIV.status').remove();
						var message = result.message || $.ZTFY.I18n.NO_UPDATE;
						$('DIV.required-info').after('<div class="status warning"><div class="summary">' + message + '</div></div>');
						break;
					case 'PASS':
						$.ZTFY.dialog.close();
						$('DIV.status').remove();
						break;
					case 'RELOAD':
						window.location.href = window.location.href;
						break;
					case 'REDIRECT':
						window.location.href = result.target;
						break;
					case 'CALLBACK':
						if (result.close_dialog)
							$.ZTFY.dialog.close();
						$.ZTFY.executeFunctionByName(result.callback, undefined, result.options);
						break;
					default:
						if (output && output.startsWith('<!-- OK -->')) {
							$.ZTFY.dialog.close();
							$('DIV.form').replaceWith(output);
						} else {
							var dialog = $.ZTFY.dialog.getCurrent();
							$('DIV.dialog', dialog).replaceWith(output);
							var form = $('FORM', dialog);
							form.attr('action', $($.ZTFY.form).data('edit_action'));
							$('INPUT[id="'+form.attr('id')+'-buttons-dialog_submit"]', dialog).bind('click', function(event) {
								$.ZTFY.form.edit(this.form);
							});
							$('INPUT[id="'+form.attr('id')+'-buttons-dialog_cancel"]', dialog).bind('click', function(event) {
								$.ZTFY.dialog.close();
							});
							$('#tabforms UL.tabs', dialog).tabs($(dialog).selector + ' DIV.panes > DIV');
						}
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
				$('LEGEND').after('<div class="status success"><div class="summary">' + $.ZTFY.I18n.DATA_UPDATED + '</div></div>');
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
				$('TD.id', this).each(function (i) {
					ids[ids.length] = $(this).text();
				});
				var data = {
					ids: ids
				}
				if (ids.length > 1) {
					$.ZTFY.ajax.post(window.location.href + '/@@ajax/ajaxUpdateOrder', data, null, function(request, status, error) {
						jAlert(request.responseText, $.ZTFY.I18n.ERROR_OCCURED, window.location.reload);
					});
				}
			}
		},

		init: function(parent) {
			if (typeof($.fn.sortable) == 'undefined')
				return;
			$('TABLE.orderable TBODY', parent).sortable($.ZTFY.sortable.options);
		}

	}  /** $.ZTFY.sortable */

	/**
	 * Treeviews management
	 */
	$.ZTFY.treeview = {

		init: function(parent) {
			if (typeof($.fn.treeTable) == 'undefined')
				return;
			$('TABLE.treeview', parent).each(function() {
				var $this = $(this);
				var data = $this.data();
				$this.treeTable({
					treeColumn: data.treeColumn === undefined ? 1 : data.treeColumn,
					initialState: data.initialState === undefined ? 'expanded' : data.initialState
				});
			});
		},

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

	/**
	 * Small set of extra widgets defined in other packages
	 */
	$.ZTFY.extras = {

		// Init main container size
		initContainerSize: function(element) {
			$(element).css('min-height', $($(element).data('container-sizer')).height());
		},

		// Captcha from ZTFY.captcha package
		initCaptcha: function(element) {
			if (element instanceof $.Event) {
				element = element.srcElement || element.target;
			}
			var data = $(element).data();
			var now = new Date();
			var target = '@@captcha.jpeg?id=' + data.captchaId + unescape('%26') + now.getTime();
			$(element).attr('src', target)
					  .off('click')
					  .on('click', $.ZTFY.extras.initCaptcha);
		}

	}

	/**
	 * Init I18n strings
	 */
	$.ZTFY.I18n = {

		WARNING: "!! WARNING !!",

		ERROR_OCCURED: "An error occured!",
		ERRORS_OCCURED: "Some errors occured!",

		BAD_LOGIN_TITLE: "Bad login!",
		BAD_LOGIN_MESSAGE: "Your anthentication credentials didn't allow you to open a session; please check your credentials or contact administrator.",

		CONFIRM: "Confirm",
		CONFIRM_REMOVE: "Removing this content can't be undone. Do you confirm?",

		NO_UPDATE: "No changes were applied.",
		DATA_UPDATED: "Data successfully updated.",

		MISSING_OVERLAY: "JQuery « overlay » plug-in is required; please include JQuery-tools resources in your page!"

	}

	var lang = $('HTML').attr('lang') || $('HTML').attr('xml:lang');
	if (lang && (lang != 'en'))
		$.ZTFY.getScript('/--static--/ztfy.skin/js/i18n/' + lang + '.js');


	/**
	 * Initialize ZTFY plug-ins and events
	 */
	$(document).ready(function() {

		// Call and register ZTFY inner plug-ins
		$.ZTFY.plugins.callAndRegister($.ZTFY.widgets.initTabs, window, document);
		$.ZTFY.plugins.callAndRegister($.ZTFY.widgets.initDates, window, document);
		$.ZTFY.plugins.callAndRegister($.ZTFY.widgets.initMultiselect, window, document);
		$.ZTFY.plugins.callAndRegister($.ZTFY.widgets.initHints, window, document);
		$.ZTFY.plugins.callAndRegister($.ZTFY.widgets.initColors, window, document);
		$.ZTFY.plugins.callAndRegister($.ZTFY.widgets.initTinyMCE, window, document);
		$.ZTFY.plugins.callAndRegister($.ZTFY.widgets.initFancybox, window, document);
		$.ZTFY.plugins.callAndRegister($.ZTFY.sortable.init, window, document);
		$.ZTFY.plugins.callAndRegister($.ZTFY.treeview.init, window, document);
		$.ZTFY.plugins.callCustomPlugins(document);

		// Register other common plug-ins
		$('A[rel="external"]').attr('target', '_blank');
		$(document).on('submit', 'FORM', $.ZTFY.form.submit);

	});

})(jQuery);