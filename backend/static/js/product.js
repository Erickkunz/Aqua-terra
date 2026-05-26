// Tabs
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.querySelector(`.tab-panel[data-panel="${btn.dataset.tab}"]`)?.classList.add('active');
  });
});

// Qty
const qtyInput = document.getElementById('qtyInput');
document.getElementById('qtyPlus')?.addEventListener('click', () => qtyInput.value = (parseInt(qtyInput.value, 10) || 1) + 1);
document.getElementById('qtyMinus')?.addEventListener('click', () => qtyInput.value = Math.max(1, (parseInt(qtyInput.value, 10) || 1) - 1));

// Add to cart with quantity
document.querySelector('.js-add-cart-qty')?.addEventListener('click', async (e) => {
  e.preventDefault();
  const btn = e.currentTarget;
  const id = parseInt(btn.dataset.productId, 10);
  const qty = parseInt(qtyInput.value, 10) || 1;
  try {
    const res = await api.post('/shop/cart/add', { product_id: id, qty });
    document.querySelectorAll('#cartBadge').forEach(b => b.textContent = res.cart_count);
    toast(`Agregado al carrito (x${qty})`);
  } catch (err) { toast('Error al agregar', 'error'); }
});

// Notify me
document.getElementById('notifyMe')?.addEventListener('click', (e) => {
  e.preventDefault();
  const email = prompt('Te avisamos cuando este disponible. Tu email:');
  if (email && email.includes('@')) toast('Listo, te avisaremos en cuanto vuelva a stock.');
});
