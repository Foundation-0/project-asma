/* Foundation0 runtime (window.F0), trimmed for the Project Asma pages. Plain script, no modules, no dependencies.
   Taken from the shared Foundation0 site runtime (source commit not recorded here) and cut on 2026-10-25 to what
   index.html and 404.html use: the theme and motion toggles, the header menu, and the "On this page" index (the
   rail is static markup in the page; this marks the current section and adds a compact bar below 960px).
   Removed: data fetchers, figure and chart helpers, status-badge builders and the AI-role ledger. It makes no
   network requests. */
(function () {
  'use strict';
  var root = document.documentElement;
  var mqReduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var mqDark = window.matchMedia('(prefers-color-scheme: dark)');
  var F0 = window.F0 = window.F0 || {};

  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } return null; }

  /* ---- reduced motion + global motion toggle ---- */
  F0.reduced = mqReduce.matches;
  var motionPref = root.getAttribute('data-motion-pref'); // set by the inline bootstrap from ?motion= or storage
  F0.motion = function () { return motionPref ? motionPref === 'on' : !F0.reduced; };
  /* The header toggle is a toggle button with a fixed name, "Motion"; aria-pressed (and the icon: waves, or waves
     struck through) says whether motion is on. Its name never changes, so a screen reader never hears "Pause, pressed". */
  function applyMotion() {
    root.setAttribute('data-motion', F0.motion() ? 'on' : 'off');
    document.querySelectorAll('[data-motion-toggle]').forEach(function (b) {
      var on = F0.motion();
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
      b.setAttribute('aria-label', 'Motion');
      b.title = on ? 'Motion is on: press to stop it' : 'Motion is off: press to allow it';
      var t = b.querySelector('.t-txt'); if (t) t.textContent = 'Motion';
      var i = b.querySelector('.ico'); if (i) i.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round">' +
        '<path d="M2 6c2-2.2 4 2.2 6 0s4-2.2 6 0M2 10.5c2-2.2 4 2.2 6 0s4-2.2 6 0"/>' + (on ? '' : '<path d="M3 14L13 2"/>') + '</g></svg>';
    });
  }
  mqReduce.addEventListener('change', function () { F0.reduced = mqReduce.matches; applyMotion(); });

  /* ---- theme ---- */
  F0.theme = function () { var t = root.getAttribute('data-theme'); return t === 'dark' || t === 'light' ? t : (mqDark.matches ? 'dark' : 'light'); };
  function themeChanged() {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      var dark = F0.theme() === 'dark';
      b.setAttribute('aria-label', dark ? 'Dark theme: switch to light' : 'Light theme: switch to dark');
      var t = b.querySelector('.t-txt'); if (t) t.textContent = dark ? 'Dark' : 'Light';
      var i = b.querySelector('.ico'); if (i) i.innerHTML = dark
        ? '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M10.8 2.2a6 6 0 1 0 3 9.6A5.2 5.2 0 0 1 10.8 2.2z" fill="currentColor"/></svg>'
        : '<svg viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="3.2" fill="currentColor"/><g stroke="currentColor" stroke-width="1.3" stroke-linecap="round"><path d="M8 1v2M8 13v2M1 8h2M13 8h2M3 3l1.4 1.4M11.6 11.6L13 13M3 13l1.4-1.4M11.6 4.4L13 3"/></g></svg>';
    });
  }
  mqDark.addEventListener('change', themeChanged);

  /* ---- escaping ---- */
  F0.esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]; }); };

  /* ---- toggles and section index ---- */
  function bind() {
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      b.addEventListener('click', function () {
        var next = F0.theme() === 'dark' ? 'light' : 'dark';
        root.setAttribute('data-theme', next); store('f0-theme', next); themeChanged();
      });
    });
    document.querySelectorAll('[data-motion-toggle]').forEach(function (b) {
      b.addEventListener('click', function () {
        motionPref = F0.motion() ? 'off' : 'on'; store('f0-motion', motionPref); applyMotion();
      });
    });
    var secs = [].slice.call(document.querySelectorAll('section[data-index]')).filter(function (s) { return s.id; });
    var hud = document.querySelector('[data-hud]');
    if (hud && secs.length) {
      var num = function (s, i) { return s.getAttribute('data-num') || String(i).padStart(2, '0'); };
      /* the rail (960px and up) is the page's own static list; find its link for each section */
      var links = secs.map(function (s) { return hud.querySelector('a[href="#' + s.id + '"]'); });
      /* the compact bar under the header (below 960px), for pages with three or more sections */
      var bar = null, sum = null, prog = null, blinks = [], det = null;
      if (secs.length >= 3) {
        bar = document.createElement('nav'); bar.className = 'secbar'; bar.setAttribute('aria-label', 'On this page (compact)');
        bar.innerHTML = '<div class="wrap"><details><summary><span class="sb-cur"></span><svg class="chev" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.5 4.5L6 8l3.5-3.5" fill="none" stroke="currentColor" stroke-width="1.4"/></svg></summary><ol></ol></details></div><span class="prog" aria-hidden="true"></span>';
        var bol = bar.querySelector('ol');
        secs.forEach(function (s, i) {
          var li = document.createElement('li'), a = document.createElement('a');
          a.href = '#' + s.id;
          a.innerHTML = '<span>' + F0.esc(num(s, i)) + '</span>' + F0.esc(s.getAttribute('data-index'));
          li.appendChild(a); bol.appendChild(li);
        });
        blinks = [].slice.call(bol.querySelectorAll('a'));
        det = bar.querySelector('details'); sum = bar.querySelector('.sb-cur'); prog = bar.querySelector('.prog');
        blinks.forEach(function (a) { a.addEventListener('click', function () { det.open = false; }); });
        hud.parentNode.insertBefore(bar, hud);
        root.classList.add('has-secbar');
        closeOnLeave(det);
      }
      var lastCur = -2;
      var spy = function () {
        var y = 140, cur = -1;
        secs.forEach(function (s, i) { if (s.getBoundingClientRect().top <= y) cur = i; });
        if (cur !== lastCur) {
          lastCur = cur;
          links.concat(blinks).forEach(function (a) { if (a) a.setAttribute('aria-current', 'false'); });
          if (cur >= 0) { if (links[cur]) links[cur].setAttribute('aria-current', 'true'); if (blinks[cur]) blinks[cur].setAttribute('aria-current', 'true'); }
          if (sum && cur >= 0) sum.innerHTML = '<b>' + F0.esc(num(secs[cur], cur)) + '</b> // <span class="t">' + F0.esc(secs[cur].getAttribute('data-index')) + '</span> <span aria-hidden="true">·</span> ' + (cur + 1) + ' of ' + secs.length;
        }
        if (bar) {
          var doc = document.documentElement, max = Math.max(1, doc.scrollHeight - window.innerHeight), f = Math.min(1, Math.max(0, window.scrollY / max));
          prog.style.transform = 'scaleX(' + f.toFixed(4) + ')';
          var show = cur >= 0 && window.scrollY > window.innerHeight * 0.5;
          if (show !== bar.classList.contains('on')) { bar.classList.toggle('on', show); if (!show) det.open = false; }
        }
      };
      var pending = false;
      window.addEventListener('scroll', function () { if (!pending) { pending = true; requestAnimationFrame(function () { pending = false; spy(); }); } }, { passive: true });
      window.addEventListener('resize', spy, { passive: true });
      spy();
    }
    /* close the mobile menu (and the compact section list) with Escape, an outside click, or when focus leaves it */
    var menu = document.querySelector('.menu');
    if (menu) closeOnLeave(menu);
    themeChanged(); applyMotion();
  }
  function closeOnLeave(d) {
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && d.open) { d.open = false; d.querySelector('summary').focus(); } });
    document.addEventListener('click', function (e) { if (d.open && !d.contains(e.target)) d.open = false; });
    d.addEventListener('focusout', function (e) { if (d.open && e.relatedTarget && !d.contains(e.relatedTarget)) d.open = false; });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bind); else bind();
})();
