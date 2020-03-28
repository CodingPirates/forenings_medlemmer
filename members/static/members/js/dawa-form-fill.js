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
