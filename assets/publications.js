<script>
document.addEventListener('DOMContentLoaded', () => {
  const catalog = document.querySelector('#publication-catalog');
  if (!catalog) return;
  const search = document.querySelector('#publication-search');
  const category = document.querySelector('#publication-category');
  const year = document.querySelector('#publication-year');
  const topic = document.querySelector('#publication-topic');
  const entries = [...catalog.querySelectorAll('.publication')];
  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const update = () => {
    const words = normalize(search.value).trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    entries.forEach(entry => {
      const match = words.every(word => normalize(entry.dataset.search).includes(word))
        && (!category.value || entry.dataset.category === category.value)
        && (!year.value || entry.dataset.year === year.value)
        && (!topic?.value || JSON.parse(entry.dataset.topics).includes(topic.value));
      entry.hidden = !match;
      visible += Number(match);
    });
    catalog.querySelectorAll('.publication-year').forEach(section => {
      section.hidden = ![...section.querySelectorAll('.publication')].some(entry => !entry.hidden);
    });
    document.querySelector('#catalog-summary').textContent = `${visible} of ${entries.length} records`;
    catalog.querySelector('.catalog-empty').hidden = visible > 0;
  };
  [search, category, year, topic].filter(Boolean).forEach(control => control.addEventListener('input', update));
  catalog.querySelector('.catalog-controls').hidden = false;
});
</script>
