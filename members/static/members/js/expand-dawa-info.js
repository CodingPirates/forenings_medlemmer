$(document).ready(function() {
    // Expand the "Dawa info" section
    $("fieldset.module.collapse:contains('Dawa info')")
        .removeClass("collapsed")
        .addClass("expanded")
        .find("*")
        .css("display", "block");
});