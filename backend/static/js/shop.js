// Compare bar logic
const COMPARE_KEY = 'compare_ids';
const compareBar = document.getElementById('compareBar');
const compareCount = document.getElementById('compareCount');
const compareGo = document.getElementById('compareGo');
const compareClear = document.getElementById('compareClear');

const getCompareIds = () => {
  try { return JSON.parse(localStorage.getItem(COMPARE_KEY) || '[]'); }
  catch { return []; }
};
const setCompareIds = (ids) => localStorage.setItem(COMPARE_KEY, JSON.stringify(ids));

const refreshCompareBar = () => {
  const ids = getCompareIds();
  if (!compareBar) return;
  compareBar.hidden = ids.length === 0;
  if (compareCount) compareCount.textContent = ids.length;
  if (compareGo) compareGo.href = '/shop/compare?ids=' + ids.join(',');
  document.querySelectorAll('.js-compare').forEach(b => {
    const id = parseInt(b.dataset.productId, 10);
    b.classList.toggle('active', ids.includes(id));
  });
};

document.addEventListener('click', (e) => {
  const btn = e.target.closest('.js-compare');
  if (!btn) return;
  e.preventDefault();
  const id = parseInt(btn.dataset.productId, 10);
  let ids = getCompareIds();
  if (ids.includes(id)) {
    ids = ids.filter(x => x !== id);
  } else {
    if (ids.length >= 4) { toast('Maximo 4 productos para comparar', 'warn'); return; }
    ids.push(id);
  }
  setCompareIds(ids);
  refreshCompareBar();
});

if (compareClear) {
  compareClear.addEventListener('click', () => { setCompareIds([]); refreshCompareBar(); });
}

refreshCompareBar();

// Auto-submit on filter change
const filterForm = document.getElementById('filterForm');
if (filterForm) {
  filterForm.querySelectorAll('select').forEach(s => s.addEventListener('change', () => filterForm.submit()));
}
