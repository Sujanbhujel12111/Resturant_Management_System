let forecastChart = null;

function showMessage(type, text) {
    const id = type === 'success' ? 'successMessage' : 'errorMessage';
    const el = document.getElementById(id);
    el.textContent = text;
    el.style.display = 'block';
    setTimeout(() => el.style.display = 'none', 5000);
}

function showLoading(show = true) {
    document.getElementById('loadingSpinner').style.display = show ? 'block' : 'none';
}

function generateSingleForecast() {
    showLoading(true);

    const payload = {
        metric: document.getElementById('metricSelect').value,
        aggregation: document.getElementById('aggregationSelect').value,
        order_type: document.getElementById('orderTypeSelect').value || null,
        periods: parseInt(document.getElementById('periodsInput').value),
        days_back: parseInt(document.getElementById('daysBackInput').value),
        use_auto_arima: document.getElementById('autoArimaCheckbox').checked,
    };

    fetch('/restaurant/ml/forecast/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(payload),
    })
        .then(response => response.json())
        .then(data => {
            showLoading(false);

            if (data.success) {
                displayForecast(data);
                showMessage('success', 'Forecast generated successfully!');
            } else {
                showMessage('error', data.error || 'Failed to generate forecast');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showMessage('error', 'Error generating forecast');
        });
}

function generateMultiForecast() {
    showLoading(true);

    const payload = {
        aggregation: document.getElementById('aggregationSelect').value,
        periods: parseInt(document.getElementById('periodsInput').value),
        days_back: parseInt(document.getElementById('daysBackInput').value),
        use_auto_arima: document.getElementById('autoArimaCheckbox').checked,
    };

    fetch('/restaurant/ml/multi-forecast/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(payload),
    })
        .then(response => response.json())
        .then(data => {
            showLoading(false);

            if (data.success) {
                displayMultiForecast(data);
                showMessage('success', 'Multi-forecast generated successfully!');
            } else {
                showMessage('error', data.error || 'Failed to generate forecast');
            }
        })
        .catch(error => {
            showLoading(false);
            console.error('Error:', error);
            showMessage('error', 'Error generating forecast');
        });
}

function displayForecast(data) {
    document.getElementById('resultsSection').style.display = 'grid';
    document.getElementById('diagnosticsSection').style.display = 'block';

    const forecast = data.forecast;
    const stats = data.statistics;
    const diag = data.diagnostics;

    // Format currency/numbers
    const formatValue = (v, decimals = 2) => {
        if (typeof v !== 'number') return '-';
        return v.toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    };

    // Update stats
    document.getElementById('statMean').textContent = formatValue(stats.mean);
    document.getElementById('statStd').textContent = formatValue(stats.std);
    document.getElementById('statMin').textContent = formatValue(stats.min);
    document.getElementById('statMax').textContent = formatValue(stats.max);
    document.getElementById('statSum').textContent = formatValue(stats.sum);
    document.getElementById('statTrend').textContent = (stats.trend || '-').toUpperCase();

    // Update diagnostics
    document.getElementById('diagAIC').textContent = formatValue(diag.aic);
    document.getElementById('diagBIC').textContent = formatValue(diag.bic);
    document.getElementById('diagLoglik').textContent = formatValue(diag.loglik);
    document.getElementById('diagResMean').textContent = formatValue(diag.residuals_mean, 6);
    document.getElementById('diagResStd').textContent = formatValue(diag.residuals_std, 6);
    document.getElementById('diagDataPoints').textContent = data.data_points;

    // Draw chart
    drawForecastChart(forecast);
}

function displayMultiForecast(data) {
    const forecasts = data.forecasts;
    alert('Multi-forecast results:\n' + JSON.stringify(forecasts, null, 2));
    // You can enhance this with a table or grid view
}

function drawForecastChart(forecast) {
    const ctx = document.getElementById('forecastChart').getContext('2d');

    const dates = forecast.dates || [];
    const values = forecast.forecast || [];
    const lower = forecast.lower_bound || [];
    const upper = forecast.upper_bound || [];

    if (forecastChart) {
        forecastChart.destroy();
    }

    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates.map(d => {
                const date = new Date(d);
                return date.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric'
                });
            }),
            datasets: [
                {
                    label: 'Forecast',
                    data: values,
                    borderColor: '#17a2b8',
                    backgroundColor: 'rgba(0, 102, 204, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 3,
                    pointBackgroundColor: '#17a2b8',
                },
                ...(lower.length > 0 ? [{
                    label: '95% Lower Bound',
                    data: lower,
                    borderColor: 'rgba(0, 102, 204, 0.3)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                }] : []),
                ...(upper.length > 0 ? [{
                    label: '95% Upper Bound',
                    data: upper,
                    borderColor: 'rgba(0, 102, 204, 0.3)',
                    borderWidth: 1,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0,
                }] : []),
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Value',
                    },
                },
            },
        },
    });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
