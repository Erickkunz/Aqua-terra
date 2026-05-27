/* Aqua-Terra UX polish
   - Page overlay (logo + spinner) covers navigation so there's NO white flash
   - Loading state on auth/admin form submit
   - Submenu click debounce
*/
(function () {
  const overlay = document.getElementById('pageOverlay');

  // ---- Hide overlay once page is ready ----
  function hideOverlay() {
    if (!overlay) return;
    overlay.classList.add('hide');
    overlay.classList.remove('show'); // ensure pointer-events returns to none
    if (overlay.__safetyTimer) { clearTimeout(overlay.__safetyTimer); overlay.__safetyTimer = null; }
    setTimeout(() => { overlay.style.display = 'none'; }, 450);
  }

  // The overlay starts visible (covers everything). Fade out when page is rendered.
  if (overlay) {
    overlay.style.display = 'flex';
    // wait for next frame so first paint is the overlay (no flash)
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        // small delay so user perceives the transition smoothly
        if (document.readyState === 'complete') {
          setTimeout(hideOverlay, 80);
        } else {
          window.addEventListener('load', () => setTimeout(hideOverlay, 80), { once: true });
          // safety: hide after 1.5s no matter what
          setTimeout(hideOverlay, 1500);
        }
      });
    });
  }

  // ---- Show overlay on internal link navigation ----
  function isInternalNav(a) {
    const href = a.getAttribute('href');
    if (!href) return false;
    if (href.startsWith('#') || href.startsWith('javascript:') || href.startsWith('mailto:') || href.startsWith('tel:')) return false;
    if (a.target === '_blank' || a.hasAttribute('download')) return false;
    if (/^https?:\/\//i.test(href) && !href.startsWith(location.origin)) return false;
    return true;
  }

  document.addEventListener('click', (e) => {
    const a = e.target.closest('a');
    if (!a) return;
    if (!isInternalNav(a)) return;
    if (a.classList.contains('js-add-cart') || a.classList.contains('js-wishlist')) return;
    showOverlay();
  });

  function showOverlay() {
    if (!overlay) return;
    overlay.style.display = 'flex';
    overlay.classList.remove('hide');
    overlay.classList.add('show');
    // Safety: if navigation never completes, hide overlay after 4s so the page
    // stays usable instead of blocking all clicks (pointer-events: auto on .show).
    if (overlay.__safetyTimer) clearTimeout(overlay.__safetyTimer);
    overlay.__safetyTimer = setTimeout(() => {
      hideOverlay();
      overlay.classList.remove('show');
    }, 4000);
  }

  // ---- Form submit: overlay + button spinner ----
  document.addEventListener('submit', (e) => {
    const form = e.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (form.dataset.skipLoading === '1') return;
    if (form.classList.contains('newsletter-form')) return;

    showOverlay();

    const btn = form.querySelector('button[type="submit"], button:not([type])');
    if (!btn || btn.dataset.loading === '1') return;
    btn.dataset.loading = '1';
    btn.dataset.originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.classList.add('btn-loading');
    btn.innerHTML = '<span class="spinner"></span> Procesando...';
    setTimeout(() => {
      if (btn.dataset.loading === '1' && btn.dataset.originalHtml) {
        btn.innerHTML = btn.dataset.originalHtml;
        btn.disabled = false;
        btn.classList.remove('btn-loading');
        btn.dataset.loading = '0';
      }
    }, 8000);
  });

  // ---- BFCache: drop overlay if user hits back ----
  window.addEventListener('pageshow', (e) => {
    if (e.persisted) {
      hideOverlay();
    }
  });

  // ---- Debounce sidebar group toggles ----
  let lastToggle = 0;
  document.querySelectorAll('.sidebar-group-trigger').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const now = Date.now();
      if (now - lastToggle < 200) { e.preventDefault(); return; }
      lastToggle = now;
    }, true);
  });
})();
