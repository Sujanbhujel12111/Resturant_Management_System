# ML Forecasting Module - Restaurant Management System

## Overview

This ML module provides **ARIMA-based time series forecasting** for restaurant order analysis. It enables demand prediction, revenue forecasting, and trend analysis using statistical models.

## Features

- **ARIMA/SARIMAX Models**: Automatic and manual time series forecasting
- **Auto ARIMA**: Automatic parameter optimization for best model fit
- **Multiple Metrics**: Forecast revenue, order counts, average values, and item quantities
- **Flexible Aggregation**: Daily, weekly, or monthly data aggregation
- **Confidence Intervals**: Generate 95% confidence bounds for predictions
- **Multi-Series Forecasting**: Forecast by order type (delivery, dine-in, takeaway)
- **Category & Item Analysis**: Predict sales for specific menu categories or items
- **Web Dashboard**: Interactive forecasting interface with visualization
- **Model Diagnostics**: AIC, BIC, residual analysis for model validation

## Installation

### 1. Install Required Packages

```bash
pip install statsmodels pmdarima pandas numpy
```

### 2. Dependencies

- **statsmodels**: Core ARIMA/SARIMAX implementation
- **pmdarima**: Auto ARIMA parameter selection
- **pandas**: Time series data manipulation
- **numpy**: Numerical computations

## Quick Start

### Using Django Shell

```bash
python manage.py shell
```

```python
from restaurant.ml import get_order_timeseries, ARIMAForecast

# Load historical data
ts_data = get_order_timeseries(
    aggregation='daily',
    metric='total_amount',
    days_back=90,
    use_history=True
)

# Create and fit model
model = ARIMAForecast(name='revenue_forecast')
model.fit(ts_data)

# Generate 30-day forecast
forecast = model.forecast(periods=30, include_conf_int=True)
print(forecast)
```

### Using the Web Dashboard

1. Navigate to: `/restaurant/ml/forecast/`
2. Configure settings:
   - **Metric**: Choose what to forecast (Revenue, Order Count, etc.)
   - **Aggregation**: Select time period (Daily, Weekly, Monthly)
   - **Order Type**: Filter by delivery/takeaway/dine-in
   - **Forecast Periods**: Number of periods to predict
   - **Auto ARIMA**: Enable automatic parameter tuning
3. Click "Generate Forecast"
4. View results with chart, statistics, and model diagnostics

## Module Structure

```
restaurant/ml/
├── __init__.py              # Module exports
├── config.py                # Configuration parameters
├── models.py                # ARIMA/SARIMAX implementations
├── utils.py                 # Data preprocessing utilities
├── data_preparation.py      # Restaurant-specific data loaders
├── views.py                 # API endpoints and views
├── urls.py                  # URL routes
├── example_usage.py         # Usage examples
└── README.md               # This file
```

## Core Classes & Functions

### ARIMAForecast Class

```python
from restaurant.ml import ARIMAForecast

# Initialize
model = ARIMAForecast(
    order=(1, 1, 1),           # ARIMA order (p, d, q)
    seasonal_order=(1, 1, 1, 7), # Seasonal order (P, D, Q, s)
    name='my_model'
)

# Fit to data
fit_result = model.fit(ts_data)  # Returns dict with AIC, BIC, etc.

# Generate forecast
forecast = model.forecast(
    periods=30,
    include_conf_int=True  # Include 95% confidence intervals
)

# Get model info
diagnostics = model.get_diagnostics()
summary = model.summary()

# Save/load
model.save('/path/to/model.pkl')
loaded_model = ARIMAForecast.load('/path/to/model.pkl')
```

### Auto ARIMA

```python
from restaurant.ml import auto_arima_fit

# Automatic parameter optimization
model = auto_arima_fit(
    ts_data,
    name='auto_model',
    max_p=5,
    max_d=2,
    max_q=5,
    seasonal=True,
    stepwise=True
)

forecast = model.forecast(periods=30)
```

### Data Loading Functions

```python
from restaurant.ml import (
    get_order_timeseries,
    get_category_sales_timeseries,
    get_menu_item_timeseries,
    get_multi_series_forecast_data,
)

# Total revenue forecast
ts_revenue = get_order_timeseries(
    aggregation='daily',
    metric='total_amount',
    order_type='delivery',  # or 'takeaway', 'dine_in', None
    days_back=90,
    use_history=True
)

# Category sales
ts_category = get_category_sales_timeseries(
    category_id=1,
    aggregation='daily',
    days_back=90
)

# Menu item sales
ts_item = get_menu_item_timeseries(
    item_id=5,
    aggregation='daily',
    days_back=90
)

# Multiple series (delivery, takeaway, dine-in, total)
ts_dict = get_multi_series_forecast_data(
    aggregation='daily',
    days_back=90
)
```

### Utility Functions

```python
from restaurant.ml import (
    validate_timeseries,
    get_forecast_statistics,
    get_stationarity_info,
)

# Validate data
is_valid, message = validate_timeseries(ts_data, min_points=14)

# Calculate forecast stats
stats = get_forecast_statistics(forecast_dict)
# Returns: mean, std, min, max, sum, trend, volatility

# Check stationarity (required for ARIMA)
stationarity = get_stationarity_info(ts_data)
# Returns: stationary (bool), p_value, test_stat, critical_values
```

## API Endpoints

All endpoints require authentication.

### POST `/restaurant/ml/api/generate-forecast/`

Generate a single forecast.

**Request:**

```json
{
  "metric": "total_amount",
  "aggregation": "daily",
  "periods": 30,
  "order_type": null,
  "use_auto_arima": true,
  "days_back": 90
}
```

**Response:**

```json
{
    "success": true,
    "forecast": {
        "forecast": [1200.50, 1250.75, ...],
        "dates": ["2024-01-01", "2024-01-02", ...],
        "lower_bound": [...],
        "upper_bound": [...]
    },
    "diagnostics": {
        "aic": 1234.56,
        "bic": 1256.78,
        "loglik": -615.28,
        "residuals_mean": 0.001,
        "residuals_std": 45.23
    },
    "statistics": {
        "mean": 1250.0,
        "std": 80.5,
        "min": 950.0,
        "max": 1500.0,
        "sum": 37500.0,
        "trend": "increasing",
        "volatility": 25.3
    },
    "trained_at": "2024-01-15T10:30:00",
    "data_points": 90
}
```

### POST `/restaurant/ml/api/multi-forecast/`

Generate forecasts for multiple order types.

**Request:**

```json
{
  "aggregation": "daily",
  "periods": 30,
  "days_back": 90,
  "use_auto_arima": true
}
```

**Response:**

```json
{
    "success": true,
    "forecasts": {
        "total_revenue": {...},
        "total_orders": {...},
        "delivery": {...},
        "takeaway": {...},
        "dine_in": {...}
    },
    "generated_at": "2024-01-15T10:30:00"
}
```

### GET `/restaurant/ml/api/status/`

Check forecasting module status.

**Response:**

```json
{
  "status": "ready",
  "models_available": {
    "arima": true,
    "auto_arima": true,
    "sarimax": true
  },
  "aggregations": ["daily", "weekly", "monthly"],
  "metrics": ["total_amount", "count", "average_amount", "items_count"]
}
```

## Configuration

Edit `restaurant/ml/config.py` to customize:

```python
# ARIMA settings
ARIMA_CONFIG = {
    'order': (1, 1, 1),              # Default (p, d, q)
    'seasonal_order': (1, 1, 1, 7),  # Default (P, D, Q, s)
    'auto_arima_enabled': True,
    'max_p': 5,                      # Auto ARIMA max p
    'max_d': 2,                      # Auto ARIMA max d
    'max_q': 5,                      # Auto ARIMA max q
}

# Forecasting defaults
FORECAST_CONFIG = {
    'default_periods': 30,           # Default forecast length
    'min_data_points': 14,           # Minimum historical data
    'confidence_interval': 0.95,     # Confidence level
}
```

## Usage Examples

### Example 1: Simple Revenue Forecast

```python
from restaurant.ml import get_order_timeseries, ARIMAForecast

# Load 90 days of revenue data
ts = get_order_timeseries(
    aggregation='daily',
    metric='total_amount',
    days_back=90
)

# Fit and forecast
model = ARIMAForecast(name='revenue')
model.fit(ts)
forecast = model.forecast(periods=30)

# Extract values
for date, value in zip(forecast['dates'], forecast['forecast']):
    print(f"{date}: Rs.{value:.2f}")
```

### Example 2: Forecast with Confidence Intervals

```python
from restaurant.ml import auto_arima_fit, get_forecast_statistics

ts = get_order_timeseries(metric='count', days_back=90)
model = auto_arima_fit(ts)

forecast = model.forecast(periods=30, include_conf_int=True)

# Access bounds
for i, (date, value) in enumerate(zip(forecast['dates'], forecast['forecast'])):
    lower = forecast['lower_bound'][i]
    upper = forecast['upper_bound'][i]
    print(f"{date}: {value:.0f} (±{upper - value:.0f})")
```

### Example 3: Category Sales Forecast

```python
from restaurant.ml import get_category_sales_timeseries, ARIMAForecast

# Forecast sales for a specific category
ts = get_category_sales_timeseries(category_id=1, days_back=90)

model = ARIMAForecast(name='category_1_sales')
model.fit(ts)
forecast = model.forecast(periods=30)
```

## Interpreting Results

### Forecast Output

- **forecast**: Point estimates for each period
- **dates**: Forecast dates
- **lower_bound**: Lower 95% confidence limit
- **upper_bound**: Upper 95% confidence limit

### Diagnostics

- **AIC/BIC**: Model fit quality (lower is better)
- **Residuals**: Forecast errors should be small and normally distributed
- **Data Points**: Number of historical observations used

### Statistics

- **Trend**: Is the forecast increasing or decreasing?
- **Volatility**: Variability in forecasted values
- **Mean/Min/Max**: Expected range of values

## Best Practices

1. **Data Quality**: Ensure 14+ days of historical data
2. **Stationarity**: Check if data is stationary; difference if needed
3. **Seasonality**: Daily data often has 7-day (weekly) patterns
4. **Confidence Intervals**: Use lower/upper bounds for risk assessment
5. **Model Validation**: Review diagnostics and residuals
6. **Regular Updates**: Retrain models with new data weekly
7. **Multiple Forecasts**: Compare across order types for insights

## Troubleshooting

### "Insufficient data points"

- Need at least 14 days of historical data
- Solution: Load more historical data with `days_back` parameter

### "Model failed to converge"

- Data may not be stationary
- Solution: Try with differenced data or shorter time period

### "Auto ARIMA takes too long"

- Large p/q/d search space
- Solution: Reduce `max_p`, `max_d`, `max_q` or disable `stepwise=False`

### statsmodels/pmdarima import errors

- Packages not installed
- Solution: `pip install statsmodels pmdarima`

## Performance Notes

- Daily forecasting: ~1-2 seconds per model
- Auto ARIMA: 10-30 seconds depending on data size
- Multi-forecast (5 series): 30-60 seconds
- Dashboard should cache results

## Future Enhancements

- [ ] Prophet model support
- [ ] LSTM neural networks
- [ ] Ensemble methods
- [ ] Anomaly detection
- [ ] Automated retraining
- [ ] Export forecast reports
- [ ] API rate limiting
- [ ] Historical forecast comparison

## References

- [statsmodels documentation](https://www.statsmodels.org/)
- [pmdarima auto_arima](https://alkaline-ml.com/pmdarima/)
- [ARIMA Theory](https://en.wikipedia.org/wiki/Autoregressive_integrated_moving_average)
- [Time Series Analysis](https://otexts.com/fpp2/)

## Support

For issues or questions:

1. Check troubleshooting section above
2. Review example_usage.py
3. Check Django logs for errors
4. Ensure all dependencies are installed
