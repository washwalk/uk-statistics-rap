async function loadData() {
  const response = await fetch('data/indicators.json');
  if (!response.ok) throw new Error('Could not load dashboard data');
  return response.json();
}

function groupByIndicator(rows) {
  return rows.reduce((acc, row) => {
    acc[row.indicator_id] = acc[row.indicator_id] || [];
    acc[row.indicator_id].push(row);
    return acc;
  }, {});
}

function recentRows(rows) {
  return rows.slice(Math.max(rows.length - 60, 0));
}

loadData().then((data) => {
  const select = document.getElementById('indicatorSelect');
  const grouped = groupByIndicator(data.series);
  const latestById = Object.fromEntries(data.latest.map((row) => [row.indicator_id, row]));

  data.latest.forEach((row) => {
    const option = document.createElement('option');
    option.value = row.indicator_id;
    option.textContent = row.indicator;
    select.appendChild(option);
  });

  const ctx = document.getElementById('trendChart');
  let chart;

  function render(indicatorId) {
    const rows = recentRows(grouped[indicatorId]);
    const latest = latestById[indicatorId];
    if (chart) chart.destroy();
    chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: rows.map((row) => row.period),
        datasets: [{
          label: `${latest.indicator} (${latest.unit})`,
          data: rows.map((row) => row.value),
          borderColor: '#005ea5',
          backgroundColor: 'rgba(0, 94, 165, 0.12)',
          fill: true,
          tension: 0.25,
          pointRadius: 0
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: { x: { ticks: { maxTicksLimit: 8 } } }
      }
    });
  }

  select.addEventListener('change', () => render(select.value));
  render(data.latest[0].indicator_id);
}).catch((error) => {
  document.querySelector('.panel').insertAdjacentHTML('beforeend', `<p>${error.message}</p>`);
});
