$.widget("dawa.dawaautocomplete", {
	options: {
		jsonp: !("withCredentials" in (new XMLHttpRequest())),
		baseUrl: 'https://dawa.aws.dk',
		minLength: 2,
		delay: 0,
		adgangsadresserOnly: false,
		autoFocus: true,
		timeout: 10000,
		error: null,
		params: {}
	},


	_create: function () {
		var element = this.element;
		var options = this.options;
		var autocompleteWidget = this;

		// perform a GET request to DAWA, caching the response
		function get(path, params, cache, cb) {
			var stringifiedParams = JSON.stringify(params);
			if (cache && cache[stringifiedParams]) {
				return cb(cache[stringifiedParams]);
			}
			$.ajax({
				url: options.baseUrl + path,
				dataType: options.jsonp ? "jsonp" : "json",
				data: $.extend({}, params, options.params),
				timeout: options.timeout,
				success: function (data) {
					if (cache) {
						cache[stringifiedParams] = data;
					}
					cb(data);
				},
				error: options.error
			});
		}

		var caches = [{}, {}, {}];
		var paths = ['/vejnavne/autocomplete', '/adgangsadresser/autocomplete', '/adresser/autocomplete'];

		var prevSearch = "", prevResultType = 0;

		// perform an autocomplete GET request to DAWA.
		// If there is at most one result, continue to next type.
		// We autocomplete through vejnavne, adgangsadresser and adresser.
		function invokeSource(typeIdx, q, cb) {
			var maxTypeIdx = options.adgangsadresserOnly ? 1 : 2;
			var params = {q: q};
			if (autocompleteWidget.constrainedToAdgangsAdresseId) {
				params = {adgangsadresseid: autocompleteWidget.constrainedToAdgangsAdresseId};
				typeIdx = 2;

				// the constraint to search for adresser for a specific adgangsadresse is a one-off, so reset it
				autocompleteWidget.constrainedToAdgangsAdresseId = undefined;
			}

			get(paths[typeIdx], params, caches[typeIdx], function (data) {
				if (data.length <= 1 && typeIdx < maxTypeIdx) {
					invokeSource(typeIdx + 1, q, cb);
				}
				else {
					prevResultType = typeIdx;
					prevSearch = q;
					cb(data);
				}
			});
		}

		var autocompleteOptions = $.extend({}, options, {
			source: function (request, response) {
				var q = request.term;

				// we start over searching in vejnavne (index 0) if the current query is not a prefix of
				// the previous one.
				var sourceTypeIdx = q.indexOf(prevSearch) !== 0 ? 0 : prevResultType;

				return invokeSource(sourceTypeIdx, q, response);
			},
			select: function (event, ui) {
				event.preventDefault();
				var item = ui.item;
				if (item.vejnavn) {
					element.val(ui.item.tekst + ' ');
					setTimeout(function () {
						element.autocomplete('search');
					});
				}
				else if (item.adgangsadresse) {
					if (options.adgangsadresserOnly) {
						element.val(item.tekst);
						autocompleteWidget._trigger('select', null, item);
						return;
					}
					var adgAdr = item.adgangsadresse;
					// We need to check if there is more than one
					// adresse associated with the adgangsadresse.
					get(
						'/adresser/autocomplete',
						{adgangsadresseid: adgAdr.id}, null,
						function (data) {
							if (data.length > 1) {
								// We'll prepare a text query and let the user enter more details (etage/dør)
								// before triggering a new search

								// We'll try to help the user by setting the caret at the appropriate position for
								// entering etage and dør
								var textBefore = adgAdr.vejnavn + ' ' + adgAdr.husnr + ', ';
								var textAfter = ' ';
								if (adgAdr.supplerendebynavn) {
									textAfter += ', ' + adgAdr.supplerendebynavn;
								}
								if (adgAdr.postnr) {
									textAfter += ', ' + adgAdr.postnr;
								}
								if (adgAdr.postnrnavn) {
									textAfter += ' ' + adgAdr.postnrnavn;
								}
								element.val(textBefore + textAfter);
								element[0].selectionStart = element[0].selectionEnd = textBefore.length;

								// in addition to constructing a prebuilt query for the user to enter etage and dør,
								// we let the autocomplete widget perform a one-off query for adresser matching the
								// selected adgangsadresse
								autocompleteWidget.constrainedToAdgangsAdresseId = adgAdr.id;

								setTimeout(function () {
									element.autocomplete('search');
								});
							}
							else if (data.length === 1) {
								autocompleteWidget._trigger('select', null, data[0]);
								element.val(data[0].tekst);
							}
						});
				}
				else {
					autocompleteWidget._trigger('select', null, ui.item);
					element.val(ui.item.tekst);
				}
			}
		});
		element.autocomplete(autocompleteOptions).data("ui-autocomplete")._renderItem = function (ul, item) {
			return $("<li></li>")
				.append(item.tekst)
				.appendTo(ul);
		};
		element.on("autocompletefocus", function (event) {
			event.preventDefault();
		});
	}
});
