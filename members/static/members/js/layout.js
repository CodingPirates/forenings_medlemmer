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