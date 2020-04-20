const toogle = document.getElementById("toggle");
const parent = toogle.parentElement;
let isDesktop = () => window.getComputedStyle(toggle).display == "none";


function toggleNav() {
  for (var child of parent.children) {
    if (child !== toggle) {
      if (isDesktop()) {
        child.className = "active";
      } else {
        child.className = child.className.includes("inactive")
          ? "active"
          : "inactive";
      }
    }
  }
}
toggleNav(); // If desktop show

function resizeNav() {
  for (var child of parent.children) {
    if (isDesktop()) {
      child.className = "active";
    } else {
      child.className = "inactive";
    }
  }
}

let body = document.getElementsByTagName("BODY")[0];
window.addEventListener("resize", resizeNav);
