function filter_rows_in_table(textbox_name, section_class, table_class ) {
  // This function will find filter data in input text box with name textbox_name
  // then find the section with class = section_class that is not hidden
  // and then hide/show the rows in the table with id table_id

  var show_row;
  var input = document.getElementById(textbox_name);
  var filter = input.value.toUpperCase();
  var section_visible = document.querySelectorAll('.' + section_class + ':not([hidden])')[0]
  if (section_visible) {
    var table = section_visible.getElementsByClassName(table_class)[0];
    var rows = table.getElementsByTagName("tr")
    for (var i = 0; i < rows.length; i++) {
      var cells = rows[i].querySelectorAll("td");
      if (filter == "") {
        show_row = true; // no filter -> show all rows
      } else {
        show_row = false;
      }
      for (var j = 0; j < cells.length; j++) {
        if (cells[j].textContent.toUpperCase().indexOf(filter) > -1) {
          show_row = true;
          break;
        }
      }
      if (show_row) {
        rows[i].style.display = "table-row";
      } else {
        rows[i].style.display = "none";
      }
    }
  }
}
