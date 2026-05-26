window.api = (() => {
  const request = async (url, opts = {}) => {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
      ...opts,
    });
    let data = null;
    try { data = await res.json(); } catch (_) {}
    if (!res.ok) throw new Error((data && data.detail) || res.statusText);
    return data;
  };
  return {
    get: (u) => request(u),
    post: (u, body) => request(u, { method: 'POST', body: JSON.stringify(body) }),
  };
})();

window.toast = (msg, type = 'success') => {
  let el = document.getElementById('toastEl');
  if (!el) {
    el = document.createElement('div');
    el.id = 'toastEl';
    el.style.cssText = 'position:fixed;bottom:90px;right:20px;background:#1F2A37;color:#fff;padding:.85rem 1.15rem;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,.25);z-index:300;opacity:0;transform:translateY(8px);transition:all .25s;font-size:.9rem;max-width:320px;';
    document.body.appendChild(el);
  }
  el.style.background = type === 'error' ? '#7F1D1D' : (type === 'warn' ? '#92400E' : '#1F2A37');
  el.textContent = msg;
  requestAnimationFrame(() => { el.style.opacity = '1'; el.style.transform = 'translateY(0)'; });
  clearTimeout(el._timer);
  el._timer = setTimeout(() => { el.style.opacity = '0'; el.style.transform = 'translateY(8px)'; }, 2800);
};
