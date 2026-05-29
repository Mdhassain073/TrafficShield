// TrafficShield — Dashboard Chart
// Fetches real alert data from /api/alerts-data and renders a Chart.js bar chart

async function loadChart() {
  const ctx = document.getElementById('chart');
  if (!ctx) return;

  try {
    const response = await fetch('/api/alerts-data');
    const data = await response.json();

    if (!data.labels || data.labels.length === 0) {
      ctx.parentElement.innerHTML = '<p style="color: #888; text-align: center;">No alert data to display yet.</p>';
      return;
    }

    // Color-code bars by severity
    const colors = data.scores.map(score => {
      if (score >= 0.95) return '#f44336';      // Critical — red
      else if (score >= 0.8) return '#ff9800';   // Warning — orange
      else return '#4caf50';                      // Normal — green
    });

    new Chart(ctx.getContext('2d'), {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Anomaly Score',
          data: data.scores,
          backgroundColor: colors,
          borderColor: colors.map(c => c),
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            max: 1.0,
            ticks: { color: '#aaa' },
            grid: { color: '#333' }
          },
          x: {
            ticks: { color: '#aaa' },
            grid: { color: '#333' }
          }
        },
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Top 10 Suspicious IP Anomaly Scores',
            color: '#0f0',
            font: { size: 14 }
          }
        }
      }
    });
  } catch (error) {
    console.error('Failed to load chart data:', error);
  }
}

// Load chart when page is ready
document.addEventListener('DOMContentLoaded', loadChart);
