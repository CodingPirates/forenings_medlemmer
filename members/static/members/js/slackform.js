function sendSlackDetails() {
  var form = new FormData(document.getElementById('slackform'));
  fetch("https://slackinvite.codingpirates.dk/invite", {
    "method": "POST",
    "headers": {
      "content-type": "multipart/form-data;"
    },
    "body": form
  })
  .then(response => {
    console.log(response);
  })
  .catch(err => {
    console.error(err);
  });
}
