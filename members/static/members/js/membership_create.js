const base_url = window.location.href
  .split("/")
  .slice(0, 3)
  .join("/");

let unions = fetch(`${base_url}/graphql`, {
  method: "POST",
  headers: {
    "content-type": "application/json"
  },
  body: '{"query":"{ unions {id membershipPriceOre }}"}'
})
  .then(res => res.json())
  .then(res => {
    unions = res.data["unions"];
  })
  .catch(err => {
    console.log(err); // TODO: error handling
  });

// Sets price according to selected union
document.addEventListener("DOMContentLoaded", event => {
  document.getElementById("id_union").addEventListener("change", event => {
    document.getElementById("price").innerText = unions.filter(
      union => union.id === event.target.value
  )[0]["membershipPriceOre"] / 100;
  });
});
