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

    // Get the 'active tab' parameter value from the URL fragment (after #-character)
    const urlFragment = window.location.hash.substring(1); // Remove the '#' char

    // Default to the first list item as active if the ID is not provided or doesn't match any item
    const activeIndex = tabButtons.findIndex(button => button.id === urlFragment);
    const defaultIndex = activeIndex !== -1 ? activeIndex : 0;

    // Default to first as active
    toggleActive(sections, tabButtons, defaultIndex);

    for (var button of tabButtons) {
      button.addEventListener("click", event =>
        toggleActive(sections, tabButtons, tabButtons.indexOf(event.target))
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

  // set url to include the tab identifier. we overwrite url, since tabs doesn't work otherwise
  const newUrl = window.location.pathname + `#${buttons[activeIndex].id}`;
  window.history.replaceState({}, "", newUrl);
}
