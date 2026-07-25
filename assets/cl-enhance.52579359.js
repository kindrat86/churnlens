/* ============================================================
   Churn Lens — UI/UX Enhancement Script
   Mobile nav, CTA bar, back-to-top, scroll reveal, progress bar
   ============================================================ */
(function() {
  'use strict';

  var CL = {};

  /* --- SKIP LINK --- */
  (function() {
    var skip = document.createElement('a');
    skip.href = '#main-content';
    skip.className = 'cl-skip-link';
    skip.textContent = 'Skip to content';
    document.body.insertBefore(skip, document.body.firstChild);
  })();

  /* --- MOBILE NAV --- */
  (function() {
    var toggle = document.querySelector('.cl-nav-toggle');
    var drawer = document.querySelector('.cl-nav-drawer');
    var overlay = document.querySelector('.cl-nav-overlay');

    if (!toggle || !drawer || !overlay) return;

    function openMenu() {
      toggle.classList.add('open');
      drawer.classList.add('open');
      overlay.classList.add('open');
      document.body.classList.add('cl-drawer-open');
      toggle.setAttribute('aria-expanded', 'true');
    }

    function closeMenu() {
      toggle.classList.remove('open');
      drawer.classList.remove('open');
      overlay.classList.remove('open');
      document.body.classList.remove('cl-drawer-open');
      toggle.setAttribute('aria-expanded', 'false');
    }

    toggle.addEventListener('click', function(e) {
      e.stopPropagation();
      if (drawer.classList.contains('open')) { closeMenu(); }
      else { openMenu(); }
    });

    overlay.addEventListener('click', closeMenu);

    // Close on Escape
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && drawer.classList.contains('open')) { closeMenu(); }
    });

    // Close on drawer link click
    drawer.querySelectorAll('a').forEach(function(link) {
      link.addEventListener('click', closeMenu);
    });

    toggle.setAttribute('aria-label', 'Toggle navigation menu');
    toggle.setAttribute('aria-expanded', 'false');
  })();

  /* --- MOBILE CTA BAR --- */
  (function() {
    var bar = document.querySelector('.cl-mobile-cta');
    if (!bar) return;

    function checkScroll() {
      var mainCta = document.querySelector('.btn-primary');
      if (!mainCta) { bar.classList.add('visible'); return; }

      var rect = mainCta.getBoundingClientRect();
      // Show bar when primary CTA has scrolled past the viewport midpoint
      if (rect.bottom < 0 || rect.top > window.innerHeight * 0.6) {
        bar.classList.add('visible');
      } else {
        bar.classList.remove('visible');
      }
    }

    checkScroll();
    window.addEventListener('scroll', checkScroll, { passive: true });
    window.addEventListener('resize', checkScroll, { passive: true });
  })();

  /* --- BACK TO TOP --- */
  (function() {
    var btn = document.querySelector('.cl-back-top');
    if (!btn) {
      // Create it
      btn = document.createElement('button');
      btn.className = 'cl-back-top';
      btn.setAttribute('aria-label', 'Back to top');
      btn.innerHTML = '&#8593;';
      document.body.appendChild(btn);
    }

    // Shared /ux.js appends its own #ux-back-to-top on DOMContentLoaded — i.e.
    // AFTER this deferred script runs — so it cannot be detected up front. Left
    // alone, both FABs stack in the same corner and overlap page content.
    // This one wins ownership because its toggle is a plain scroll listener:
    // ux.js gates its toggle behind requestAnimationFrame, which never fires in
    // a backgrounded tab and latches its internal `ticking` flag true forever,
    // leaving that FAB permanently invisible once the tab is hidden mid-scroll.
    function dropUxDuplicate() {
      var dupe = document.getElementById('ux-back-to-top');
      if (dupe && dupe.parentNode) dupe.parentNode.removeChild(dupe);
    }
    document.addEventListener('DOMContentLoaded', dropUxDuplicate);
    window.addEventListener('load', dropUxDuplicate);
    dropUxDuplicate();

    function checkScroll() {
      if (window.scrollY > 400) {
        btn.classList.add('visible');
      } else {
        btn.classList.remove('visible');
      }
    }

    btn.addEventListener('click', function() {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    checkScroll();
    window.addEventListener('scroll', checkScroll, { passive: true });
  })();

  /* --- SCROLL REVEAL (Intersection Observer) --- */
  (function() {
    var revealEls = document.querySelectorAll('.cl-reveal');
    if (!revealEls.length) return;

    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('cl-visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -40px 0px'
    });

    revealEls.forEach(function(el) { observer.observe(el); });
  })();

  /* --- READING PROGRESS BAR --- */
  (function() {
    var bar = document.querySelector('.cl-progress');
    if (!bar) {
      bar = document.createElement('div');
      bar.className = 'cl-progress';
      document.body.appendChild(bar);
    }

    function updateProgress() {
      var scrollTop = window.scrollY;
      var docHeight = document.documentElement.scrollHeight - window.innerHeight;
      if (docHeight <= 0) { bar.style.width = '0%'; return; }
      var pct = Math.min((scrollTop / docHeight) * 100, 100);
      bar.style.width = pct + '%';
    }

    updateProgress();
    window.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress, { passive: true });
  })();

  /* --- EXIT INTENT ENHANCEMENT --- */
  (function() {
    // Fix: mark exit-intent shown when user interacts with bar CTA
    var barCta = document.querySelector('.cl-mobile-cta a');
    if (barCta) {
      barCta.addEventListener('click', function() {
        try { sessionStorage.setItem('exit_intent_shown', '1'); } catch(e) {}
      });
    }
  })();

  /* --- FORM SUBMIT ENHANCEMENT --- */
  (function() {
    var form = document.getElementById('optin-form');
    if (!form) return;

    var btn = document.getElementById('submit-btn');
    var errorEl = document.createElement('div');
    errorEl.className = 'cl-form-error';
    form.parentNode.insertBefore(errorEl, form.nextSibling);

    // Override form submit to prevent duplicate handlers
    var origHandler = form._submitHandler;
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      var email = document.getElementById('email-input');
      if (!email || !email.value.trim()) {
        errorEl.textContent = 'Please enter your email address.';
        errorEl.classList.add('show');
        return;
      }
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) {
        errorEl.textContent = 'Please enter a valid email address.';
        errorEl.classList.add('show');
        return;
      }
      errorEl.classList.remove('show');
      btn.classList.add('loading');
      btn.disabled = true;

      try {
        var resp = await fetch('/api/subscribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email.value.trim(), source: 'squeeze-page' })
        });
        var data = await resp.json();
        if (!resp.ok || !data.ok) {
          throw new Error(data.error || 'Server error');
        }
      } catch(err) {
        console.error('Subscribe error:', err);
        errorEl.textContent = 'Something went wrong. Please try again or email hello@churnlens.site.';
        errorEl.classList.add('show');
        btn.classList.remove('loading');
        btn.disabled = false;
        return;
      }

      btn.classList.remove('loading');
      form.style.display = 'none';

      var oto = document.getElementById('oto-msg');
      if (oto) oto.classList.add('show');
      if (window.posthog) {
        posthog.capture('lead_optin', { source: 'squeeze-page' });
        posthog.capture('oto_shown');
      }
    });
  })();

  /* ============================================================
     R19 — 2026-07-25
     Drawer accessibility (inert / focus trap / focus restore) and a
     correct sticky-CTA rule. Runs after the original IIFEs above, so it
     upgrades the elements they already wired.
     ============================================================ */

  /* --- DRAWER: inert when closed, focus-trapped when open --- */
  (function() {
    var toggle = document.querySelector('.cl-nav-toggle');
    var drawer = document.querySelector('.cl-nav-drawer');
    var overlay = document.querySelector('.cl-nav-overlay');
    if (!toggle || !drawer || !overlay) return;

    var lastFocus = null;

    // Closed drawer sits off-canvas at translateX(100%) but stayed visible to
    // the a11y tree: 8 links you could Tab into but never see.
    function seal() {
      if (drawer.classList.contains('open')) return;
      drawer.setAttribute('inert', '');
      drawer.setAttribute('aria-hidden', 'true');
    }
    function unseal() {
      drawer.removeAttribute('inert');
      drawer.setAttribute('aria-hidden', 'false');
    }
    seal();

    function focusables() {
      return Array.prototype.filter.call(
        drawer.querySelectorAll('a[href], button:not([disabled])'),
        function(el) { return el.offsetParent !== null || getComputedStyle(el).position === 'fixed'; }
      );
    }

    // The drawer transitions out over 0.4s; sealing it immediately would yank
    // it from the a11y tree mid-animation, so wait for the transition to end.
    drawer.addEventListener('transitionend', function(e) {
      if (e.propertyName === 'transform') seal();
    });

    toggle.addEventListener('click', function() {
      if (drawer.classList.contains('open')) {
        unseal();
        lastFocus = toggle;
        var f = focusables();
        if (f.length) f[0].focus();
      }
      // closing is handled by transitionend -> seal()
    });

    overlay.addEventListener('click', restoreFocus);
    function restoreFocus() {
      if (lastFocus) { try { lastFocus.focus(); } catch (e) {} lastFocus = null; }
    }
    drawer.querySelectorAll('a').forEach(function(a) {
      a.addEventListener('click', function() { lastFocus = null; });
    });

    document.addEventListener('keydown', function(e) {
      if (!drawer.classList.contains('open')) return;
      if (e.key === 'Escape') { restoreFocus(); return; }
      if (e.key !== 'Tab') return;
      var f = focusables();
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  })();

  /* --- STICKY MOBILE CTA: show it only when no inline CTA is on screen --- */
  (function() {
    var bar = document.querySelector('.cl-mobile-cta');
    if (!bar) return;
    // The original rule watched `document.querySelector('.btn-primary')` — the
    // FIRST primary button only. On /pricing that is the Starter tier button
    // near the top, so once you scrolled past it the bar appeared and sat
    // there duplicating the Pro and Dealmaker buttons still on screen.
    // The bar exists so there is always exactly one reachable CTA: show it
    // when none of the inline ones are currently visible.
    var inline = document.querySelectorAll('.btn-primary, .tier-cta, .sq-btn, .cta > a');
    if (!inline.length) { bar.classList.add('visible'); return; }

    var onScreen = 0;
    var io = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) { onScreen += e.isIntersecting ? 1 : -1; });
      if (onScreen < 0) onScreen = 0;
      bar.classList.toggle('visible', onScreen === 0 && window.scrollY > 400);
    }, { rootMargin: '0px 0px -60px 0px' });
    inline.forEach(function(el) { io.observe(el); });

    window.addEventListener('scroll', function() {
      bar.classList.toggle('visible', onScreen === 0 && window.scrollY > 400);
    }, { passive: true });
  })();

})();
