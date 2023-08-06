(function($) {

	if (typeof($.ZTFY) == 'undefined') {
		$.ZTFY = {}
	}

	$.ZTFY.thesaurus = {

		/**
		 * Remove thesaurus
		 */
		remove: function(oid, source) {
			jConfirm($.ZTFY.I18n.CONFIRM_REMOVE, $.ZTFY.I18n.CONFIRM, function(confirmed) {
				if (confirmed) {
					var data = {
						oid: oid
					}
					$.ZTFY.ajax.post(window.location.href + '/@@ajax/ajaxRemove', data, window.location.reload, function(request, status, error) {
						jAlert(request.responseText, $.ZTFY.I18n.ERROR_OCCURED, window.location.reload);
					});
				}
			});
		},


		/**
		 * Thesaurus tree management
		 */
		tree: {

			showHideExtract: function(source) {
				var extract = $(source).attr('ztfy_extract');
				if ($(source).hasClass('hide')) {
					$('DIV.tree SPAN.square[ztfy_extract=' + extract + ']').css('visibility', 'visible')
																		   .each(function() {
						if ($(this).hasClass('used')) {
							$(this).css('background-color', '#'+$(source).attr('ztfy_color'))
								   .click(function() {
									   $.ZTFY.thesaurus.tree.switchExtract(this);
								   });
						} else {
							var source_div = $(this).parents('DIV').get(2);
							if ($(source_div).hasClass('form') || $('SPAN[ztfy_extract='+extract+']:first', source_div).hasClass('used')) {
								$(this).css('background-color', 'white')
									   .click(function() {
										   $.ZTFY.thesaurus.tree.switchExtract(this);
									   });
							} else {
								$(this).css('background-color', 'silver');
							}
						}
					});
					$(source).css('background-image', "url('/--static--/ztfy.thesaurus/img/visible.gif')")
							 .removeClass('hide');
				} else {
					$('DIV.tree SPAN.square[ztfy_extract=' + extract + ']').css('visibility', 'hidden')
																		   .unbind('click');
					$(source).css('background-image', "url('/--static--/ztfy.thesaurus/img/hidden.gif')")
							 .addClass('hide');
				}
			},

			expand: function(source) {
				if ($(source).attr('src') == '/--static--/ztfy.thesaurus/img/plus.png') {
					$(source).attr('src', '/--static--/ztfy.thesaurus/img/loader.gif');
					var context = $(source).parents('DIV.tree').attr('ztfy_base');
					var term = $('A', $(source).parents('DIV').get(0)).text();
					var data = $.data($.ZTFY.thesaurus.tree, 'source') || new Array();
					data[term] = source;
					$.data($.ZTFY.thesaurus.tree, 'source', data);
					$.ZTFY.ajax.post(context + '/@@terms.html/@@ajax/getNodes', {'term': term}, $.ZTFY.thesaurus.tree._expandCallback);
				} else {
					$.ZTFY.thesaurus.tree.collapse(source);
				}
			},

			_expandCallback: function(result, status) {
				if (status == 'success') {
					var term = result.term;
					var source = $.data($.ZTFY.thesaurus.tree, 'source')[term];
					var source_div = $(source).parents('DIV').get(0);
					var tree = $(source).parents('DIV.tree');
					var show_links = tree.attr('ztfy_details') != 'off';
					var $target = $('DIV.subnodes', $(source).parents('DIV').get(0));
					for (var index in result.nodes) {
						var node = result.nodes[index];
						var $div = $('<div></div>');
						$('<img />').addClass('plminus')
									.attr('src', node.expand ? '/--static--/ztfy.thesaurus/img/plus.png'
															 : '/--static--/ztfy.thesaurus/img/lline.png')
									.click(function() {
										$.ZTFY.thesaurus.tree.expand(this);
									})
									.appendTo($div);
						$('<a></a>').addClass(show_links ? 'label' : '')
									.addClass(node.cssClass)
									.click(function() {
										$.ZTFY.thesaurus.tree.openTerm(this);
									})
									.html(node.label).appendTo($div);
						$('<span> </span>').appendTo($div);
						for (var ind_ext in node.extensions) {
							var extension = node.extensions[ind_ext];
							$('<img />').addClass('extension')
										.attr('src', extension.icon)
										.attr('ztfy_view', extension.view)
										.click(function() {
											$.ZTFY.thesaurus.tree.openExtension(this);
										})
										.appendTo($div);
						}
						node.extracts.reverse();
						for (var ind_ext in node.extracts) {
							var extract = node.extracts[ind_ext];
							var checker = $('DIV.extract SPAN.showhide[ztfy_extract=' + extract.name + ']');
							var $span = $('<span></span>').addClass('square')
														  .addClass(extract.used ? 'used' : null)
														  .attr('title', extract.title)
														  .attr('ztfy_extract', extract.name);
							if ($(checker).hasClass('hide')) {
								$span.css('visibility', 'hidden');
							} else if ($('SPAN[ztfy_extract='+extract.name+']:first', source_div).hasClass('used')) {
								$span.css('background-color', extract.used ? '#'+extract.color : 'white');
								$span.click(function() {
									$.ZTFY.thesaurus.tree.switchExtract(this);
								});
							} else {
								$span.css('background-color', 'silver');
							}
							$span.appendTo($div);
						}
						$('<div></div>').addClass('subnodes').appendTo($div);
						$div.appendTo($target);
					}
					$(source).attr('src', '/--static--/ztfy.thesaurus/img/minus.png');
				}
			},

			collapse: function(source) {
				$('DIV.subnodes', $(source).parents('DIV').get(0)).empty();
				$(source).attr('src', '/--static--/ztfy.thesaurus/img/plus.png');
			},

			openTerm: function(source) {
				var tree = $(source).parents('DIV.tree');
				if (tree.attr('ztfy_details') == 'off') {
					return;
				}
				var term = $(source).text().replace(/ /g, '%20');
				if ($.browser.msie) {
					term = $.UTF8.encode(term);
				}
				$.ZTFY.dialog.open('++terms++/' + term + '/@@properties.html');
			},

			openExtension: function(source) {
				var view = $(source).attr('ztfy_view').replace('/ /g', '%20');
				if ($.browser.msie) {
					view = $.UTF8.encode(view);
				}
				$.ZTFY.dialog.open(view);
			},

			reloadTerm: function(source) {
				$.ZTFY.dialog.close();
				var img = $('IMG.plminus:first', $("A:econtains(" + source.replace('&#039;','\'') + ")").parent('DIV'));
				$.ZTFY.thesaurus.tree.collapse(img);
				$.ZTFY.thesaurus.tree.expand(img);
			},

			switchExtract: function(source) {
				var extract = $(source).attr('ztfy_extract');
				var checker = $('DIV.extract SPAN.showhide[ztfy_extract=' + extract + ']');
				if (checker.attr('ztfy_enabled') == 'False') {
					return;
				}
				var label = $('A.label', $(source).parents('DIV')).get(0);
				if ($.ZTFY.rgb2hex($(source).css('background-color')) == '#ffffff') {
					/* Don't confirm when adding a term */ 
					$.ZTFY.thesaurus.tree._switchExtract(label, extract);
				} else {
					if ($(label).parent('DIV').children('IMG').attr('src').endsWith('/lline.png')) {
						/* Don't confirm if term don't have any specific term */
						$.ZTFY.thesaurus.tree._switchExtract(label, extract);
					} else {
						jConfirm($.ZTFY.thesaurus.I18n.CONFIRM_UNSELECT_WITH_CHILD, $.ZTFY.I18n.CONFIRM, function(confirmed) {
							if (confirmed) {
								$.ZTFY.thesaurus.tree._switchExtract(label, extract);
							}
						});
					}
				}
			},

			_switchExtract: function(label, extract) {
				var term = $(label).text();
				$.ZTFY.ajax.post('@@terms.html/@@ajax/switchExtract',
								 { 'term': term, 'extract': extract },
								 $.ZTFY.thesaurus.tree._switchExtractCallback);
			},

			_switchExtractCallback: function(result, status) {
				if (status == 'success') {
					var term = result.term;
					var label = $('A.label:withtext(' + term + ')');
					var div = $(label).parents('DIV').get(0);
					if (result.used) {
						$('DIV.subnodes:first > DIV', div).children('SPAN[ztfy_extract='+result.extract+']', div)
														  .css('background-color', 'white')
														  .unbind('click')
														  .click(function() {
															  $.ZTFY.thesaurus.tree.switchExtract(this);
														  });
						$('SPAN[ztfy_extract='+result.extract+']:first', div).addClass('used')
																			 .css('background-color', '#'+result.color);
					} else {
						$('SPAN[ztfy_extract='+result.extract+']', div).removeClass('used')
																	   .css('background-color', 'silver')
																	   .unbind('click');
						$('SPAN[ztfy_extract='+result.extract+']:first', div).css('background-color', 'white')
																			 .click(function() {
																				 $.ZTFY.thesaurus.tree.switchExtract(this);
																			 });
					}
				}
			}
		},

		findTerms: function(query, thesaurus_name, extract_name) {
			var result;
			var options = {
				url: $.ZTFY.ajax.getAddr(),
				type: 'POST',
				method: 'findTerms',
				async: false,
				params: {
					query: query,
					thesaurus_name: thesaurus_name || '',
					extract_name: extract_name || ''
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

		download: function(form) {
			$.ZTFY.form.check(function() {
				$.ZTFY.thesaurus._download(form);
			});
			return false;
		},

		_download: function(form) {
			var action = $(form).attr('action');
			var target = action + '/@@ajax/ajaxDownload';
			var iframe = $('<iframe></iframe>').hide()
											   .attr('name', 'downloadFrame')
											   .appendTo($(form));
			$(form).attr('action', target)
				   .attr('target', 'downloadFrame')
				   .ajaxSubmit({
					   success: function() {
							$.ZTFY.dialog.close();
					   }
				   });
			/** !! reset form action after submit !! */
			$(form).attr('action', action);
		}
	}

	var lang = $('HTML').attr('lang') || $('HTML').attr('xml:lang') || 'en';
	$.getScript('/--static--/ztfy.thesaurus/js/i18n/' + lang + '.js');

})(jQuery);