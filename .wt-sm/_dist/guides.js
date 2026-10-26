/* guides.js — search, category filters and Show more for /guides/.
   ============================================================================
   DESIGN CONSTRAINTS, all of them deliberate:

   PROGRESSIVE ENHANCEMENT. The cards are server-rendered and already in the
   document. This file only ADDS controls. Without JavaScript the visitor and
   the crawler both get the complete list, unfiltered, with no dead buttons —
   the toolbar ships with `hidden` and is revealed here. Nothing below can
   hide an article from a search engine, and no guide URL changes.

   NO SEARCH SERVICE. Matching runs against a `data-terms` attribute the
   generator writes onto each card from the title, category, blurb, the
   article's own h1, its intent and its slug. At 100 guides this is a hundred
   substring tests on a keystroke — far below the threshold where anyone
   would feel it, and it costs no request, no key and no third party.

   NO ANIMATION. Cards are shown or hidden. A library that fades and reflows
   on every keystroke feels busy, and this site is meant to feel calm.

   NOTHING IS MAINTAINED BY HAND. Categories, counts and terms all come from
   the generator, so the 6 AM routine's new guide appears in search and under
   its chip with nobody editing this file. */
(function () {
  "use strict";

  var tools = document.getElementById("libTools");
  var list = document.querySelector(".topics");
  if (!tools || !list) return;

  var cards = Array.prototype.slice.call(list.querySelectorAll(".topic"));
  var input = document.getElementById("libQ");
  var count = document.getElementById("libCount");
  var moreBtn = document.getElementById("libMore");
  var chips = Array.prototype.slice.call(tools.querySelectorAll(".chip"));

  /* How many to show before "Show more". Ten guides fit comfortably; the
     cap only starts doing work once the library outgrows one screen. */
  var PAGE = 9;

  var activeCat = "";
  var query = "";
  /* How many matching guides are currently revealed. Show more adds one
     PAGE at a time rather than dumping the remainder: at 100 guides the old
     behaviour turned one click into a 91-card wall, which is the thing the
     cap existed to prevent. Any change to the search or the filter resets
     this to one page, because the result set underneath it has changed. */
  var limit = PAGE;

  function matches(card) {
    if (activeCat && card.getAttribute("data-cat") !== activeCat) return false;
    if (!query) return true;
    var terms = card.getAttribute("data-terms") || "";
    /* Every word the visitor typed must appear. "medicaid house" finds the
       estate-recovery guide; it does not return everything about Medicaid. */
    var words = query.split(/\s+/);
    for (var i = 0; i < words.length; i++) {
      if (words[i] && terms.indexOf(words[i]) === -1) return false;
    }
    return true;
  }

  function render() {
    var shown = 0;
    var hits = 0;
    for (var i = 0; i < cards.length; i++) {
      var ok = matches(cards[i]);
      if (ok) hits++;
      var visible = ok && shown < limit;
      if (visible) shown++;
      cards[i].hidden = !visible;
    }

    var hidden = hits - shown;
    if (hidden > 0) {
      var next = Math.min(PAGE, hidden);
      moreBtn.hidden = false;
      moreBtn.textContent = "Show " + next + " more guide" + (next === 1 ? "" : "s");
      /* The button's accessible name says what is left overall, so a screen
         reader user knows how deep the list still goes, not just the size of
         the next step. */
      moreBtn.setAttribute("aria-label",
        "Show " + next + " more guide" + (next === 1 ? "" : "s") +
        ". " + hidden + " of " + hits + " still hidden.");
    } else {
      moreBtn.hidden = true;
      moreBtn.removeAttribute("aria-label");
    }

    if (hits === 0) {
      count.textContent = query
        ? "No guides match “" + query + "”. Try a shorter word, or clear the filters."
        : "No guides in this category yet.";
    } else if (query || activeCat) {
      count.textContent = "Showing " + shown + " of " + hits +
        " matching guide" + (hits === 1 ? "" : "s") +
        " — " + cards.length + " in total.";
    } else {
      count.textContent = "Showing " + shown + " of " + cards.length + " guides.";
    }
  }

  input.addEventListener("input", function () {
    query = input.value.trim().toLowerCase().replace(/[^a-z0-9 ]+/g, " ").trim();
    limit = PAGE;   /* a new search starts from the top of the results */
    render();
  });

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      activeCat = chip.getAttribute("data-cat") || "";
      limit = PAGE;
      chips.forEach(function (c) {
        var on = c === chip;
        c.classList.toggle("chip--on", on);
        c.setAttribute("aria-pressed", on ? "true" : "false");
      });
      render();
    });
    chip.setAttribute("aria-pressed",
      chip.classList.contains("chip--on") ? "true" : "false");
  });

  moreBtn.addEventListener("click", function () {
    /* Remember where the button was, reveal, then put focus on the first
       newly-shown card's link. A keyboard user who presses Show more should
       land on the new content, not at the top of the page. */
    var firstNew = null;
    for (var i = 0; i < cards.length; i++) {
      if (cards[i].hidden && matches(cards[i])) { firstNew = cards[i]; break; }
    }
    limit += PAGE;
    render();
    if (firstNew) {
      var link = firstNew.querySelector("a");
      if (link) link.focus({ preventScroll: true });
    }
  });

  tools.hidden = false;
  render();
}());
