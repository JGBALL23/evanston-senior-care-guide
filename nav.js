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
