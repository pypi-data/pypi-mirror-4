/*jslint vars: true, plusplus: true, maxerr: 50, indent: 4 */
/*global jq: false, document: false, window: false */

/**
 * JavaScript for the ReferenceColumn with autocomplete features
 * 
 * @author keul
 */

if (!window.DATAGRIDFIELD_REFERENCE_ENABLED) {
	/*
	 * This trick help us to run the autocomplete only once
	 * (if we have more than one ReferenceColumn in a page
	 */
	window.DATAGRIDFIELD_REFERENCE_ENABLED = true;
	jq(document).ready(function () {
		/**
		 * The first time we get the focus, we will enable the autocomplete 
		 */
		jq('.dataGridAutocompleteColumn').live('focus', function () {
			var $this = jq(this);
			if (!$this.data('autocompleteEnabled')) {
				if (window.console && window.console.info) {
					window.console.info('Autocomplete enabled onto field');
					window.console.log($this);
				}
				$this.data('autocompleteEnabled', true);
				var configuration = $this.prevAll('.edit_common');
				var contextCall = configuration.attr('data-context-call') + '/dataGridAutocomplete';
				var query = [], i = 0;

				var object_provides = configuration.attr('data-object-provides');
				if (object_provides) {
					object_provides = object_provides.split(',');
					for (i = 0; i < object_provides.length; i++) {
						query.push('object_provides:list=' + object_provides[i]);
					}
				}

				var search_site = configuration.attr('data-search-site');
				var surf_site = configuration.attr('data-surf-site');
				if (search_site) {
					query.push('search_site=1');
				}
				if (surf_site) {
					query.push('surf_site=1');
				}

				if (query) {
					contextCall += '?';
					contextCall += query.join('&');
				}

				if ($this.autocomplete) {
					$this.autocomplete({
						source: contextCall,
						focus: function (event, ui) {
							// $this.prev().val(ui.item.value);
							// $this.val(ui.item.label);
							event.preventDefault();
						},
						select: function (event, ui) {
							$this.prev().val(ui.item.value);
							$this.val(ui.item.label);
							event.preventDefault();
						}
					});
				} else {
					if (window.console && window.console.error) {
						window.console.error("Can't find jQueryUI autocomplete feature");
					}
				}
			}
		});
	});
}

