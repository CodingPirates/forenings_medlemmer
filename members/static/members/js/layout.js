function loadTables() {
    $(document).ready(function () {
        var tables = ["#waitingListTable"]
        for (var i = 0; i < tables.length; i++) {
            $(tables[i]).DataTable({
                "language": {
                    "decimal": "",
                    "emptyTable": "Ingen data tilgænglig",
                    "info": "Viser resultat _START_ til _END_ af ialt _TOTAL_ resultater",
                    "infoEmpty": "Viser 0 til 0 af 0 resultater",
                    "infoFiltered": "(filtered from _MAX_ total entries)",
                    "infoPostFix": "",
                    "thousands": ",",
                    "lengthMenu": "Vis _MENU_ resultater per side",
                    "loadingRecords": "Loader...",
                    "processing": "Arbejder...",
                    "search": "S&oslash;g:",
                    "searchPlaceholder": "fx København",
                    "zeroRecords": "Ingen resultater fundet",
                    "paginate": {
                        "first": "Første",
                        "last": "Sidste",
                        "next": "N&aelig;ste",
                        "previous": "Forrige"
                    },
                    "aria": {
                        "sortAscending": ": aktiver for at sortere kolonnen stigende",
                        "sortDescending": ": aktiver for at sortere kolonnen faldende"
                    }
                }
            });
        }
    });
}

function showInputFields(id) {
    if (screen.width < 600 || window.innerWidth < 600) {
        document.getElementById(id).style.display == "block" ? document.getElementById(id).style.display = "none" : document.getElementById(id).style.display = "block";
        console.log(document.getElementById(id).style.display);
    }
}

function switchView(pageId) {
    //if (document.getElementByClass("page").id
    var elements = document.getElementsByClassName("page");
    for (var i = 0; i < elements.length; i++) {
        elements[i].id == pageId ? elements[i].style.display = "block" : elements[i].style.display = "none";
    }
}

function doActive(element) {
    element.class += "active";
}