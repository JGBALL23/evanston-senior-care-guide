/* ============================================================
   nav.js — the mobile menu
   Below 880px, styles.css hides every nav link except the CTA
   (".nav__links > a:not(.nav__cta) { display: none }"). On a phone
   that left a logo and a "Start" button, and no way to reach the
   articles at all. This restores them behind a visible Menu button.
   One file, loaded by the homepage AND every generated guide page,
   so the behaviour can never drift between them.
   ============================================================ */
(function () {
  "use strict";

  var toggle = document.getElementById("navToggle");
  var menu = document.getElementById("navMenu");
  if (!toggle || !menu) { return; }

  function setOpen(open) {
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
    if (open) {
      menu.removeAttribute("hidden");
    } else {
      menu.setAttribute("hidden", "");
    }
  }

  function isOpen() {
    return toggle.getAttribute("aria-expanded") === "true";
  }

  toggle.addEventListener("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    setOpen(!isOpen());
  });

  /* tapping a destination closes the menu before the page moves */
  menu.addEventListener("click", function (e) {
    var t = e.target;
    while (t && t !== menu) {
      if (t.tagName === "A") { setOpen(false); return; }
      t = t.parentNode;
    }
  });

  /* tapping anywhere else closes it */
  document.addEventListener("click", function (e) {
    if (!isOpen()) { return; }
    if (menu.contains(e.target) || toggle.contains(e.target)) { return; }
    setOpen(false);
  });

  /* Escape closes it and gives focus back, so a keyboard user is
     never stranded inside a panel they cannot see */
  document.addEventListener("keydown", function (e) {
    if ((e.key === "Escape" || e.keyCode === 27) && isOpen()) {
      setOpen(false);
      toggle.focus();
    }
  });

  /* rotating to landscape must not leave a phone menu open over a
     desktop layout */
  window.addEventListener("resize", function () {
    if (window.innerWidth > 880 && isOpen()) { setOpen(false); }
  });

  setOpen(false);
})();

/* ---------- THE CHANNEL SURVIVES A CLICK FROM A GUIDE ----------
   Guide pages load this file only, so they fire no beacon. A family
   who lands on a guide from a tagged link (a referral email, a post,
   or search) and taps "Ask about a tour here" reloads the homepage with
   no ref and a same-site referrer, and the landing, form and submission
   are all counted as "direct". This carries the SAME short, sanitised
   token app.js would compute (utm_source, else ref, else the external
   referrer's host name; never a path, query or anything personal) onto
   same-site links to the homepage and to other guides.
   Guide pages and the /assisted-living-evanston/ search landing page
   only: on the homepage "/#..." links are same-page jumps, and app.js
   handles its own /? links. A link that already carries a
   tag is left alone, and a broken href never breaks the click. */
(function () {
  "use strict";
  var LANDINGS = ["/guides/", "/assisted-living-evanston/"];
  function isLanding(p) {
    for (var i = 0; i < LANDINGS.length; i++) {
      if (p.indexOf(LANDINGS[i]) === 0) { return true; }
    }
    return false;
  }
  if (!isLanding(window.location.pathname)) { return; }

  function token() {
    try {
      var params = new URLSearchParams(window.location.search);
      var raw = params.get("utm_source") || params.get("ref") || "";
      if (!raw && document.referrer) {
        var host = new URL(document.referrer).hostname;
        if (host && host !== window.location.hostname) {
          raw = host.replace(/^www\./, "").split(".")[0];
        }
      }
      return String(raw).toLowerCase().replace(/[^a-z0-9-]/g, "").slice(0, 24);
    } catch (err) {
      return "";
    }
  }
  var SOURCE = token();
  if (!SOURCE || SOURCE === "direct") { return; }

  document.addEventListener("click", function (e) {
    var t = e.target;
    while (t && t.tagName !== "A") { t = t.parentNode; }
    if (!t) { return; }
    var href = t.getAttribute("href") || "";
    if (href.charAt(0) !== "/" || href.charAt(1) === "/") { return; }
    try {
      var url = new URL(href, window.location.origin);
      if (url.pathname !== "/" && !isLanding(url.pathname)) { return; }
      if (url.searchParams.has("ref") || url.searchParams.has("utm_source")) { return; }
      url.searchParams.set("ref", SOURCE);
      t.setAttribute("href", url.pathname + url.search + url.hash);
    } catch (err) { /* a broken href must never break the click */ }
  }, true);
})();
