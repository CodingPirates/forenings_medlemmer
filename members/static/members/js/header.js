const toogle = document.getElementById("toggle");
const parent = toogle.parentElement;
let isDesktop = () => window.getComputedStyle(toggle).display == "none";

function toggleNav() {
  for (var child of parent.children) {
    if (child !== toggle) {
      if (isDesktop()) {
        child.classList.remove("inactive");
      } else {
        child.classList.toggle("inactive");
      }
    }
  }
}
toggleNav(); // If desktop show

function resizeNav() {
  for (var child of parent.children) {
    if (isDesktop()) {
      child.classList.remove("inactive");
    } else {
      child.classList.add("inactive");
    }
  }
}

let body = document.getElementsByTagName("BODY")[0];
window.addEventListener("resize", resizeNav);
