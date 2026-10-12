/* GLOBIS HR Consultancy — site behaviour. Everything degrades gracefully without JS. */
(function () {
  'use strict';
  var root = document.documentElement;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  /* ---------- theme ---------- */
  var btn = $('#themeBtn');
  if (btn) btn.addEventListener('click', function () {
    var next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
    root.setAttribute('data-theme', next); store('globis-theme', next);
  });

  /* ---------- nav ---------- */
  var nav = $('.nav');
  function onScroll() {
    var y = window.scrollY;
    if (nav) nav.classList.toggle('is-scrolled', y > 12);
    var dock = $('#dock'); if (dock) dock.classList.toggle('is-show', y > 480);
  }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();

  var burger = $('#burger');
  function setMenu(open) {
    document.body.classList.toggle('menu-open', open);
    if (burger) { burger.setAttribute('aria-expanded', open); burger.setAttribute('aria-label', open ? 'Close menu' : 'Open menu'); }
  }
  if (burger) burger.addEventListener('click', function () { setMenu(!document.body.classList.contains('menu-open')); });
  $$('.dd__btn').forEach(function (b) { b.addEventListener('click', function (e) { e.stopPropagation(); var d = b.parentNode, o = !d.classList.contains('open'); $$('.dd').forEach(function (x) { x.classList.remove('open'); x.firstElementChild.setAttribute('aria-expanded', 'false'); }); if (o) { d.classList.add('open'); b.setAttribute('aria-expanded', 'true'); } }); });
  document.addEventListener('click', function () { $$('.dd').forEach(function (x) { x.classList.remove('open'); }); });
  $$('.drawer a').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { setMenu(false); closeLightbox(); } });
  window.addEventListener('resize', function () { if (window.innerWidth >= 1240) setMenu(false); });

  /* ---------- flash messages ---------- */
  $$('.flash__item button').forEach(function (b) { b.addEventListener('click', function () { b.parentNode.remove(); }); });
  setTimeout(function () { $$('.flash__item:not(.is-error)').forEach(function (n) { n.style.transition = 'opacity .5s'; n.style.opacity = 0; setTimeout(function () { n.remove(); }, 500); }); }, 7000);

  /* ---------- reveal on scroll ---------- */
  var rv = $$('.rv');
  if ('IntersectionObserver' in window && rv.length) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: .08, rootMargin: '0px 0px -40px 0px' });
    rv.forEach(function (el, i) { el.style.setProperty('--d', ((i % 6) * 70) + 'ms'); io.observe(el); });
    // safety net: never leave content hidden
    setTimeout(function () { rv.forEach(function (el) { el.classList.add('in'); }); }, 4000);
  } else { rv.forEach(function (el) { el.classList.add('in'); }); }

  /* ---------- spotlight cards ---------- */
  document.addEventListener('pointermove', function (e) {
    var c = e.target.closest && e.target.closest('.card'); if (!c) return;
    var r = c.getBoundingClientRect();
    c.style.setProperty('--mx', (e.clientX - r.left) + 'px'); c.style.setProperty('--my', (e.clientY - r.top) + 'px');
  }, { passive: true });

  /* ---------- counters ---------- */
  var counters = $$('[data-count]');
  if (counters.length && 'IntersectionObserver' in window) {
    var co = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return; co.unobserve(e.target);
        var el = e.target, end = parseFloat(el.dataset.count), suf = el.dataset.suffix || '', t0 = null, dur = 1400;
        if (reduce) { el.textContent = end + suf; return; }
        (function step(t) { if (!t0) t0 = t; var p = Math.min((t - t0) / dur, 1), v = Math.round(end * (1 - Math.pow(1 - p, 3))); el.textContent = v + suf; if (p < 1) requestAnimationFrame(step); })(performance.now());
      });
    }, { threshold: .4 });
    counters.forEach(function (c) { co.observe(c); });
  }

  /* ---------- marquee: duplicate content for seamless loop ---------- */
  $$('.marquee__track').forEach(function (t) { t.innerHTML += t.innerHTML; });

  /* ---------- lightbox ---------- */
  var lb = $('#lightbox');
  function closeLightbox() { if (!lb) return; lb.classList.remove('is-open'); var m = $('.lightbox__media', lb); if (m) m.innerHTML = ''; }
  $$('[data-lightbox]').forEach(function (t) {
    t.addEventListener('click', function () {
      if (!lb) return;
      var m = $('.lightbox__media', lb), cap = $('.lightbox__cap', lb);
      m.innerHTML = '';
      if (t.dataset.video) { var v = document.createElement('video'); v.src = t.dataset.video; v.controls = true; v.autoplay = true; v.playsInline = true; if (t.dataset.poster) v.poster = t.dataset.poster; m.appendChild(v); }
      else { var i = document.createElement('img'); i.src = t.dataset.lightbox; i.alt = t.dataset.title || ''; m.appendChild(i); }
      cap.textContent = t.dataset.title || ''; lb.classList.add('is-open');
    });
  });
  if (lb) lb.addEventListener('click', function (e) { if (e.target === lb || e.target.classList.contains('lightbox__x')) closeLightbox(); });

  /* ---------- apply form ---------- */
  var form = $('#applyForm');
  if (form) {
    // guess country code from the visitor's locale/timezone
    var sel = $('#id_phone_country');
    var tzMap = { 'Africa/Kampala': 'UG', 'Africa/Nairobi': 'KE', 'Africa/Lagos': 'NG', 'Africa/Accra': 'GH', 'Africa/Dar_es_Salaam': 'TZ', 'Africa/Kigali': 'RW', 'Africa/Addis_Ababa': 'ET', 'Africa/Lusaka': 'ZM', 'Africa/Harare': 'ZW', 'Africa/Blantyre': 'MW', 'Africa/Douala': 'CM', 'Africa/Freetown': 'SL', 'Africa/Monrovia': 'LR', 'Africa/Dakar': 'SN', 'Africa/Cairo': 'EG', 'Asia/Kolkata': 'IN', 'Asia/Calcutta': 'IN', 'Asia/Karachi': 'PK', 'Asia/Dhaka': 'BD', 'Asia/Kathmandu': 'NP', 'Asia/Colombo': 'LK', 'Asia/Manila': 'PH', 'Asia/Dubai': 'AE', 'Africa/Juba': 'SS', 'Africa/Khartoum': 'SD', 'Africa/Bujumbura': 'BI' };
    if (sel && !form.dataset.hasPost) {
      try { var tz = Intl.DateTimeFormat().resolvedOptions().timeZone; if (tzMap[tz]) { sel.value = tzMap[tz]; var nat = $('#id_nationality'); if (nat && !nat.value && tz !== 'Asia/Dubai') { var name = sel.options[sel.selectedIndex].text.replace(/\s*\(.*$/, ''); for (var i = 0; i < nat.options.length; i++) if (nat.options[i].value === name) { nat.selectedIndex = i; break; } } } } catch (e) { }
    }
    // dial-code badge
    var dial = $('#dialBadge'), map = {};
    try { map = JSON.parse($('#dialMap').textContent); } catch (e) { }
    function upd() { if (dial && sel) dial.textContent = '+' + (map[sel.value] || ''); }
    if (sel) { sel.addEventListener('change', upd); upd(); }
    // phone: digits and spaces only
    var ph = $('#id_phone_number');
    if (ph) ph.addEventListener('input', function () { ph.value = ph.value.replace(/[^\d+\s-]/g, ''); });
    // file name
    var cv = $('#id_cv'), cvn = $('#cvName');
    if (cv && cvn) cv.addEventListener('change', function () {
      var f = cv.files[0]; if (!f) { cvn.textContent = 'Tap to attach your CV'; return; }
      if (f.size > 5 * 1024 * 1024) { alert('That file is larger than 5 MB. Please choose a smaller one.'); cv.value = ''; cvn.textContent = 'Tap to attach your CV'; return; }
      cvn.textContent = f.name;
    });
    // submit state + double-submit guard
    form.addEventListener('submit', function () {
      var b = $('button[type=submit]', form); if (!b || b.disabled) return;
      setTimeout(function () { b.disabled = true; b.innerHTML = '<span class="spin"></span> Sending your application…'; }, 0);
    });
    // open optional section when it contains an error
    var more = $('.more', form); if (more && $('.has-error', more)) more.open = true;
    var firstErr = $('.has-error input, .has-error select, .alert'); if (firstErr) firstErr.scrollIntoView({ block: 'center', behavior: reduce ? 'auto' : 'smooth' });
  }

  /* ---------- share on WhatsApp / native share ---------- */
  $$('[data-share]').forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.preventDefault(); e.stopPropagation();
      var url = location.origin + b.dataset.path, msg = b.dataset.text.replace(/\\n/g, '\n'), text = msg + '\n' + url;
      if (b.dataset.native === '1' && navigator.share) { navigator.share({ title: b.dataset.title, text: msg, url: url }).catch(function () { }); return; }
      window.open('https://wa.me/?text=' + encodeURIComponent(text), '_blank', 'noopener');
    });
  });
  var dock = document.getElementById('dock'); if (dock) document.body.classList.add('dock-on');

  /* ---------- globe ---------- */
  var cv2 = $('#globe');
  if (cv2 && cv2.getContext) initGlobe(cv2);

  function initGlobe(canvas) {
    var ctx = canvas.getContext('2d'), dpr = Math.min(window.devicePixelRatio || 1, 2), S = 0, R = 0, running = true, t0 = performance.now();
    var css = getComputedStyle(root);
    function col(n, fb) { return (css.getPropertyValue(n) || fb).trim() || fb; }
    var D = Math.PI / 180;
    var cities = [
      { n: 'Kampala', la: 0.35, lo: 32.58 }, { n: 'Mombasa', la: -4.04, lo: 39.67 }, { n: 'Lagos', la: 6.52, lo: 3.38 },
      { n: 'Accra', la: 5.6, lo: -0.19 }, { n: 'Addis', la: 9.03, lo: 38.74 }, { n: 'Kigali', la: -1.95, lo: 30.06 },
      { n: 'Dubai', la: 25.2, lo: 55.27, hub: 1 }, { n: 'Delhi', la: 28.61, lo: 77.21 }, { n: 'Dhaka', la: 23.81, lo: 90.41 }, { n: 'Manila', la: 14.6, lo: 120.98 },
      { n: 'Riyadh', la: 24.71, lo: 46.68 }, { n: 'Muscat', la: 23.59, lo: 58.41 }, { n: 'Istanbul', la: 41.01, lo: 28.98 }, { n: 'London', la: 51.5, lo: -0.12 }
    ];
    var labelled = { Dubai: 1, Kampala: 1, Lagos: 1, Mombasa: 1, London: 1, Manila: 1 };
    var hub = cities.filter(function (c) { return c.hub; })[0];
    var arcs = cities.filter(function (c) { return !c.hub; }).map(function (c, i) { return { a: c, b: hub, ph: i * .09 }; });
    var pts = []; var N = 700, g = Math.PI * (3 - Math.sqrt(5));
    for (var i = 0; i < N; i++) { var y = 1 - (i / (N - 1)) * 2, r = Math.sqrt(1 - y * y), th = g * i; pts.push([Math.cos(th) * r, y, Math.sin(th) * r]); }
    // world map: land dots (data from static/js/world-land.js, Natural Earth, public domain)
    var land = [];
    (window.GLOBIS_LAND || []).forEach(function (row) { var la = row[0]; row[1].forEach(function (lo) { land.push(ll(la, lo)); }); });

    function ll(la, lo) { var p = la * D, l = lo * D; return [Math.cos(p) * Math.sin(l), Math.sin(p), Math.cos(p) * Math.cos(l)]; }
    function rot(v, yaw, pitch) {
      var cy = Math.cos(yaw), sy = Math.sin(yaw), x = v[0] * cy - v[2] * sy, z = v[0] * sy + v[2] * cy;
      var cp = Math.cos(pitch), sp = Math.sin(pitch), y = v[1] * cp - z * sp; z = v[1] * sp + z * cp; return [x, y, z];
    }
    function slerp(a, b, t) {
      var d = Math.max(-1, Math.min(1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2])), om = Math.acos(d), so = Math.sin(om);
      if (so < 1e-5) return a; var k1 = Math.sin((1 - t) * om) / so, k2 = Math.sin(t * om) / so;
      return [a[0] * k1 + b[0] * k2, a[1] * k1 + b[1] * k2, a[2] * k1 + b[2] * k2];
    }
    function resize() {
      var r = canvas.getBoundingClientRect(); S = Math.max(1, Math.round(r.width)); canvas.width = S * dpr; canvas.height = S * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); R = S * .39;
    }
    function proj(v, yaw, pitch, lift) { var q = rot(v, yaw, pitch), k = 1 + (lift || 0); return { x: S / 2 + q[0] * R * k, y: S / 2 - q[1] * R * k, z: q[2] }; }

    function draw(now) {
      var t = (now - t0) / 1000, pitch = .36, yaw = 35 * D + (reduce ? 0 : Math.sin(t * .2) * .5);
      var cyan = col('--cyan', '#46bdff'), gold = col('--gold', '#f6b94a'), violet = col('--violet', '#4a4fe0'), line = col('--line-2', 'rgba(255,255,255,.18)'), text = col('--text', '#fff');
      ctx.clearRect(0, 0, S, S);
      // halo
      var gr = ctx.createRadialGradient(S / 2, S / 2, R * .6, S / 2, S / 2, R * 1.35); gr.addColorStop(0, 'rgba(31,139,255,.0)'); gr.addColorStop(.72, 'rgba(31,139,255,.20)'); gr.addColorStop(1, 'rgba(31,139,255,0)');
      ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(S / 2, S / 2, R * 1.35, 0, 7); ctx.fill();
      // body
      var bg = ctx.createRadialGradient(S / 2 - R * .3, S / 2 - R * .35, R * .1, S / 2, S / 2, R);
      bg.addColorStop(0, 'rgba(70,189,255,.16)'); bg.addColorStop(1, 'rgba(30,50,120,.10)');
      ctx.fillStyle = bg; ctx.beginPath(); ctx.arc(S / 2, S / 2, R, 0, 7); ctx.fill();
      ctx.strokeStyle = line; ctx.lineWidth = 1; ctx.stroke();
      // graticule
      ctx.lineWidth = .6; ctx.strokeStyle = 'rgba(120,170,255,.16)';
      for (var lo = -180; lo < 180; lo += 20) { ctx.beginPath(); var on = false; for (var la = -90; la <= 90; la += 5) { var p = proj(ll(la, lo), yaw, pitch); if (p.z > 0) { on ? ctx.lineTo(p.x, p.y) : ctx.moveTo(p.x, p.y); on = true; } else on = false; } ctx.stroke(); }
      for (var la2 = -60; la2 <= 60; la2 += 20) { ctx.beginPath(); var on2 = false; for (var lo2 = -180; lo2 <= 180; lo2 += 5) { var p2 = proj(ll(la2, lo2), yaw, pitch); if (p2.z > 0) { on2 ? ctx.lineTo(p2.x, p2.y) : ctx.moveTo(p2.x, p2.y); on2 = true; } else on2 = false; } ctx.stroke(); }
      // ocean dots (faint)
      ctx.fillStyle = cyan;
      for (var i = 0; i < pts.length; i++) { var q = rot(pts[i], yaw, pitch); if (q[2] > 0) { ctx.globalAlpha = .05 + q[2] * .14; ctx.fillRect(S / 2 + q[0] * R, S / 2 - q[1] * R, 1.2, 1.2); } }
      // land dots (the world map)
      var ds = Math.max(1.5, S * .0042);
      ctx.fillStyle = land.length ? cyan : 'transparent';
      for (var j = 0; j < land.length; j++) { var w = rot(land[j], yaw, pitch); if (w[2] > 0) { ctx.globalAlpha = .28 + w[2] * .62; ctx.fillRect(S / 2 + w[0] * R - ds / 2, S / 2 - w[1] * R - ds / 2, ds, ds); } }
      ctx.globalAlpha = 1;
      // arcs
      arcs.forEach(function (a) {
        var A = ll(a.a.la, a.a.lo), B = ll(a.b.la, a.b.lo), steps = 48, first = true;
        ctx.beginPath();
        for (var s = 0; s <= steps; s++) { var u = s / steps, v = slerp(A, B, u), lift = Math.sin(u * Math.PI) * .22, p = proj(v, yaw, pitch, lift); if (p.z < -.05) { first = true; continue; } first ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y); first = false; }
        ctx.strokeStyle = 'rgba(246,185,74,.38)'; ctx.lineWidth = 1.2; ctx.stroke();
        var u2 = ((t * .22 + a.ph) % 1), vv = slerp(A, B, u2), pp = proj(vv, yaw, pitch, Math.sin(u2 * Math.PI) * .22);
        if (pp.z > 0) { ctx.fillStyle = gold; ctx.shadowColor = gold; ctx.shadowBlur = 12; ctx.beginPath(); ctx.arc(pp.x, pp.y, 2.6, 0, 7); ctx.fill(); ctx.shadowBlur = 0; }
      });
      // cities
      cities.forEach(function (c) {
        var p = proj(ll(c.la, c.lo), yaw, pitch); if (p.z <= 0.02) return;
        var pulse = (Math.sin(t * 2.4 + c.lo) + 1) / 2, rad = c.hub ? 5.5 : 3.4;
        ctx.fillStyle = c.hub ? gold : cyan; ctx.shadowColor = c.hub ? gold : cyan; ctx.shadowBlur = 14;
        ctx.beginPath(); ctx.arc(p.x, p.y, rad, 0, 7); ctx.fill(); ctx.shadowBlur = 0;
        ctx.strokeStyle = c.hub ? gold : cyan; ctx.globalAlpha = .55 * (1 - pulse); ctx.lineWidth = 1.4; ctx.beginPath(); ctx.arc(p.x, p.y, rad + 3 + pulse * 11, 0, 7); ctx.stroke(); ctx.globalAlpha = 1;
        if (labelled[c.n]) { ctx.fillStyle = text; ctx.globalAlpha = .9; ctx.font = (c.hub ? '700 ' : '600 ') + Math.max(10, S * .026) + 'px Manrope, system-ui, sans-serif'; ctx.fillText(c.n, p.x + rad + 5, p.y + 3.5); ctx.globalAlpha = 1; }
      });
    }
    var looping = false;
    function tick(now) { if (!running) { looping = false; return; } draw(now); if (reduce) { looping = false; return; } requestAnimationFrame(tick); }
    function start() { running = true; if (!looping) { looping = true; requestAnimationFrame(tick); } }
    resize(); draw(performance.now());
    if ('ResizeObserver' in window) new ResizeObserver(function () { resize(); draw(performance.now()); }).observe(canvas);
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { if (es[0].isIntersecting) start(); else running = false; }, { threshold: 0 }).observe(canvas);
    else start();
    document.addEventListener('visibilitychange', function () { if (document.hidden) running = false; else start(); });
    new MutationObserver(function () { css = getComputedStyle(root); }).observe(root, { attributes: true, attributeFilter: ['data-theme'] });
  }
})();
