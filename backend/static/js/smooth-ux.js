/* Aqua-Terra UX polish
   - Loading state on auth/admin form submit (spinner + disabled)
   - Smooth page fade-in on load
   - Sidebar links: brief shimmer on click (perceived speed)
*/
(function () {
  // ---- Fade in body on load ----
  document.documentElement.classList.add('page-loading');
  window.addEventListener('load', () => {
    document.documentElement.classList.remove('page-loading');
    document.documentElement.classList.add('page-ready');
  });
  // safety: even if 'load' is slow, reveal after 600ms
  setTimeout(() => {
    document.documentElement.classList.remove('page-loading');
    document.documentElement.classList.add('page-ready');
  }, 600);

  // ---- Loading state on form submit (auth + admin) ----
  document.addEventListener('submit', (e) => {
    const form = e.target;
    if (!(form instanceof HTMLFormElement)) return;
    // skip JSON forms (newsletter / cart use api.js)
    if (form.dataset.skipLoading === '1') return;
    if (form.classList.contains('newsletter-form')) return;

    const btn = form.querySelector('button[type="submit"], button:not([type])');
    if (!btn || btn.dataset.loading === '1') return;

    btn.dataset.loading = '1';
    btn.dataset.originalHtml = btn.innerHTML;
    btn.disabled = true;
    btn.classList.add('btn-loading');
    btn.innerHTML = '<span class="spinner"></span> Procesando...';
    // safety re-enable after 8s (in case navigation never finishes)
    setTimeout(() => {
      if (btn.dataset.loading === '1' && btn.dataset.originalHtml) {
        btn.innerHTML = btn.dataset.originalHtml;
        btn.disabled = false;
        btn.classList.remove('btn-loading');
        btn.dataset.loading = '0';
      }
    }, 8000);
  });

  // ---- Sidebar links: outbound nav transition ----
  // Wait a tick on internal link clicks so the user sees a subtle indicator.
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a');
    if (!a) return;
    const href = a.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('javascript:')) return;
    // external?
    if (/^https?:\/\//i.test(href) && !href.startsWith(location.origin)) return;
    if (a.target === '_blank' || a.hasAttribute('download')) return;
    // skip cart/wishlist toggle buttons
    if (a.classList.contains('js-add-cart') || a.classList.contains('js-wishlist')) return;
    document.documentElement.classList.add('page-leaving');
  });
  // if back-forward cache restores the page, drop the leaving class
  window.addEventListener('pageshow', () => {
    document.documentElement.classList.remove('page-leaving');
  });

  // ---- Smooth sidebar group expand (height transition) ----
  // Already CSS-driven via .open class; no JS needed here, but ensure
  // toggle is debounced so rapid clicks don't break the animation.
  let lastToggle = 0;
  document.querySelectorAll('.sidebar-group-trigger').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const now = Date.now();
      if (now - lastToggle < 200) { e.preventDefault(); return; }
      lastToggle = now;
    }, true);
  });
})();
