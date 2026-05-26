// Cart quantity updates
const reloadCart = () => location.reload();

document.querySelectorAll('.cart-qty-plus').forEach(b => b.addEventListener('click', async (e) => {
  const row = e.target.closest('.cart-row');
  const input = row.querySelector('.cart-qty-input');
  input.value = (parseInt(input.value, 10) || 1) + 1;
  await api.post('/shop/cart/update', { product_id: parseInt(input.dataset.productId, 10), qty: parseInt(input.value, 10) });
  reloadCart();
}));

document.querySelectorAll('.cart-qty-minus').forEach(b => b.addEventListener('click', async (e) => {
  const row = e.target.closest('.cart-row');
  const input = row.querySelector('.cart-qty-input');
  const v = Math.max(1, (parseInt(input.value, 10) || 1) - 1);
  input.value = v;
  await api.post('/shop/cart/update', { product_id: parseInt(input.dataset.productId, 10), qty: v });
  reloadCart();
}));

document.querySelectorAll('.cart-qty-input').forEach(inp => inp.addEventListener('change', async (e) => {
  const v = Math.max(1, parseInt(e.target.value, 10) || 1);
  e.target.value = v;
  await api.post('/shop/cart/update', { product_id: parseInt(e.target.dataset.productId, 10), qty: v });
  reloadCart();
}));

document.querySelectorAll('.cart-remove').forEach(b => b.addEventListener('click', async (e) => {
  const id = parseInt(e.currentTarget.dataset.productId, 10);
  await api.post('/shop/cart/remove', { product_id: id, qty: 1 });
  reloadCart();
}));

// Quote modal
const modal = document.getElementById('quoteModal');
document.getElementById('openQuoteModal')?.addEventListener('click', () => { if (modal) modal.hidden = false; });
document.getElementById('closeQuoteModal')?.addEventListener('click', () => { if (modal) modal.hidden = true; });
modal?.addEventListener('click', (e) => { if (e.target === modal) modal.hidden = true; });

document.getElementById('quoteForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const msg = document.getElementById('quoteMsg');
  const items = [...document.querySelectorAll('.cart-row')].map(r => ({
    product_id: parseInt(r.dataset.productId, 10),
    qty: parseInt(r.querySelector('.cart-qty-input').value, 10) || 1,
  }));
  const payload = {
    name: form.name.value.trim(),
    email: form.email.value.trim(),
    company: form.company.value.trim(),
    phone: form.phone.value.trim(),
    country: form.country.value.trim(),
    notes: form.notes.value.trim(),
    items,
  };
  try {
    const res = await api.post('/shop/quote', payload);
    msg.className = 'form-msg success';
    msg.textContent = `Cotizacion #${res.quote_id} enviada. Total estimado: USD ${res.estimated_total.toLocaleString('es-ES', { maximumFractionDigits: 2 })}`;
    setTimeout(() => location.href = '/shop', 2200);
  } catch (err) {
    msg.className = 'form-msg error';
    msg.textContent = 'No se pudo enviar la cotizacion. Revisa los datos.';
  }
});
