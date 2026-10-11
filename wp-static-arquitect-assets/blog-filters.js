(() => {
  const form = document.querySelector('#ms-blog-filters');
  if (!form) return;
  const grid = document.querySelector('#ms-blog-grid');
  const cards = [...grid.children];
  const search = form.querySelector('[name=q]');
  const category = form.querySelector('[name=category]');
  const order = form.querySelector('#ms-blog-order');
  const since = form.querySelector('[name=since]');
  const more = document.querySelector('#ms-blog-more');
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  let limit = 12;
  const params = new URLSearchParams(location.search);
  const disclosure = form.closest('.ms-filter-details');
  const compact = window.matchMedia('(max-width: 620px)');
  function syncDisclosure() {
    if (disclosure) disclosure.open = !compact.matches || ['q', 'category', 'since'].some(key => params.get(key));
  }
  syncDisclosure();
  if (disclosure) disclosure.dataset.ready = 'true';
  compact.addEventListener('change', syncDisclosure);
  search.value = params.get('q') || '';
  category.value = params.get('category') || '';
  since.value = params.get('since') || '';
  function render(reset = true) {
    if (reset) limit = 12;
    const words = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    const filtered = cards.filter(card => (!category.value || card.dataset.category === category.value) && (!since.value || card.dataset.date >= since.value) && words.every(word => normalize(card.textContent).includes(word)));
    filtered.sort((a, b) => order.value === 'oldest' ? a.dataset.date.localeCompare(b.dataset.date) : b.dataset.date.localeCompare(a.dataset.date));
    cards.forEach(card => { card.hidden = true; });
    filtered.forEach((card, index) => { grid.append(card); card.hidden = index >= limit; });
    const visible = Math.min(limit, filtered.length);
    document.querySelector('#ms-blog-results').textContent = `${filtered.length} ${filtered.length === 1 ? 'artículo' : 'artículos'} · ${visible} ${visible === 1 ? 'visible' : 'visibles'}`;
    document.querySelector('#ms-blog-empty').hidden = filtered.length > 0;
    more.hidden = filtered.length <= limit;
    const next = new URL(location.href);
    for (const [key, value] of [['q', search.value], ['category', category.value], ['since', since.value]]) {
      if (value) next.searchParams.set(key, value); else next.searchParams.delete(key);
    }
    history.replaceState(null, '', next);
    grid.dataset.ready = 'true';
  }
  form.addEventListener('submit', event => { event.preventDefault(); render(); });
  form.addEventListener('input', () => render());
  form.addEventListener('reset', () => { setTimeout(() => render(), 0); });
  more.addEventListener('click', () => { limit += 12; render(false); });
  render();
})();
