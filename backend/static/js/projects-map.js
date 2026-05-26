const mapEl = document.getElementById('projectsMap');
if (mapEl && window.L) {
  const points = JSON.parse(mapEl.dataset.points || '[]');
  const map = L.map('projectsMap', { worldCopyJump: true, scrollWheelZoom: false }).setView([-5, -60], 3);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap' }).addTo(map);
  if (points.length) {
    const group = L.featureGroup();
    points.forEach(p => {
      const m = L.marker([p.lat, p.lng]).bindPopup(
        `<strong>${p.name}</strong><br/>${p.country} - ${p.hectares.toLocaleString('es-ES')} ha<br/>${p.water_saved_m3.toLocaleString('es-ES')} m3 ahorrados<br/><a href="/projects/${p.slug}">Ver detalle</a>`
      );
      m.addTo(map);
      group.addLayer(m);
    });
    map.fitBounds(group.getBounds().pad(0.25));
  }
}
