var adressevaelger = (() => {
  var o = Object.defineProperty;
  var d = Object.getOwnPropertyDescriptor;
  var u = Object.getOwnPropertyNames;
  var p = Object.prototype.hasOwnProperty;
  var a = (r, e) => o(r, "name", { value: e, configurable: !0 });
  var E = (r, e) => {
      for (var t in e) o(r, t, { get: e[t], enumerable: !0 });
    },
    f = (r, e, t, s) => {
      if ((e && typeof e == "object") || typeof e == "function")
        for (let i of u(e))
          !p.call(r, i) &&
            i !== t &&
            o(r, i, {
              get: () => e[i],
              enumerable: !(s = d(e, i)) || s.enumerable,
            });
      return r;
    };
  var b = (r) => f(o({}, "__esModule", { value: !0 }), r);
  var y = {};
  E(y, {
    AdresseSearchAPI: () => n,
    AdresseSearchInput: () => h,
    adressevaelger: () => c,
    default: () => k,
  });
  var n = class {
    static {
      a(this, "AdresseSearchAPI");
    }
    apiUrl = "https://adressevaelger.dk";
    token = "";
    constructor(e) {
      if (!e || !e.token)
        throw new Error(
          'AdresseSearchAPI must be initialized with a valid configuration. `{token: "xxx"} is the minimum required.`',
        );
      ((this.token = e.token), e.apiUrl && (this.apiUrl = e.apiUrl));
    }
    async search(e, t, s = {}) {
      if (!e || !t)
        throw new Error(
          "search() requires both endpoint and query parameters.",
        );
      let i = await fetch(
        `${this.apiUrl}/${e}/soeg?tekst=${t}&token=${this.token}${this.formatParams(s)}`,
      );
      if (!i.ok) throw new Error(`HTTP error! Status: ${i.status}`);
      let l = await i.json();
      if (l.status === "fejl")
        throw new Error(`Search error: ${l.beskrivelse}`);
      return l.fund;
    }
    async get(e, t) {
      if (!e || !t)
        throw new Error("get() requires both endpoint and id parameters.");
      let s = await fetch(`${this.apiUrl}/${e}/${t}?token=${this.token}`);
      if (!s.ok) throw new Error(`HTTP error! status: ${s.status}`);
      let i = await s.json();
      if (i.status === "fejl") throw new Error(i.beskrivelse);
      return i;
    }
    formatParams(e) {
      let t = "";
      return (
        e.medtagForeloebige && (t += "&medtagForeloebige=true"),
        e.maksimum && (t += `&maksimum=${e.maksimum}`),
        e.kommuneKode && (t += `&kommuneKode=${e.kommuneKode}`),
        e.vejnavn && (t += `&vejnavn=${e.vejnavn}`),
        e.postnummer && (t += `&postnummer=${e.postnummer}`),
        t
      );
    }
  };
  function c(r, e) {
    let t = new m(r, e);
  }
  a(c, "adressevaelger");
  var m = class {
    static {
      a(this, "AdresseSearchUI");
    }
    searchType = "adresser";
    debounceTimer;
    options;
    wrapperElement;
    inputElement;
    listElement;
    api;
    constructor(e, t) {
      ((this.options = t),
        (this.searchType = t.adgangsadresserOnly ? "husnumre" : "adresser"),
        (this.inputElement = e),
        (this.listElement = document.createElement("div")),
        (this.wrapperElement = this.inputElement.parentNode),
        this.wrapperElement.append(this.listElement),
        this.inputElement.addEventListener(
          "input",
          this.inputHandler.bind(this),
        ),
        this.wrapperElement.addEventListener(
          "keyup",
          this.listKeyHandler.bind(this),
        ),
        document.addEventListener(
          "click",
          this.outsideClickHandler.bind(this),
        ));
      let s = this.options.apiUrl
        ? { token: t.token, apiUrl: this.options.apiUrl }
        : { token: t.token };
      this.api = new n(s);
    }
    inputHandler(e) {
      e.target.value !== "" &&
        (this.debounceTimer && clearTimeout(this.debounceTimer),
        (this.debounceTimer = setTimeout(async () => {
          await this.refreshList(e.target.value);
        }, 500)));
    }
    async refreshList(e) {
      try {
        let t = await this.api.search(this.searchType, e, this.options);
        this.renderDOMList(this.listElement, t);
      } catch (t) {
        this.errorHandler(
          new Error(`Failed to load search items: ${t.message}`),
        );
      }
    }
    renderDOMList(e, t) {
      let s = document.createElement("ul");
      ((s.className = "adressevaelger-suggestions"),
        (s.role = "listbox"),
        (s.ariaLabel = "S\xF8geresultater"),
        t.forEach((i) => {
          this.renderDOMListItem(s, i);
        }),
        e.querySelector("ul")?.remove(),
        e.append(s));
    }
    renderDOMListItem(e, t) {
      let s = document.createElement("li");
      ((s.className = "adressevaelger-suggestion"),
        (s.role = "option"),
        (s.tabIndex = 0),
        (s.dataset.item = JSON.stringify(t)),
        s.addEventListener("click", (i) => {
          this.selectProcessor(JSON.parse(i.target.dataset.item));
        }),
        (s.innerText = t.titel),
        e.append(s));
    }
    errorHandler(e) {
      (console.error(e),
        this.inputElement.dispatchEvent(
          new CustomEvent("address:error", {
            bubbles: !0,
            composed: !0,
            detail: { message: e.message },
          }),
        ));
    }
    listKeyHandler(e) {
      e.key === "ArrowDown"
        ? this.moveFocus(1)
        : e.key === "ArrowUp"
          ? this.moveFocus(-1)
          : e.key === "Enter" && this.listElement.querySelector(":focus")
            ? (this.inputElement.focus(),
              this.selectProcessor(JSON.parse(e.target.dataset.item)))
            : e.key === "Escape" &&
              (this.inputElement.focus(),
              this.listElement.querySelector("ul")?.remove());
    }
    outsideClickHandler(e) {
      this.wrapperElement.contains(e.target) ||
        this.listElement.querySelector("ul")?.remove();
    }
    moveFocus(e) {
      if (!this.listElement.querySelector("ul")) return;
      let t = this.listElement.querySelector(":focus")?.nextElementSibling,
        s = this.listElement.querySelector(":focus")?.previousElementSibling,
        i = this.listElement.querySelector("li");
      (this.listElement.querySelectorAll("li").forEach((l) => {
        l.classList.remove("dawa-selected");
      }),
        e === 1 && !t && !s
          ? i.focus()
          : e === -1 && !s
            ? this.inputElement.focus()
            : e === 1 && t
              ? t.focus()
              : e === -1 && s && s.focus(),
        this.listElement
          .querySelector(":focus")
          ?.classList.add("dawa-selected"));
    }
    selectProcessor(e) {
      e.type === "vejnavn" ||
      e.type === "navngivenvejpostnummer" ||
      (e.type === "husnummer" && this.searchType === "adresser")
        ? ((this.inputElement.value = e.titel), this.refreshList(e.titel))
        : (this.listElement.querySelector("ul")?.remove(), this.selectItem(e));
    }
    async selectItem(e) {
      try {
        let t = await this.api.get(this.searchType, e.id);
        ((this.inputElement.value = e.titel),
          this.inputElement.dispatchEvent(
            new CustomEvent("address:select", {
              bubbles: !0,
              composed: !0,
              detail: t,
            }),
          ),
          this.options.select(t));
      } catch (t) {
        this.errorHandler(new Error(`Failed to fetch items: ${t.message}`));
      }
    }
  };
  var h = class extends HTMLElement {
    static {
      a(this, "AdresseSearchInput");
    }
    static observedAttributes = [
      "placeholder",
      "disabled",
      "adgangsadresser-only",
      "kommune-kode",
      "maksimum",
      "medtag-foreloebige",
      "token",
      "api-url",
    ];
    elementId = `adr-${Math.ceil(Math.random() * 1e5)}`;
    disabled = !1;
    placeholder = "S\xF8g adresse";
    searchType = "adresser";
    options = { kommuneKode: null, maksimum: null, medtagForeloebige: null };
    debounceTimer;
    inputElement;
    listElement;
    api;
    token;
    style = `
    #${this.elementId} {
      --highlight-color: lightblue;
      max-width: 30rem;
      width: 100%;
      display: block;
    }
    #${this.elementId}-input {
      anchor-name: --input-${this.elementId};
      width: 100%;
      display: block;
    }
    #${this.elementId}-list {
      margin: 0;
      inset: auto;
      position-anchor: --input-${this.elementId};
      position: fixed;
      left: anchor(left);
      top: anchor(bottom);
      right: auto;

      position-try-fallbacks: flip-block;
      max-height: 50vh;
      overflow: auto;

      li {
        cursor: pointer;
      }
      li:hover {
        background-color: var(--highlight-color);
      }
    }
  `;
    constructor() {
      super();
    }
    connectedCallback() {
      ((this.id = this.elementId),
        this.attachStyle(this.style),
        this.renderList());
    }
    attributeChangedCallback(e, t, s) {
      switch (e) {
        case "token":
          this.token = s;
          break;
        case "adgangsadresser-only":
          this.searchType = "husnumre";
          break;
        case "placeholder":
          this.placeholder = s;
          break;
        case "kommune-kode":
          this.options.kommuneKode = s;
          break;
        case "maksimum":
          this.options.maksimum = Number(s);
          break;
        case "medtag-foreloebige":
          this.options.medtagForeloebige = s !== "false";
          break;
        case "api-url":
          this.options.apiUrl = s;
          break;
        default:
      }
      (e === "disabled" && s === "" && (this.disabled = !0),
        this.setAPI(),
        this.renderInput());
    }
    setAPI() {
      if (!this.token) return;
      let e = this.options.apiUrl
        ? { apiUrl: this.options.apiUrl, token: this.token }
        : { token: this.token };
      this.api = new n(e);
    }
    async selectHandler(e) {
      let t = JSON.parse(e.target.dataset.item);
      this.selectProcessor(t);
    }
    async selectProcessor(e) {
      e.type === "vejnavn" ||
      e.type === "navngivenvejpostnummer" ||
      (e.type === "husnummer" && this.searchType === "adresser")
        ? ((this.inputElement.value = e.titel), await this.refreshList(e.titel))
        : (await this.selectItem(e), this.listElement.hidePopover());
    }
    async selectItem(e) {
      try {
        let t = await this.api.get(this.searchType, e.id);
        ((this.inputElement.value = e.titel),
          this.dispatchEvent(
            new CustomEvent("address:select", {
              bubbles: !0,
              composed: !0,
              detail: t,
            }),
          ));
      } catch (t) {
        this.errorHandler(new Error(`Failed to fetch items: ${t.message}`));
      }
    }
    attachStyle() {
      let e = document.createElement("style");
      ((e.textContent = this.style), document.head.append(e));
    }
    renderInput() {
      (this.inputElement && this.inputElement.remove(),
        (this.inputElement = document.createElement("input")),
        (this.inputElement.id = `${this.elementId}-input`),
        (this.inputElement.type = "search"),
        (this.inputElement.role = "combobox"),
        (this.inputElement.ariaAutocomplete = "list"),
        (this.inputElement.ariaControls = `${this.elementId}-list`),
        (this.inputElement.placeholder = this.placeholder),
        (this.inputElement.disabled = this.disabled),
        this.inputElement.addEventListener(
          "input",
          this.inputHandler.bind(this),
        ),
        this.inputElement.addEventListener(
          "keyup",
          this.inputKeyHandler.bind(this),
        ),
        this.append(this.inputElement));
    }
    renderList() {
      ((this.listElement = document.createElement("ul")),
        (this.listElement.id = `${this.elementId}-list`),
        (this.listElement.popover = "auto"),
        (this.listElement.role = "listbox"),
        (this.listElement.ariaLabel = "S\xF8geresultater"),
        this.listElement.addEventListener(
          "keyup",
          this.listKeyHandler.bind(this),
        ),
        this.append(this.listElement));
    }
    renderListItems(e) {
      (this.listElement.hidePopover(),
        (this.listElement.innerHTML = ""),
        e.forEach((t) => {
          this.listElement.append(this.createListItem(t));
        }),
        this.listElement.showPopover());
    }
    createListItem(e) {
      let t = document.createElement("li");
      return (
        (t.tabIndex = 0),
        (t.role = "option"),
        (t.innerText = e.titel),
        (t.dataset.item = JSON.stringify(e)),
        t.addEventListener("click", this.selectHandler.bind(this)),
        t
      );
    }
    moveFocus(e) {
      let t = this.listElement.querySelector(":focus").nextElementSibling,
        s = this.listElement.querySelector(":focus").previousElementSibling;
      e === 1 && t ? t.focus() : e === -1 && s && s.focus();
    }
    async refreshList(e) {
      try {
        let t = await this.api.search(this.searchType, e, this.options);
        this.renderListItems(t);
      } catch (t) {
        this.errorHandler(
          new Error(`Failed to load search items: ${t.message}`),
        );
      }
    }
    inputHandler(e) {
      if (e.target.value === "") {
        this.listElement.hidePopover();
        return;
      }
      (this.debounceTimer && clearTimeout(this.debounceTimer),
        (this.debounceTimer = setTimeout(async () => {
          await this.refreshList(e.target.value);
        }, 300)));
    }
    inputKeyHandler(e) {
      e.key === "ArrowDown" && this.listElement.childNodes[0].focus();
    }
    listKeyHandler(e) {
      switch (e.key) {
        case "ArrowUp":
          this.moveFocus(-1);
          break;
        case "ArrowDown":
          this.moveFocus(1);
          break;
        case "Enter":
          (this.listElement.hidePopover(),
            this.selectProcessor(JSON.parse(e.target.dataset.item)));
          break;
        default:
      }
    }
    errorHandler(e) {
      (console.error(e),
        this.dispatchEvent(
          new CustomEvent("address:error", {
            bubbles: !0,
            composed: !0,
            detail: { message: e.message },
          }),
        ));
    }
  };
  var k = c;
  return b(y);
})();
