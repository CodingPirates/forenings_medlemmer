// Sets listner on every tab section
document.addEventListener("DOMContentLoaded", function(event) {
  for (var tabs of Array.from(document.getElementsByClassName("tabs"))) {
    const tabButtons = Array.from(
      Array.from(tabs.children).filter(element => element.tagName === "UL")[0]
        .children
    );
    const sections = Array.from(
      Array.from(tabs.children).filter(element => element.tagName === "SECTION")
    );

    // Default to first as active
    toggleActive(sections, tabButtons, 0);

    for (var button of tabButtons) {
      button.addEventListener("click", event =>
        toggleActive(sections, tabButtons, tabButtons.indexOf(event.srcElement))
      );
    }
  }
});

function toggleActive(sections, buttons, activeIndex) {
  for (var button of buttons) {
    button.classList.remove("tab-active");
  }
  for (var section of sections) {
    section.hidden = true;
  }
  buttons[activeIndex].classList.add("tab-active");
  sections[activeIndex].hidden = false;
}
