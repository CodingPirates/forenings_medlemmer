$(function() {
    $(".datepicker").datepicker({
        format: "dd-mm-yyyy",
        autoclose: true,
        weekStart: 1,
        language: 'da'
    });
    $('#id_search_address').dawaautocomplete({
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
        }
    });
    $("#id_manual_entry").click(function() {
        $("#id_streetname").val('');
        $("#id_housenumber").val('');
        $("#id_floor").val('');
        $("#id_door").val('');
        $("#id_placename").val('');
        $("#id_zipcode").val('');
        $("#id_city").val('');
        $("#id_dawa_id").val(null);
        $("#id_search_address").val(null);

        var checked = $("#id_manual_entry").get(0).checked;
        $("#id_streetname").attr("readonly", !checked);
        $("#id_housenumber").attr("readonly", !checked);
        $("#id_floor").attr("readonly", !checked);
        $("#id_door").attr("readonly", !checked);
        $("#id_placename").attr("readonly", !checked);
        $("#id_zipcode").attr("readonly", !checked);
        $("#id_city").attr("readonly", !checked);
        $("#id_search_address").attr("readonly", checked);
    });
});
