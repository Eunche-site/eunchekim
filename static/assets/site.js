(function () {
  var root = document.documentElement;

  // ---- Language (EN / KO). Menu and most pages stay English; Biography & Concerts switch. ----
  function setLang(lang) {
    root.setAttribute("data-lang", lang);
    try { localStorage.setItem("lang", lang); } catch (e) {}
    document.querySelectorAll(".lang-switch button").forEach(function (b) {
      b.setAttribute("aria-pressed", String(b.dataset.lang === lang));
    });
  }
  document.querySelectorAll(".lang-switch button").forEach(function (b) {
    b.addEventListener("click", function () { setLang(b.dataset.lang); });
  });
  setLang(root.getAttribute("data-lang") || "en");

  // ---- Mobile menu ----
  var toggle = document.querySelector(".menu-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("menu-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  // ---- Concerts: drop dates that passed since the site was last built ----
  var list = document.querySelector(".concert-list");
  if (list) {
    var d = new Date();
    var today = d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
    list.querySelectorAll(".concert").forEach(function (li) {
      if (li.dataset.date < today) li.remove();
    });
    if (!list.querySelector(".concert")) {
      list.hidden = true;
      document.querySelector(".concert-empty").hidden = false;
    }
  }

  // ---- Media: load YouTube player only when clicked ----
  document.querySelectorAll(".video-frame button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var iframe = document.createElement("iframe");
      iframe.src = "https://www.youtube-nocookie.com/embed/" + btn.dataset.id + "?autoplay=1&rel=0";
      iframe.title = btn.getAttribute("aria-label");
      iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      iframe.allowFullscreen = true;
      btn.replaceWith(iframe);
    });
  });

  // ---- Media: photo lightbox ----
  var lb = document.querySelector(".lightbox");
  if (lb) {
    var photos = Array.prototype.slice.call(document.querySelectorAll(".photo-grid button"));
    var lbImg = lb.querySelector("img");
    var lbCredit = lb.querySelector(".credit");
    var current = 0;
    function show(i) {
      current = (i + photos.length) % photos.length;
      var b = photos[current];
      lbImg.src = b.dataset.full;
      lbImg.alt = b.querySelector("img").alt;
      lbCredit.textContent = b.dataset.credit || "";
    }
    function close() { lb.classList.remove("open"); document.body.style.overflow = ""; photos[current].focus(); }
    photos.forEach(function (b, i) {
      b.addEventListener("click", function () {
        show(i);
        lb.classList.add("open");
        document.body.style.overflow = "hidden";
        lb.querySelector(".lb-close").focus();
      });
    });
    lb.querySelector(".lb-close").addEventListener("click", close);
    lb.querySelector(".lb-prev").addEventListener("click", function () { show(current - 1); });
    lb.querySelector(".lb-next").addEventListener("click", function () { show(current + 1); });
    lb.addEventListener("click", function (e) { if (e.target === lb) close(); });
    document.addEventListener("keydown", function (e) {
      if (!lb.classList.contains("open")) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(current - 1);
      if (e.key === "ArrowRight") show(current + 1);
    });
  }

  // ---- Contact form (sent via FormSubmit to the address in the form action) ----
  var form = document.querySelector(".contact-form");
  if (form) {
    var status = form.querySelector(".form-status");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = form.querySelector(".btn");
      btn.disabled = true;
      status.textContent = "Sending…";
      fetch(form.action.replace("formsubmit.co/", "formsubmit.co/ajax/"), {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(form)
      })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok || j.success === "false") throw j; }); })
        .then(function () { form.reset(); status.textContent = "Thank you — your message has been sent."; })
        .catch(function () { status.textContent = "Sorry, something went wrong. Please email directly at infoeunchekim@gmail.com."; })
        .finally(function () { btn.disabled = false; });
    });
  }
})();
