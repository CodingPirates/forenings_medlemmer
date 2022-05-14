const base_url = window.location.href
  .split("/")
  .slice(0, 3)
  .join("/");

var map;
var markers = {};

let department_request = fetch(`${base_url}/graphql`, {
  method: "POST",
  headers: {
    "content-type": "application/json"
  },
  body: '{"query":"{ departments {id isVisible address { longitude latitude }}}"}'
})
  .then(res => res.json())
  .then(res => {
    return res.data["departments"];
  })
  .catch(err => {
    console.log(err); // TODO: error handling
  });

document.addEventListener("DOMContentLoaded", event => {
  const southWest = L.latLng(54.77534585936447, 4.94384765625);
  const northEast = L.latLng(57.83890342754204, 16.962890625000004);
  map = L.map("map").fitBounds([southWest, northEast]);
  L.tileLayer(
    "https://api.mapbox.com/styles/v1/codingpirates/cjdaaa7yt3qts2rrwzpsx5ysw/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiY29kaW5ncGlyYXRlcyIsImEiOiJjamRhN3JtZHgxamphMzNvMHpraTJra2J1In0.lVqzzzCf9gHneicqDONuaw",
    {
      attribution:
        'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
      maxZoom: 18,
      accessToken:
        "pk.eyJ1IjoiY29kaW5ncGlyYXRlcyIsImEiOiJjamRhOXM1ZGIwdm04MnlvMnQ5dDBsdWpkIn0.NMaydnMG6m8OBpJhUbNgzg"
    }
  ).addTo(map);

  department_request.then(departments => {
    departments.map(department => addToMap(department))
  });
});

function focusOnMap(id) {
  map.setView(markers["" + id]._latlng, 12);
}

function addToMap(department) {
  if (
    department.address.latitude === null ||
    department.address.latitude === null ||
    department.isVisible == false
  ) {
    return;
  }
  let marker = L.marker([
    department.address.latitude,
    department.address.longitude
  ]).addTo(map);
  markers[department.id] = marker;
  let departmentHTML = document
    .getElementById(`department-${department.id}`)
    .cloneNode(true);
  departmentHTML.classList.add("department-map-box");
  marker.bindPopup(departmentHTML);
}
