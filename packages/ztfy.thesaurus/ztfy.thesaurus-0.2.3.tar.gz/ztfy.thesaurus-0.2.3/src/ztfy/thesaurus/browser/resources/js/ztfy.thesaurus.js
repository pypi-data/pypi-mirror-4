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
					$.ZTFY.ajax.post(window.location.href + '/@@ajax/ajaxRemove', data, function() {
						window.location.reload();
					}, function(request, status, error) {
						jAlert(request.responseText, $.ZTFY.I18n.ERROR_OCCURED, window.location.reload);
					});
				}
			});
		},


		/**
		 * Thesaurus tree management
		 */
		tree: {

			// Show or hide an entire extract
			showHideExtract: function(source) {
				var source = this;
				var extract = $(source).data('ztfy-extract-name');
				if ($(source).hasClass('hide')) {
					$('DIV.tree SPAN.square[data-ztfy-extract-name="' + extract + '"]').css('visibility', 'visible')
																					   .each(function() {
						if ($(this).hasClass('used')) {
							$(this).css('background-color', '#'+$(source).data('ztfy-extract-color'))
								   .click(function() {
									   $.ZTFY.thesaurus.tree.switchExtract(this);
								   });
						} else {
							var source_div = $(this).parents('DIV').get(2);
							if ($(source_div).hasClass('form') || $('SPAN[data-ztfy-extract-name="'+extract+'"]:first', source_div).hasClass('used')) {
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
					$('DIV.tree SPAN.square[data-ztfy-extract-name="' + extract + '"]').css('visibility', 'hidden')
																					   .unbind('click');
					$(source).css('background-image', "url('/--static--/ztfy.thesaurus/img/hidden.gif')")
							 .addClass('hide');
				}
			},

			// Expand term node
			expand: function(source) {
				if ($(source).attr('src') == '/--static--/ztfy.thesaurus/img/plus.png') {
					$(source).attr('src', '/--static--/ztfy.thesaurus/img/loader.gif');
					var context = $(source).closest('DIV.tree').data('ztfy-base');
					var term = $('A', $(source).closest('DIV').get(0)).text();
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
					var source_div = $(source).closest('DIV').get(0);
					var tree = $(source).closest('DIV.tree');
					var show_links = tree.data('ztfy-tree-details') != 'off';
					var $target = $('DIV.subnodes', $(source).closest('DIV').get(0));
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
										.data('ztfy-view', extension.view)
										.click(function() {
											$.ZTFY.thesaurus.tree.openExtension(this);
										})
										.appendTo($div);
						}
						node.extracts.reverse();
						for (var ind_ext in node.extracts) {
							var extract = node.extracts[ind_ext];
							var checker = $('DIV.extract SPAN.showhide[data-ztfy-extract-name="' + extract.name + '"]');
							var $span = $('<span></span>').addClass('square')
														  .addClass(extract.used ? 'used' : null)
														  .attr('title', extract.title)
														  .attr('data-ztfy-extract-name', extract.name);
							if ($(checker).hasClass('hide')) {
								$span.css('visibility', 'hidden');
							} else if ($('SPAN[data-ztfy-extract-name="'+extract.name+'"]:first', source_div).hasClass('used')) {
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

			// Collapse term node
			collapse: function(source) {
				$('DIV.subnodes', $(source).closest('DIV').get(0)).empty();
				$(source).attr('src', '/--static--/ztfy.thesaurus/img/plus.png');
			},

			// Open term properties dialog
			openTerm: function(source) {
				var tree = $(source).closest('DIV.tree');
				if (tree.data('ztfy-tree-details') == 'off') {
					return;
				}
				var term = $(source).text().replace(/ /g, '%20');
				if ($.browser.msie) {
					term = $.UTF8.encode(term);
				}
				$.ZTFY.dialog.open('++terms++/' + term + '/@@properties.html');
			},

			// Open term properties from search engine
			openTermFromSearch: function(source) {
				if (source instanceof $.Event) {
					var source  = source.srcElement || source.target;
				}
				var term = $(source).text().replace(/ /g, '%20');
				if (term) {
					if ($.browser.msie) {
						term = $.UTF8.encode(term);
					}
					$.ZTFY.dialog.open('++terms++/' + term + '/@@properties.html');
				}
			},

			// Open term extension properties dialog
			openExtension: function(source) {
				var view = $(source).data('ztfy-view').replace('/ /g', '%20');
				if ($.browser.msie) {
					view = $.UTF8.encode(view);
				}
				$.ZTFY.dialog.open(view);
			},

			// Reload a term after properties change
			reloadTerm: function(options) {
				$.ZTFY.dialog.close();
				var source = options.source;
				var img = $('IMG.plminus:first', $("A:econtains(" + source.replace('&#039;','\'') + ")").closest('DIV'));
				$.ZTFY.thesaurus.tree.collapse(img);
				$.ZTFY.thesaurus.tree.expand(img);
			},

			// Switch extract selection for a given term
			switchExtract: function(source) {
				if (source instanceof $.Event) {
					$.ZTFY.skin.stopEvent(source);
					var source  = source.srcElement || source.target;
				}
				var extract = $(source).data('ztfy-extract-name');
				var checker = $('DIV.extract SPAN.showhide[data-ztfy-extract-name="' + extract + '"]');
				if (checker.data('ztfy-enabled') == false) {
					return;
				}
				var label = $('A.label', $(source).closest('DIV')).get(0);
				if ($.ZTFY.rgb2hex($(source).css('background-color')) == '#ffffff') {
					/* Don't confirm when adding a term */ 
					$.ZTFY.thesaurus.tree._switchExtract(label, extract);
				} else {
					if ($(label).closest('DIV').children('IMG').attr('src').endsWith('/lline.png')) {
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
					var div = $(label).closest('DIV').get(0);
					if (result.used) {
						$('DIV.subnodes:first > DIV', div).children('SPAN[data-ztfy-extract-name="'+result.extract+'"]', div)
														  .css('background-color', 'white')
														  .unbind('click')
														  .click(function() {
															  $.ZTFY.thesaurus.tree.switchExtract(this);
														  });
						$('SPAN[data-ztfy-extract-name="'+result.extract+'"]:first', div).addClass('used')
																						 .css('background-color', '#'+result.color);
					} else {
						$('SPAN[data-ztfy-extract-name="'+result.extract+'"]', div).removeClass('used')
																				   .css('background-color', 'silver')
																				   .off('click');
						$('SPAN[data-ztfy-extract-name="'+result.extract+'"]:first', div).css('background-color', 'white')
																						 .on('click', function() {
																							 $.ZTFY.thesaurus.tree.switchExtract(this);
																						 });
					}
				}
			}
		},

		// Thesaurus terms search engine entry point
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

		// Thesaurus terms search engine entry point
		findTermsWithLabel: function(query, thesaurus_name, extract_name) {
			var result;
			var options = {
				url: $.ZTFY.ajax.getAddr(),
				type: 'POST',
				method: 'findTermsWithLabel',
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

		// Thesaurus download management
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
					   iframe: true,
					   iframeTarget: iframe,
					   success: function() {
							$.ZTFY.dialog.close();
					   }
				   });
			/** !! reset form action after submit !! */
			$(form).attr('action', action);
		}
	}


	/**
	 * Init I18n strings
	 */
	$.ZTFY.thesaurus.I18n = {

		CONFIRM_UNSELECT_WITH_CHILD: "Removing this term from this extract will also remove all it's specific terms and their synonyms. Are you sure?"

	}

	var lang = $('HTML').attr('lang') || $('HTML').attr('xml:lang');
	if (lang && (lang != 'en'))
		$.ZTFY.getScript('/--static--/ztfy.thesaurus/js/i18n/' + lang + '.js');


	/**
	 * Initialize thesaurus events
	 */
	$(document).ready(function() {
		$('DIV.extract').on('click', 'SPAN.showhide', $.ZTFY.thesaurus.tree.showHideExtract);
		$('DIV.tree SPAN.square').click($.ZTFY.thesaurus.tree.switchExtract);
		$('FIELDSET.search').on('click', 'A.bit-box', $.ZTFY.thesaurus.tree.openTermFromSearch);
	});

})(jQuery);