// Sets data-label attribute on tables
document.addEventListener("DOMContentLoaded", function(event) {
  for (var table of Array.from(document.getElementsByTagName("table"))) {
    headers = Array.from(table.getElementsByTagName("th")).map(
      elemnt => elemnt.textContent
    );
    const rows = table
      .getElementsByTagName("tbody")
      .item(0)
      .getElementsByTagName("tr");
    for (var row of rows) {
      Array.from(row.children).map((cell, i) =>
        cell.setAttribute("data-label", headers[i])
      );
    }
  }
});
