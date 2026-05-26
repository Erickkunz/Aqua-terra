// Simple ROI estimator (heuristic, demo)
const CROP_BASE_USD = { cereales: 800, frutales: 2200, hortalizas: 1800, vid: 2800, "caña": 1500 };
const SAVINGS_BY_CLIMATE = { arido: 0.55, semiarido: 0.45, templado: 0.32, humedo: 0.22 };
const SAVINGS_BONUS_BY_CURRENT = { gravedad: 0.18, aspersion: 0.08, goteo_basico: 0.0 };
const INVEST_PER_HA = 1100; // USD per hectare (demo)

const form = document.getElementById('roiForm');
const results = document.getElementById('roiResults');
let chartInstance = null;

form?.addEventListener('submit', (e) => {
  e.preventDefault();
  const ha = parseFloat(form.hectares.value) || 0;
  const crop = form.crop.value;
  const climate = form.climate.value;
  const current = form.current.value;

  const baseRevenuePerHa = CROP_BASE_USD[crop] || 1200;
  const savingsPct = Math.min(0.72, (SAVINGS_BY_CLIMATE[climate] || 0.3) + (SAVINGS_BONUS_BY_CURRENT[current] || 0));
  const waterCostPerHa = 350; // USD/ha/year (demo)
  const annualSavings = ha * waterCostPerHa * savingsPct + ha * baseRevenuePerHa * 0.08;
  const investment = ha * INVEST_PER_HA;
  const payback = investment / Math.max(annualSavings, 1);

  document.getElementById('roiSavings').textContent = `${Math.round(savingsPct * 100)}%`;
  document.getElementById('roiAnnual').textContent = `USD ${Math.round(annualSavings).toLocaleString('es-ES')}`;
  document.getElementById('roiPayback').textContent = payback.toFixed(1);

  const years = [1, 2, 3, 4, 5];
  const cumulative = years.map(y => Math.round(y * annualSavings - investment));
  if (chartInstance) chartInstance.destroy();
  const ctx = document.getElementById('roiChart');
  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: years.map(y => `Año ${y}`),
      datasets: [{
        label: 'Flujo acumulado (USD)',
        data: cumulative,
        backgroundColor: cumulative.map(v => v >= 0 ? '#70AD47' : '#DC2626'),
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { ticks: { callback: v => v.toLocaleString('es-ES') } } },
    },
  });

  results.hidden = false;
  results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
});
