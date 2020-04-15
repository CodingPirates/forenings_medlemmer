// Sets data-label attribute on tables
document.addEventListener("DOMContentLoaded", function(event) {
  for (var tabs of Array.from(document.getElementsByClassName("tabs"))) {
    const tabButtons = Array.from(
      Array.from(tabs.children).filter(element => element.tagName === "UL")[0]
        .children
    );
    const sections = Array.from(
      Array.from(tabs.children).filter(element => element.tagName === "SECTION")
    );
    console.log(sections);
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
  // remove active from every button.
  for (var button of buttons) {
      // TODO use classlist 
    button.className = button.className
      .split(" ")
      .filter(className => className !== "tab-active")
      .join(" ");
  }
  for (var section of sections) {
    section.className = section.className
      .split(" ")
      .filter(className => className !== "tab-section-active")
      .join(" ");
  }

  buttons[activeIndex].className += " tab-active";
  sections[activeIndex].className += " tab-section-active";
}
