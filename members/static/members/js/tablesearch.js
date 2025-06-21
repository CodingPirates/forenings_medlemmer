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

function filter_label(textbox_name, label_class) {
  // This function will find labels with class label_class
  // and hide/show them based on the input text box with name textbox_name
  var input = document.getElementById(textbox_name);
  var filter = input.value.toUpperCase();
  var labels = document.getElementsByClassName(label_class);
  for (var i = 0; i < labels.length; i++) {
    var label = labels[i];
    var parent = label.closest("div"); // Adjust this selector to match the parent container of the checkbox and label
    if (label.textContent.toUpperCase().indexOf(filter) > -1) {
      parent.style.display = ""; // Show the parent container
    } else {
      parent.style.display = "none"; // Hide the parent container
    }
  }
}