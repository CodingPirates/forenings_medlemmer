const base_url = window.location.href
  .split("/")
  .slice(0, 3)
  .join("/");

let unions = undefined;
fetch("http://localhost:8000/graphql", {
  method: "POST",
  headers: {
    "content-type": "application/json"
  },
  body: '{"query":"{ unions {\\n    id\\n    membershipPrice\\n  }\\n}"}'
})
  .then(res => res.json())
  .then(res => {
    unions = res.data["unions"];
  })
  .catch(err => {
    console.log(err);
  });

// Sets price according to selected union
document.addEventListener("DOMContentLoaded", event => {
  document.getElementById("id_union").addEventListener("change", event => {
    document.getElementById("price").innerText = unions.filter(
      union => union.id === event.target.value
    )[0]["membershipPrice"];
  });
});
