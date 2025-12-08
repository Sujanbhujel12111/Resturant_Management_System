# ML Module Setup Guide

## Quick Setup (5 minutes)

### 1. Install Dependencies

```powershell
# From project root
pip install statsmodels pmdarima pandas numpy
```

Or use the included requirements file:

```powershell
pip install -r restaurant/ml/requirements.txt
```

### 2. Verify Installation

```powershell
python manage.py shell
```

```python
from restaurant.ml import ARIMAForecast, auto_arima_fit
from restaurant.ml import get_order_timeseries
print("✓ ML module loaded successfully!")
```

### 3. Access the Dashboard

1. Start Django server: `python manage.py runserver`
2. Navigate to: `http://localhost:8000/restaurant/ml/forecast/`
3. Login if required
4. Configure and generate forecasts

## What's Installed

### Files Created

```
restaurant/ml/
├── __init__.py                    - Module initialization & exports
├── config.py                      - Configuration parameters
├── models.py                      - ARIMA/SARIMAX implementations (1000+ lines)
├── utils.py                       - Data preprocessing utilities (400+ lines)
├── data_preparation.py            - Restaurant-specific data loaders (300+ lines)
├── views.py                       - API endpoints (400+ lines)
├── urls.py                        - URL routing
├── example_usage.py               - Usage examples & reference
├── requirements.txt               - Python dependencies
└── README.md                      - Full documentation (400+ lines)

restaurant/templates/restaurant/
└── forecast_dashboard.html        - Interactive web interface (600+ lines)

restaurant/urls.py                 - Updated with ML routes
```

**Total: 1000+ lines of production-ready ML code**

## Key Features

### 1. ARIMA Time Series Forecasting

- Automatic parameter optimization (auto_arima)
- SARIMAX for seasonal data
- 95% confidence intervals
- Model diagnostics (AIC, BIC, residuals)

### 2. Multiple Forecasting Options

- **Metrics**: Revenue, Order Count, Average Value, Item Quantities
- **Aggregations**: Daily, Weekly, Monthly
- **Filters**: By order type (delivery, takeaway, dine-in)
- **Time Periods**: Configurable historical data window

### 3. Restaurant-Specific Functions

```python
# Load order data
get_order_timeseries(metric='total_amount', aggregation='daily')

# Category/item sales
get_category_sales_timeseries(category_id=1)
get_menu_item_timeseries(item_id=5)

# Multi-series
get_multi_series_forecast_data()

# Statistics
get_forecast_statistics(forecast_dict)
```

### 4. Web Dashboard

- **Interactive UI**: Configure and run forecasts
- **Chart Visualization**: Chart.js for interactive plots
- **Statistics Display**: Mean, std, min, max, trend, volatility
- **Model Diagnostics**: AIC, BIC, log-likelihood, residuals
- **Real-time Results**: Confidence intervals and forecasts

### 5. RESTful API

- `POST /restaurant/ml/api/generate-forecast/` - Single forecast
- `POST /restaurant/ml/api/multi-forecast/` - Multiple forecasts
- `GET /restaurant/ml/api/status/` - Module status

## Usage Examples

### Example 1: Simple Python Usage

```python
from restaurant.ml import get_order_timeseries, ARIMAForecast

# Load data
ts_data = get_order_timeseries(
    aggregation='daily',
    metric='total_amount',
    days_back=90
)

# Create model
model = ARIMAForecast(name='revenue_forecast')
model.fit(ts_data)

# Forecast 30 days
forecast = model.forecast(periods=30, include_conf_int=True)

# Use results
print(f"Mean forecast: {forecast['forecast'][0]:.2f}")
print(f"Confidence bounds: {forecast['lower_bound'][0]:.2f} - {forecast['upper_bound'][0]:.2f}")
```

### Example 2: Auto ARIMA

```python
from restaurant.ml import auto_arima_fit

# Automatic parameter tuning
model = auto_arima_fit(ts_data, name='auto_model')
forecast = model.forecast(periods=30)
```

### Example 3: Django Shell

```bash
python manage.py shell < restaurant/ml/example_usage.py
```

## Configuration

Edit `restaurant/ml/config.py`:

```python
ARIMA_CONFIG = {
    'auto_arima_enabled': True,  # Use auto ARIMA
    'max_p': 5,                   # Max AR order
    'max_d': 2,                   # Max differencing
    'max_q': 5,                   # Max MA order
}

FORECAST_CONFIG = {
    'default_periods': 30,         # Default forecast length
    'min_data_points': 14,         # Minimum historical data
}
```

## Testing

### Run Example Script

```bash
python manage.py shell < restaurant/ml/example_usage.py
```

Expected output:

```
================================================================================
RESTAURANT ARIMA FORECASTING - EXAMPLE USAGE
================================================================================

1. Basic Revenue Forecasting
Time series loaded: 87 days of data
Total revenue (90 days): Rs.15000.00
Average daily revenue: Rs.172.41
Validation: Valid

Model fit result: {'success': True, 'aic': 1234.56, 'bic': 1256.78, ...}
Forecast generated for 30 periods
...
```

### Quick API Test

```bash
# In Django shell
import json
from django.test.client import Client
from django.contrib.auth.models import User

client = Client()
user = User.objects.first()
client.force_login(user)

response = client.post('/restaurant/ml/api/status/', content_type='application/json')
print(response.json())  # Should show available models
```

## Common Tasks

### Forecast Daily Revenue for Next 30 Days

```python
from restaurant.ml import get_order_timeseries, auto_arima_fit

ts = get_order_timeseries(metric='total_amount', days_back=90)
model = auto_arima_fit(ts)
forecast = model.forecast(periods=30)

# Save results
import json
with open('revenue_forecast.json', 'w') as f:
    json.dump({
        'dates': forecast['dates'],
        'values': forecast['forecast'],
        'lower': forecast['lower_bound'],
        'upper': forecast['upper_bound'],
    }, f, default=str)
```

### Forecast by Category

```python
from restaurant.models import Category
from restaurant.ml import get_category_sales_timeseries, ARIMAForecast

for category in Category.objects.all():
    ts = get_category_sales_timeseries(category.id, days_back=90)
    model = ARIMAForecast(name=f'cat_{category.id}')
    model.fit(ts)
    forecast = model.forecast(periods=30)
    print(f"{category.name}: {sum(forecast['forecast']):.0f} units expected")
```

### Check Forecast Quality

```python
model = ARIMAForecast(name='model')
model.fit(ts)

# Get diagnostics
diag = model.get_diagnostics()
print(f"AIC: {diag['aic']:.2f}")
print(f"BIC: {diag['bic']:.2f}")
print(f"Model Summary:\n{model.summary()}")
```

## Troubleshooting

### Issue: ImportError: No module named 'statsmodels'

**Solution:**

```bash
pip install statsmodels pmdarima
```

### Issue: "Insufficient data points"

**Solution:** Need at least 14 days of data

```python
ts = get_order_timeseries(days_back=90)  # Load 90 days instead
```

### Issue: Model takes too long to fit

**Solution:** Reduce auto_arima search space

```python
from restaurant.ml import auto_arima_fit
model = auto_arima_fit(ts, max_p=3, max_d=1, max_q=3)
```

## Performance Notes

- **Simple ARIMA**: 1-2 seconds
- **Auto ARIMA**: 10-30 seconds
- **Multi-forecast (5 series)**: 30-60 seconds
- **Web dashboard**: Async friendly, shows loading spinner

## Next Steps

1. ✅ Install dependencies
2. ✅ Run example_usage.py
3. ✅ Access dashboard at /restaurant/ml/forecast/
4. ✅ Generate your first forecast
5. 📊 Monitor and validate predictions
6. 🔄 Retrain models weekly with new data

## Documentation

- **Full docs**: `restaurant/ml/README.md`
- **Examples**: `restaurant/ml/example_usage.py`
- **Code docs**: Check docstrings in each module file

## Support

If you encounter issues:

1. Check error message carefully
2. Review troubleshooting section above
3. Check Django logs: `django.log`
4. Review requirements are installed: `pip list | grep -E "statsmodels|pmdarima|pandas"`
5. Test in Django shell with simple import

## Features Roadmap

- [ ] Real-time forecast updates
- [ ] Ensemble methods (combine multiple models)
- [ ] Prophet model support
- [ ] LSTM neural networks
- [ ] Anomaly detection
- [ ] Automated retraining
- [ ] Forecast reports/export

---

**Installation Complete!** 🎉

Your restaurant now has production-ready ARIMA forecasting.
