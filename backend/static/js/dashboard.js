const D = window.__DASH || { growth: [], techDistribution: [], byCountry: [], mapPoints: [] };
const PALETTE = ['#2E75B6', '#70AD47', '#3D5A80', '#1F4E79', '#F59E0B', '#DC2626', '#16A34A', '#6B7280'];

// Growth line
const growthCtx = document.getElementById('growthChart');
if (growthCtx) {
  new Chart(growthCtx, {
    type: 'line',
    data: {
      labels: D.growth.map(g => g.year),
      datasets: [{
        label: 'm3 ahorrados',
        data: D.growth.map(g => g.water_saved_m3),
        borderColor: '#2E75B6', backgroundColor: 'rgba(46,117,182,.15)',
        fill: true, tension: .35, pointRadius: 4, pointBackgroundColor: '#2E75B6',
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, ticks: { callback: v => v.toLocaleString('es-ES') } } },
    },
  });
}

// Tech distribution doughnut
const techCtx = document.getElementById('techChart');
if (techCtx) {
  new Chart(techCtx, {
    type: 'doughnut',
    data: {
      labels: D.techDistribution.map(t => t.label),
      datasets: [{
        data: D.techDistribution.map(t => t.value),
        backgroundColor: PALETTE, borderWidth: 0,
      }],
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right' } } },
  });
}

// Country bars
const countryCtx = document.getElementById('countryChart');
if (countryCtx) {
  const top = D.byCountry.slice(0, 8);
  new Chart(countryCtx, {
    type: 'bar',
    data: {
      labels: top.map(c => c.country),
      datasets: [{
        label: 'm3 ahorrados',
        data: top.map(c => c.water_saved_m3),
        backgroundColor: '#70AD47',
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false, indexAxis: 'y',
      plugins: { legend: { display: false } },
      scales: { x: { ticks: { callback: v => v.toLocaleString('es-ES') } } },
    },
  });
}

// Impact map
const impactMapEl = document.getElementById('impactMap');
if (impactMapEl && window.L) {
  const map = L.map('impactMap', { worldCopyJump: true, scrollWheelZoom: false }).setView([0, -30], 2);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OSM' }).addTo(map);
  const group = L.featureGroup();
  D.mapPoints.forEach(p => {
    const m = L.circleMarker([p.lat, p.lng], {
      radius: Math.max(5, Math.min(18, Math.sqrt(p.hectares) / 2)),
      color: '#2E75B6', fillColor: '#70AD47', fillOpacity: .7, weight: 2,
    }).bindPopup(`<strong>${p.name}</strong><br/>${p.country}<br/>${p.water_saved_m3.toLocaleString('es-ES')} m3`);
    m.addTo(map);
    group.addLayer(m);
  });
  if (D.mapPoints.length) map.fitBounds(group.getBounds().pad(0.25));
}
