// ---- AOS init ----
if (window.AOS) AOS.init({ once: true, duration: 700, easing: 'ease-out' });

// ---- Sidebar: mobile drawer ----
const navToggle = document.getElementById('navToggle');
const sidebar = document.getElementById('sidebar');
const backdrop = document.getElementById('sidebarBackdrop');

const openSidebar = () => {
  document.body.classList.add('sidebar-open');
  if (backdrop) backdrop.hidden = false;
  navToggle?.setAttribute('aria-expanded', 'true');
};
const closeSidebar = () => {
  document.body.classList.remove('sidebar-open');
  if (backdrop) backdrop.hidden = true;
  navToggle?.setAttribute('aria-expanded', 'false');
};

navToggle?.addEventListener('click', () => {
  if (document.body.classList.contains('sidebar-open')) closeSidebar();
  else openSidebar();
});
backdrop?.addEventListener('click', closeSidebar);
sidebar?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
  if (window.innerWidth <= 1024) closeSidebar();
}));
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeSidebar(); });

// ---- Sidebar: desktop collapse ----
const COLLAPSE_KEY = 'sidebar_collapsed';
const collapseBtn = document.getElementById('sidebarCollapse');
if (localStorage.getItem(COLLAPSE_KEY) === '1') document.body.classList.add('sidebar-collapsed');
collapseBtn?.addEventListener('click', () => {
  const collapsed = document.body.classList.toggle('sidebar-collapsed');
  localStorage.setItem(COLLAPSE_KEY, collapsed ? '1' : '0');
});

// ---- Sidebar: expandable groups ----
document.querySelectorAll('.sidebar-group-trigger').forEach(btn => {
  btn.addEventListener('click', () => {
    const key = btn.dataset.group;
    const submenu = document.querySelector(`[data-submenu="${key}"]`);
    if (!submenu) return;
    const open = submenu.classList.toggle('open');
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
});

// ---- Counters ----
const counters = document.querySelectorAll('.counter');
if (counters.length) {
  const animate = (el) => {
    const target = parseFloat(el.dataset.target || '0');
    if (!target) { el.textContent = '0'; return; }
    const dur = 1600, start = performance.now();
    const tick = (now) => {
      const t = Math.min(1, (now - start) / dur);
      const ease = 1 - Math.pow(1 - t, 3);
      const v = Math.floor(target * ease);
      el.textContent = v.toLocaleString('es-ES');
      if (t < 1) requestAnimationFrame(tick);
      else el.textContent = target.toLocaleString('es-ES');
    };
    requestAnimationFrame(tick);
  };
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) { animate(e.target); io.unobserve(e.target); }
    });
  }, { threshold: 0.4 });
  counters.forEach(c => io.observe(c));
}

// ---- Testimonial slider ----
const slides = document.querySelectorAll('.testimonial-slide');
const dotsBox = document.getElementById('testimonialDots');
if (slides.length && dotsBox) {
  let idx = 0;
  slides.forEach((_, i) => {
    const b = document.createElement('button');
    if (i === 0) b.classList.add('active');
    b.addEventListener('click', () => goto(i));
    dotsBox.appendChild(b);
  });
  const dots = dotsBox.querySelectorAll('button');
  const goto = (i) => {
    slides[idx].classList.remove('active');
    dots[idx].classList.remove('active');
    idx = (i + slides.length) % slides.length;
    slides[idx].classList.add('active');
    dots[idx].classList.add('active');
  };
  document.querySelector('.slider-prev')?.addEventListener('click', () => goto(idx - 1));
  document.querySelector('.slider-next')?.addEventListener('click', () => goto(idx + 1));
  setInterval(() => goto(idx + 1), 6500);
}

// ---- Add to cart (quick buttons) ----
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.js-add-cart');
  if (!btn) return;
  e.preventDefault();
  const id = parseInt(btn.dataset.productId, 10);
  try {
    const res = await api.post('/shop/cart/add', { product_id: id, qty: 1 });
    document.querySelectorAll('#cartBadge').forEach(b => b.textContent = res.cart_count);
    toast(`Agregado al carrito: ${res.product}`);
  } catch (err) { toast('Error al agregar', 'error'); }
});

// ---- Wishlist ----
document.addEventListener('click', async (e) => {
  const btn = e.target.closest('.js-wishlist');
  if (!btn) return;
  e.preventDefault();
  const id = parseInt(btn.dataset.productId, 10);
  try {
    const res = await api.post('/shop/wishlist/toggle', { product_id: id, qty: 1 });
    btn.classList.toggle('active', res.added);
    const icon = btn.querySelector('i');
    if (icon) icon.className = res.added ? 'fa-solid fa-heart' : 'fa-regular fa-heart';
    document.querySelectorAll('#wishlistBadge').forEach(b => b.textContent = res.count);
    toast(res.added ? 'Agregado a favoritos' : 'Quitado de favoritos');
  } catch (err) { toast('Error', 'error'); }
});

// ---- Newsletter ----
const newsletter = document.getElementById('newsletterForm');
if (newsletter) {
  newsletter.addEventListener('submit', async (e) => {
    e.preventDefault();
    const msg = document.getElementById('newsletterMsg');
    const email = newsletter.querySelector('input[name="email"]').value;
    try {
      const res = await api.post('/newsletter/subscribe', { email, source: 'footer' });
      msg.textContent = res.already ? 'Ya estabas suscrito - gracias!' : 'Suscripcion confirmada.';
      msg.className = 'form-msg success';
      newsletter.reset();
    } catch (err) {
      msg.textContent = 'Email invalido. Intenta de nuevo.';
      msg.className = 'form-msg error';
    }
  });
}
