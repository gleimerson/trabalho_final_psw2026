(function () {
  "use strict";
  function ready() {
    var spinner = document.getElementById("spinner");
    if (spinner) { spinner.classList.remove("show"); }
    if (window.WOW && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) { new WOW().init(); }
    if (window.jQuery) {
      var $ = window.jQuery;
      if ($.fn.owlCarousel) { $(".header-carousel, .testimonial-carousel").owlCarousel({items: 1, autoplay: true, smartSpeed: 1000, dots: true, loop: true}); }
      if ($.fn.counterUp && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) { $("[data-counter-up]").counterUp({delay: 10, time: 1000}); }
    }
    var top = document.querySelector(".back-to-top");
    if (top) { window.addEventListener("scroll", function () { top.style.display = window.scrollY > 300 ? "flex" : "none"; }); }
    document.querySelectorAll("img[data-fallback]").forEach(function (image) {
      image.addEventListener("error", function () { if (image.src !== image.dataset.fallback) image.src = image.dataset.fallback; }, {once: true});
    });
  }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", ready); } else { ready(); }
}());
