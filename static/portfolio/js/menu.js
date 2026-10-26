// The only script on the site: close the mobile menu (<details>) after a
// link is tapped or Esc is pressed. Without it the menu still works, it just
// stays open until tapped again.
(function () {
  "use strict";
  var menu = document.querySelector(".menu");
  if (!menu) return;
  menu.addEventListener("click", function (e) {
    if (e.target.closest("a")) menu.open = false;
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && menu.open) {
      menu.open = false;
      menu.querySelector("summary").focus();
    }
  });
  document.addEventListener("click", function (e) {
    if (menu.open && !menu.contains(e.target)) menu.open = false;
  });
})();
