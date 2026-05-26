document.getElementById('contactForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.currentTarget;
  const msg = document.getElementById('contactMsg');
  const payload = {
    name: form.name.value.trim(),
    email: form.email.value.trim(),
    phone: form.phone.value.trim(),
    inquiry_type: form.inquiry_type.value,
    pillar: form.pillar.value,
    message: form.message.value.trim(),
  };
  try {
    await api.post('/contact/submit', payload);
    msg.className = 'form-msg success';
    msg.textContent = 'Mensaje enviado. Te respondemos en menos de 24 horas.';
    form.reset();
  } catch (err) {
    msg.className = 'form-msg error';
    msg.textContent = 'No se pudo enviar. Revisa los datos.';
  }
});

// Offices map
const officesMapEl = document.getElementById('officesMap');
if (officesMapEl && window.L) {
  const offices = JSON.parse(officesMapEl.dataset.offices || '[]');
  if (offices.length) {
    const map = L.map('officesMap', { scrollWheelZoom: false }).setView([0, -70], 2);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap' }).addTo(map);
    offices.forEach(o => L.marker([o.lat, o.lng]).addTo(map).bindPopup(`<strong>${o.city}, ${o.country}</strong><br/>${o.address}`));
    const group = L.featureGroup(offices.map(o => L.marker([o.lat, o.lng])));
    map.fitBounds(group.getBounds().pad(0.3));
  }
}
