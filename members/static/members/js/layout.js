function showInputFields(id) {
    if (screen.width < 600 || window.innerWidth < 600) {
        document.getElementById(id).style.display == "block" ? document.getElementById(id).style.display = "none" : document.getElementById(id).style.display = "block";
        console.log(document.getElementById(id).style.display);
    }
}