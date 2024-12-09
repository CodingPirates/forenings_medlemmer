$(function() {
    $(".datepicker").datepicker({
        format: "dd-mm-yyyy",
        autoclose: true,
        weekStart: 1,
        language: 'da'
    });
    $('#search-address').dawaautocomplete({
        select: function(event, adresse) {
            // denne funktion bliver kaldt når brugeren vælger en adresse.
            // Udfyld adressefelterne
            $("#id_streetname").val(adresse.adresse.vejnavn);
            $("#id_housenumber").val(adresse.adresse.husnr);
            $("#id_floor").val(adresse.adresse.etage);
            $("#id_door").val(adresse.adresse.dør);
            $("#id_placename").val(adresse.adresse.supplerendebynavn);
            $("#id_zipcode").val(adresse.adresse.postnr);
            $("#id_city").val(adresse.adresse.postnrnavn);
            $("#id_dawa_id").val(adresse.adresse.id);
            console.log("A")
        }
    });
    $("#manual-entry").click(function() {
        $("#id_streetname").val('');
        $("#id_housenumber").val('');
        $("#id_floor").val('');
        $("#id_door").val('');
        $("#id_placename").val('');
        $("#id_zipcode").val('');
        $("#id_city").val('');
        $("#id_dawa_id").val(null);
        $("#search-address").val(null);

        var checked = $("#manual-entry").get(0).checked;
        $(".autofilled-address").attr("readonly", !checked);
        $("#search-address").attr("readonly", checked);
    });
});
$(function() {
    console.log("Initializing DAWA autocomplete...");
    $('#id_search_address').dawaautocomplete({
        minLength: 2,
        delay: 300,
        source: function(request, response) {
            $.ajax({
                url: "https://dawa.aws.dk/adresser/autocomplete",
                dataType: "json",
                data: {
                    q: request.term
                },
                success: function(data) {
                    response($.map(data, function(item) {
                        return {
                            label: item.tekst,
                            value: item.tekst,
                            adresse: item.adresse
                        };
                    }));
                }
            });
        },

        select: function(event, ui) {
            console.log("Selected ui:", ui)
            console.log("Selected item:", ui.item)
            var adresse = ui.adresse;
            console.log("Selected address object", adresse)
            if (adresse) {
                // denne funktion bliver kaldt når brugeren vælger en adresse.
                // Udfyld adressefelterne
                /*
                console.log("  by:" + adresse.postnrnavn)
                $("#id_streetname").val(adresse.vejnavn);
                $("#id_housenumber").val(adresse.husnr);
                $("#id_floor").val(adresse.etage);
                $("#id_door").val(adresse.dør);
                $("#id_placename").val(adresse.supplerendebynavn);
                $("#id_zipcode").val(adresse.postnr);
                $("#id_city").val(adresse.postnrnavn);
                $("#id_dawa_id").val(adresse.id);
                $("#id_municipality").val(adresse.kommunenavn);
                $("#id_region").val(adresse.regionsnavn);*/
                // Perform an additional lookup to get complete address details
                // + "?format=geojson"
                $.ajax({
                    url: "https://api.dataforsyningen.dk/adresser/" + adresse.id ,
                    dataType: "json",
                    success: function(data) {
                        console.log("Complete address details:", data);
                        adgangsadresse = data.properties;
                        $("#id_streetname").val(adgangsadresse.vejnavn);
                        $("#id_housenumber").val(adgangsadresse.husnr);
                        $("#id_floor").val(data.etage);
                        $("#id_door").val(data.dør);
                        $("#id_placename").val(adgangsadresse.supplerendebynavn);
                        $("#id_zipcode").val(adgangsadresse.postnummer.nr);
                        $("#id_city").val(adgangsadresse.postnummer.navn);
                        $("#id_dawa_id").val(data.id);
                        $("#id_municipality").val(adgangsadresse.kommune.navn);
                        $("#id_region").val(adgangsadresse.region.navn);
                    },
                    error: function(xhr, status, error) {
                        console.error("Error fetching complete address details:", status, error);
                    }
                });
            } else {
                console.error("Unexpected address structure:", ui.item);


            }
        }
    });

    function toggleReadonlyFields(isManual) {
        var fields = $('#id_streetname, #id_housenumber, #id_floor, #id_door, #id_placename, #id_zipcode, #id_city, #id_region, #id_municipality');
        fields.prop('readonly', !isManual);
        fields.toggleClass('readonly-field', !isManual);
        $('#id_search_address').prop('readonly', isManual);
        $('#id_search_address').toggleClass('readonly-field', isManual);
        console.log("Fields readonly state updated.");
    }

    $('#id_manual_entry').change(function() {
        var isManual = $(this).is(':checked');
        console.log("Manual entry checkbox changed:", isManual);
        toggleReadonlyFields(isManual);
    }).change(); // Trigger change event on page load to set initial state

    // Initial state check
    var isManual = $('#id_manual_entry').is(':checked');
    console.log("Initial manual entry checkbox state:", isManual);
    toggleReadonlyFields(isManual);
    console.log("Initial fields readonly state set.");

});
