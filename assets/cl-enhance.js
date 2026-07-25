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

})();
