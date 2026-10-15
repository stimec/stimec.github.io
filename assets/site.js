/* Apartma Štimec – shared scripts. Text comes from window.SITE (set per language page). */
(function () {
  var S = window.SITE || {};
  var T = S.t || {};
  var booked = []; // [{start: Date, end: Date}] end exclusive (checkout day)

  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  /* ---------- Language: remember choice, suggest browser language on first visit ---------- */
  document.querySelectorAll('[data-setlang]').forEach(function (a) {
    a.addEventListener('click', function () { store('lang', a.getAttribute('data-setlang')); });
  });
  (function () {
    var hint = document.getElementById('lang-hint');
    if (!hint || store('lang') || store('langHintClosed')) return;
    var nav = (navigator.language || 'sl').slice(0, 2).toLowerCase();
    if (nav === S.lang || !S.hints || !S.hints[nav]) return;
    hint.querySelector('.hint-text').innerHTML = S.hints[nav];
    hint.classList.add('show');
    hint.querySelector('button').addEventListener('click', function () { hint.classList.remove('show'); store('langHintClosed', '1'); });
  })();

  /* ---------- Lightbox ---------- */
  var items = Array.prototype.slice.call(document.querySelectorAll('.gallery button'));
  var lb = document.getElementById('lightbox');
  var lbImg = lb && lb.querySelector('img');
  var lbCap = lb && lb.querySelector('.lb-cap');
  var idx = 0, lastFocus = null;
  function show(i) {
    idx = (i + items.length) % items.length;
    var b = items[idx];
    lbImg.src = b.getAttribute('data-full');
    lbImg.alt = b.querySelector('img').alt;
    lbCap.textContent = b.querySelector('img').alt + '  ·  ' + (idx + 1) + ' / ' + items.length;
  }
  function open(i) { lastFocus = document.activeElement; show(i); lb.classList.add('open'); document.body.style.overflow = 'hidden'; lb.querySelector('.lb-close').focus(); }
  function close() { lb.classList.remove('open'); document.body.style.overflow = ''; if (lastFocus) lastFocus.focus(); }
  if (lb) {
    items.forEach(function (b, i) { b.addEventListener('click', function () { open(i); }); });
    lb.querySelector('.lb-close').addEventListener('click', close);
    lb.querySelector('.lb-prev').addEventListener('click', function () { show(idx - 1); });
    lb.querySelector('.lb-next').addEventListener('click', function () { show(idx + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    document.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('open')) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(idx - 1);
      if (e.key === 'ArrowRight') show(idx + 1);
    });
    var x0 = null;
    lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 40) show(idx + (dx < 0 ? 1 : -1));
      x0 = null;
    });
  }

  /* ---------- Calendar ---------- */
  function parseDay(s) { var p = s.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]); }
  function iso(d) { return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0'); }

  document.addEventListener('DOMContentLoaded', function () {
    var el = document.getElementById('calendar');
    if (el && window.FullCalendar) {
      var cal = new FullCalendar.Calendar(el, {
        initialView: 'dayGridMonth',
        locale: S.fcLocale || 'en',
        firstDay: 1,
        height: 'auto',
        stickyHeaderDates: false,
        fixedWeekCount: false,
        showNonCurrentDates: false,
        headerToolbar: { left: 'prev', center: 'title', right: 'next' },
        events: '/availability.json',
        eventDisplay: 'background',
        selectable: true,
        selectOverlap: false,
        // day numbers are <a> without href; mark them as plain text for crawlers and screen readers
        dayCellDidMount: function (arg) { var n = arg.el.querySelector('a.fc-daygrid-day-number'); if (n) n.setAttribute('role', 'presentation'); },
        selectAllow: function (info) { var t = new Date(); t.setHours(0, 0, 0, 0); return info.start >= t; },
        select: function (info) {
          // Click or drag on free days fills the request form
          var arr = document.getElementById('f-arrival');
          var dep = document.getElementById('f-departure');
          var end = info.end;
          if ((end - info.start) / 864e5 < 2) { end = new Date(info.start); end.setDate(end.getDate() + 3); }
          arr.value = info.startStr;
          dep.value = iso(end);
          estimate();
          cal.unselect();
        }
      });
      cal.render();
    }
    fetch('/availability.json').then(function (r) { return r.json(); }).then(function (list) {
      booked = list.map(function (e) { return { start: parseDay(e.start), end: parseDay(e.end) }; });
      estimate();
    }).catch(function () {});
  });

  /* ---------- Price estimate ---------- */
  var P = S.prices || { high: 140, mid: 115, low: 90, cleaning: 40, taxAdult: 3.10, taxChild: 1.55 };
  function nightPrice(d) {
    var m = d.getMonth() + 1;
    if (m === 7 || m === 8) return P.high;
    if (m === 6 || m === 9) return P.mid;
    return P.low;
  }
  function eur(n) { return n.toLocaleString(S.numLocale || 'sl-SI', { style: 'currency', currency: 'EUR', minimumFractionDigits: n % 1 ? 2 : 0 }); }
  function val(id) { var e = document.getElementById(id); return e ? e.value : ''; }

  function estimate() {
    var box = document.getElementById('estimate');
    if (!box) return;
    var a = val('f-arrival'), d = val('f-departure');
    var adults = +val('f-adults') || 0, kids = +val('f-kids') || 0, small = +val('f-small') || 0;
    if (!a || !d) { box.innerHTML = T.estHint; return; }
    var start = parseDay(a), end = parseDay(d);
    var nights = Math.round((end - start) / 864e5);
    if (nights < 1) { box.innerHTML = '<span class="warn">' + T.estBadDates + '</span>'; return; }
    var room = 0, highNights = 0;
    for (var i = 0; i < nights; i++) {
      var n = new Date(start); n.setDate(n.getDate() + i);
      room += nightPrice(n);
      if (n.getMonth() === 6 || n.getMonth() === 7) highNights++;
    }
    var tax = nights * (adults * P.taxAdult + kids * P.taxChild);
    var total = room + P.cleaning + tax;
    var warn = [];
    var clash = booked.some(function (b) { return start < b.end && end > b.start; });
    if (clash) warn.push(T.estBooked);
    if (highNights && nights < 3) warn.push(T.estMin);
    else if (nights < 2) warn.push(T.estMin2);
    if (adults + kids + small > 4) warn.push(T.estMax);
    box.innerHTML =
      '<div class="d-flex justify-content-between"><span>' + nights + ' ' + (nights === 1 ? T.night : T.nights) + '</span><span>' + eur(room) + '</span></div>' +
      '<div class="d-flex justify-content-between"><span>' + T.cleaning + '</span><span>' + eur(P.cleaning) + '</span></div>' +
      '<div class="d-flex justify-content-between"><span>' + T.tax + '</span><span>' + eur(tax) + '</span></div>' +
      '<hr class="my-2"><div class="d-flex justify-content-between align-items-baseline"><span>' + T.total + '</span><span class="total">' + eur(total) + '</span></div>' +
      '<div class="small text-muted mt-1">' + T.estNote + '</div>' +
      (warn.length ? '<div class="warn mt-2">' + warn.join('<br>') + '</div>' : '');
    var hidden = document.getElementById('f-estimate');
    if (hidden) hidden.value = nights + ' nights, approx. ' + total.toFixed(2) + ' EUR';
  }
  ['f-arrival', 'f-departure', 'f-adults', 'f-kids', 'f-small'].forEach(function (id) {
    var e = document.getElementById(id);
    if (e) { e.addEventListener('change', estimate); e.addEventListener('input', estimate); }
  });
  var arrEl = document.getElementById('f-arrival');
  if (arrEl) {
    var today = iso(new Date());
    arrEl.min = today;
    arrEl.addEventListener('change', function () {
      var dep = document.getElementById('f-departure');
      dep.min = arrEl.value;
      if (!dep.value || dep.value <= arrEl.value) { var x = parseDay(arrEl.value); x.setDate(x.getDate() + 3); dep.value = iso(x); }
      estimate();
    });
  }
  estimate();

  /* ---------- Form submit (Formspree, stays on page) ---------- */
  var form = document.getElementById('request-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var status = document.getElementById('form-status');
      var btn = form.querySelector('button[type=submit]');
      btn.disabled = true;
      fetch(form.action, { method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' } })
        .then(function (r) {
          if (!r.ok) throw new Error();
          status.className = 'form-status ok'; status.textContent = T.sent; form.reset(); estimate();
          if (window.gtag) gtag('event', 'generate_lead', { method: 'form' });
        })
        .catch(function () { status.className = 'form-status err'; status.textContent = T.failed; })
        .finally(function () { btn.disabled = false; });
    });
  }

  /* ---------- Count WhatsApp / phone clicks (only if analytics accepted) ---------- */
  document.querySelectorAll('a[href^="https://wa.me"], a[href^="tel:"]').forEach(function (a) {
    a.addEventListener('click', function () { if (window.gtag) gtag('event', 'contact', { method: a.href.indexOf('wa.me') > -1 ? 'whatsapp' : 'phone' }); });
  });

  /* ---------- Cookie consent: Google Analytics loads only after "Accept" ---------- */
  function loadGA() {
    if (!S.gaId || window.gtag) return;
    var s = document.createElement('script');
    s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=' + S.gaId;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { dataLayer.push(arguments); };
    gtag('js', new Date()); gtag('config', S.gaId, { anonymize_ip: true });
  }
  var banner = document.getElementById('cookie-banner');
  var consent = store('cookieConsent');
  if (consent === 'yes') loadGA();
  else if (!consent && banner) {
    banner.classList.add('show');
    banner.querySelector('.cb-yes').addEventListener('click', function () { store('cookieConsent', 'yes'); banner.classList.remove('show'); loadGA(); });
    banner.querySelector('.cb-no').addEventListener('click', function () { store('cookieConsent', 'no'); banner.classList.remove('show'); });
  }
})();
