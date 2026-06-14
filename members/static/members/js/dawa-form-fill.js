$(function () {
  $(".datepicker").datepicker({
    format: "dd-mm-yyyy",
    autoclose: true,
    weekStart: 1,
    language: "da",
  });

  const searchInput = document.getElementById("search-address");
  if (searchInput) {
    adressevaelger.adressevaelger(searchInput, {
      // KDS recommends "adressevaelger123" until proper user management is introduced
      // TODO December 2026: check if KDS has launched user management and replace this token
      token: "adressevaelger123",
      select: function (selected) {
        const adr = selected.adresse;
        $("#id_streetname").val(adr.husnummer.vejnavn);
        $("#id_housenumber").val(adr.husnummer.husnummertekst);
        $("#id_floor").val(adr.etagebetegnelse);
        $("#id_door").val(adr.doerbetegnelse);
        $("#id_placename").val(adr.husnummer.supplerendebynavn?.navn ?? "");
        $("#id_zipcode").val(adr.husnummer.postnummer.postnr);
        $("#id_city").val(adr.husnummer.postnummer.navn);
        $("#id_dawa_id").val(adr.id_lokalid);
      },
    });
  }

  $("#manual-entry").click(function () {
    $("#id_streetname").val("");
    $("#id_housenumber").val("");
    $("#id_floor").val("");
    $("#id_door").val("");
    $("#id_placename").val("");
    $("#id_zipcode").val("");
    $("#id_city").val("");
    $("#id_dawa_id").val(null);
    $("#search-address").val(null);

    var checked = $("#manual-entry").get(0).checked;
    $(".autofilled-address").attr("readonly", !checked);
    $("#search-address").attr("readonly", checked);
  });
});
