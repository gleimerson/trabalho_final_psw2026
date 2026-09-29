(function () {
  "use strict";
  function ready() {
    var spinner = document.getElementById("spinner");
    if (spinner) { spinner.classList.remove("show"); }
    var top = document.querySelector(".back-to-top");
    if (top) { window.addEventListener("scroll", function () { top.style.display = window.scrollY > 300 ? "flex" : "none"; }); }
    document.querySelectorAll("img[data-fallback]").forEach(function (image) {
      image.addEventListener("error", function () { if (image.src !== image.dataset.fallback) image.src = image.dataset.fallback; }, {once: true});
    });
  }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", ready); } else { ready(); }
}());
