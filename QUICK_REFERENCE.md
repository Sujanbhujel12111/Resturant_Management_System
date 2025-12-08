# QUICK REFERENCE GUIDE - ML Forecasting Module

## Installation (Copy & Paste)

```bash
pip install statsmodels pmdarima pandas numpy
python manage.py runserver
# Open: http://localhost:8000/restaurant/ml/forecast/
```

## 5-Minute Quick Start

### Via Web Dashboard

1. Go to `/restaurant/ml/forecast/`
2. Leave defaults or customize
3. Click "Generate Forecast"
4. View chart and statistics

### Via Python

```python
from restaurant.ml import get_order_timeseries, ARIMAForecast

ts = get_order_timeseries()
model = ARIMAForecast()
model.fit(ts)
forecast = model.forecast(periods=30)
print(forecast['forecast'][:5])
```

## Common Operations

### Load Data

```python
# By metric
from restaurant.ml import get_order_timeseries

ts = get_order_timeseries(metric='total_amount')    # Revenue
ts = get_order_timeseries(metric='count')           # Order count

# By order type
ts = get_order_timeseries(order_type='delivery')    # Delivery only
ts = get_order_timeseries(order_type='takeaway')    # Takeaway only
ts = get_order_timeseries(order_type='dine_in')     # Dine-in only

# By category
from restaurant.ml import get_category_sales_timeseries
ts = get_category_sales_timeseries(category_id=1)

# By item
from restaurant.ml import get_menu_item_timeseries
ts = get_menu_item_timeseries(item_id=5)

# Multiple series
from restaurant.ml import get_multi_series_forecast_data
ts_dict = get_multi_series_forecast_data()
```

### Create Models

```python
from restaurant.ml import ARIMAForecast, auto_arima_fit

# Manual ARIMA
model = ARIMAForecast(order=(1,1,1), name='manual')
model.fit(ts)

# Auto ARIMA (best parameters)
model = auto_arima_fit(ts, name='auto')
```

### Generate Forecasts

```python
# Basic forecast
forecast = model.forecast(periods=30)

# With confidence intervals
forecast = model.forecast(periods=30, include_conf_int=True)

# Access results
dates = forecast['dates']
values = forecast['forecast']
lower = forecast['lower_bound']
upper = forecast['upper_bound']
```

### Get Statistics

```python
from restaurant.ml import get_forecast_statistics

stats = get_forecast_statistics(forecast)
print(f"Mean: {stats['mean']}")
print(f"Trend: {stats['trend']}")
print(f"Volatility: {stats['volatility']}")
```

### Model Diagnostics

```python
diag = model.get_diagnostics()
print(f"AIC: {diag['aic']}")
print(f"BIC: {diag['bic']}")
print(f"Summary:\n{model.summary()}")
```

## API Endpoints

### Generate Single Forecast

```bash
POST /restaurant/ml/api/generate-forecast/
Content-Type: application/json

{
    "metric": "total_amount",
    "aggregation": "daily",
    "periods": 30,
    "order_type": null,
    "use_auto_arima": true,
    "days_back": 90
}
```

### Generate Multi Forecast

```bash
POST /restaurant/ml/api/multi-forecast/
{
    "aggregation": "daily",
    "periods": 30,
    "days_back": 90,
    "use_auto_arima": true
}
```

### Check Status

```bash
GET /restaurant/ml/api/status/
```

## Configuration

Edit `restaurant/ml/config.py`:

```python
# ARIMA order (p, d, q)
# p = autoregressive order
# d = differencing order (0=stationary, 1=trend, 2=curved)
# q = moving average order

ARIMA_CONFIG = {
    'order': (1, 1, 1),           # Change these
    'seasonal_order': (1, 1, 1, 7),
    'max_p': 5,
    'max_d': 2,
    'max_q': 5,
}

FORECAST_CONFIG = {
    'default_periods': 30,
    'min_data_points': 14,
}
```

## Troubleshooting

| Problem                  | Solution                           |
| ------------------------ | ---------------------------------- |
| ImportError: statsmodels | `pip install statsmodels pmdarima` |
| "Insufficient data"      | Use `days_back=90` or more         |
| Model slow               | Reduce `max_p`, `max_d`, `max_q`   |
| No data                  | Check database has orders          |
| Dashboard blank          | Check you're logged in             |

## Files to Know

| File                                                      | Purpose              |
| --------------------------------------------------------- | -------------------- |
| `restaurant/ml/models.py`                                 | ARIMA implementation |
| `restaurant/ml/data_preparation.py`                       | Load restaurant data |
| `restaurant/ml/views.py`                                  | API endpoints        |
| `restaurant/templates/restaurant/forecast_dashboard.html` | Web UI               |
| `SETUP_ML_MODULE.md`                                      | Full setup guide     |
| `restaurant/ml/README.md`                                 | Full documentation   |
| `restaurant/ml/example_usage.py`                          | Working examples     |

## Time Estimates

| Task                  | Time       |
| --------------------- | ---------- |
| Install               | 2 minutes  |
| First forecast (web)  | 1 minute   |
| First forecast (code) | 3 minutes  |
| Auto ARIMA tuning     | 20 seconds |
| Full multi-forecast   | 1 minute   |

## Example: Forecast Revenue for Next 30 Days

```python
from restaurant.ml import get_order_timeseries, auto_arima_fit, get_forecast_statistics

# Load 90 days of daily revenue
ts = get_order_timeseries(
    metric='total_amount',
    aggregation='daily',
    days_back=90
)

# Auto fit best model
model = auto_arima_fit(ts)

# Generate forecast
forecast = model.forecast(periods=30, include_conf_int=True)

# Display results
print("Revenue Forecast - Next 30 Days")
print("=" * 50)
for date, value, lower, upper in zip(
    forecast['dates'],
    forecast['forecast'],
    forecast['lower_bound'],
    forecast['upper_bound']
):
    print(f"{date}: Rs.{value:8.2f} ({lower:8.2f} - {upper:8.2f})")

# Statistics
stats = get_forecast_statistics(forecast)
print("\n" + "=" * 50)
print(f"Average: Rs.{stats['mean']:.2f}")
print(f"Total 30-day: Rs.{stats['sum']:.2f}")
print(f"Trend: {stats['trend']}")
```

## Key Concepts

**ARIMA = AutoRegressive Integrated Moving Average**

- **AR**: Uses past values to predict future
- **I**: Differencing to make stationary
- **MA**: Uses past errors to predict future

**Why ARIMA?**

- Perfect for time series with trends
- Captures seasonality (SARIMAX)
- Fast and reliable
- Interpretable results

**Confidence Intervals**

- 95% means 95% probability value falls within bounds
- Wider bounds = less confidence
- Use for risk assessment

## Next Steps

1. ✅ Install dependencies
2. ✅ Access dashboard
3. ✅ Generate first forecast
4. 📊 Monitor accuracy
5. 🔄 Retrain weekly
6. 📈 Optimize parameters
7. 🚀 Build on top (add to dashboards, automate, etc.)

## Resources

- **Web Dashboard**: `/restaurant/ml/forecast/`
- **Full Docs**: `restaurant/ml/README.md`
- **Examples**: `restaurant/ml/example_usage.py`
- **Setup**: `SETUP_ML_MODULE.md`
- **API Docs**: Run and check responses

## Support Commands

```bash
# Test installation
python -c "import statsmodels; print('OK')"

# Run examples
python manage.py shell < restaurant/ml/example_usage.py

# Check models
python manage.py shell
>>> from restaurant.ml import ARIMAForecast
>>> print(ARIMAForecast.__doc__)

# View configuration
python -c "from restaurant.ml import config; print(config.ARIMA_CONFIG)"
```

---

**Need Help?**

1. Check `SETUP_ML_MODULE.md` → Installation & Setup
2. Check `restaurant/ml/README.md` → Full Documentation
3. Check `restaurant/ml/example_usage.py` → Working Code Examples

**You're ready to forecast! 🚀**
