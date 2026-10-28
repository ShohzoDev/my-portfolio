// The only script on the site. Everything works without it; it adds:
// 1. the code window types itself out (the full code is in the HTML);
// 2. the header menu underlines the section you are reading;
// 3. the mobile menu closes after a tap or Esc.
(function () {
  "use strict";

  var calm = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------ typing */
  var code = document.querySelector("#code code");
  if (code && !calm) {
    var pre = code.parentNode;
    pre.style.minHeight = pre.offsetHeight + "px"; // no layout jump while typing
    var walker = document.createTreeWalker(code, NodeFilter.SHOW_TEXT);
    var nodes = [];
    while (walker.nextNode()) {
      // lines hidden on small screens keep their text and are simply skipped
      if (walker.currentNode.parentElement.getClientRects().length === 0) continue;
      nodes.push({ node: walker.currentNode, text: walker.currentNode.nodeValue });
    }
    nodes.forEach(function (n) { n.node.nodeValue = ""; });
    var caret = document.createElement("span");
    caret.className = "caret";
    caret.setAttribute("aria-hidden", "true");
    code.appendChild(caret);

    var i = 0, j = 0;
    (function type() {
      if (i >= nodes.length) { caret.classList.add("blink"); return; }
      var n = nodes[i];
      // whitespace (indentation) appears at once, characters one by one
      var step = /\s/.test(n.text.charAt(j)) ? n.text.slice(j).match(/^\s+/)[0].length : 1;
      j += step;
      n.node.nodeValue = n.text.slice(0, j);
      n.node.parentNode.insertBefore(caret, n.node.nextSibling);
      if (j >= n.text.length) { i += 1; j = 0; }
      setTimeout(type, step > 1 ? 30 : 12 + Math.random() * 22);
    })();
  }

  /* ---------------------------------------------------------- scrollspy */
  var links = Array.prototype.slice.call(document.querySelectorAll(".nav a"));
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
      var current = sections.filter(function (s) { return visible[s.id]; })[0];
      setActive(current ? current.id : "");
    }, { rootMargin: "-30% 0px -55% 0px" });
    sections.forEach(function (s) { observer.observe(s); });
    window.addEventListener("scroll", function () {
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) {
        setActive(sections[sections.length - 1].id);
      }
    }, { passive: true });
  }

  /* -------------------------------------------------------- mobile menu */
  var menu = document.querySelector(".menu");
  if (menu) {
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) menu.open = false; });
    document.addEventListener("click", function (e) { if (menu.open && !menu.contains(e.target)) menu.open = false; });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && menu.open) { menu.open = false; menu.querySelector("summary").focus(); }
    });
  }
})();
