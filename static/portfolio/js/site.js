// The only script on the site, and everything works without it:
// 1. the left-hand menu highlights the section you are reading;
// 2. on desktop a soft light follows the cursor.
(function () {
  "use strict";

  var links = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
  var sections = links
    .map(function (a) { return document.querySelector(a.getAttribute("href")); })
    .filter(Boolean);

  function setActive(id) {
    links.forEach(function (a) {
      var on = a.getAttribute("href") === "#" + id;
      a.classList.toggle("active", on);
      if (on) a.setAttribute("aria-current", "true");
      else a.removeAttribute("aria-current");
    });
  }

  if (sections.length && "IntersectionObserver" in window) {
    var visible = {};
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { visible[e.target.id] = e.isIntersecting; });
      // the first section (top to bottom) that is on screen wins
      var current = sections.filter(function (s) { return visible[s.id]; })[0];
      if (current) setActive(current.id);
    }, { rootMargin: "-25% 0px -55% 0px" });
    sections.forEach(function (s) { observer.observe(s); });
    setActive(sections[0].id);
    // the last section is short: at the very bottom of the page it wins
    window.addEventListener("scroll", function () {
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) {
        setActive(sections[sections.length - 1].id);
      }
    }, { passive: true });
  }

  var fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (fine && !calm) {
    var root = document.documentElement;
    window.addEventListener("pointermove", function (e) {
      root.style.setProperty("--spot-x", e.clientX + "px");
      root.style.setProperty("--spot-y", e.clientY + "px");
    }, { passive: true });
    root.classList.add("has-spotlight");
  }
})();
