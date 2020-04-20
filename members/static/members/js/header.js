const toogle = document.getElementById("toggle");
const parent = toogle.parentElement;
let isDesktop = () => window.getComputedStyle(toggle).display == "none";

function toggleNav() {
  for (var child of parent.children) {
    if (child !== toggle) {
      if (isDesktop()) {
        child.classList.add("active");
      } else {
        if (child.classList.contains("inactive")) {
          child.classList.remove("inactive");
          child.classList.add("active");
        } else {
          child.classList.remove("active");
          child.classList.add("inactive");
        }
      }
    }
  }
}
toggleNav(); // If desktop show

function resizeNav() {
  for (var child of parent.children) {
    if (isDesktop()) {
      child.classList.add("active");
    } else {
      child.classList.add("inactive");
    }
  }
}

let body = document.getElementsByTagName("BODY")[0];
window.addEventListener("resize", resizeNav);
