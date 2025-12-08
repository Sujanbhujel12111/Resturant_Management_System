"""
Example usage of the ML forecasting module.
Run from Django shell: python manage.py shell < restaurant/ml/example_usage.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_project.settings')
django.setup()

from restaurant.ml import (
    ARIMAForecast,
    auto_arima_fit,
    get_order_timeseries,
    get_multi_series_forecast_data,
    validate_timeseries,
    get_forecast_statistics,
)

print("=" * 80)
print("RESTAURANT ARIMA FORECASTING - EXAMPLE USAGE")
print("=" * 80)

# Example 1: Basic ARIMA forecasting for total revenue
print("\n1. Basic Revenue Forecasting")
print("-" * 80)

ts_revenue = get_order_timeseries(
    aggregation='daily',
    metric='total_amount',
    days_back=90,
    use_history=True
)

print(f"Time series loaded: {len(ts_revenue)} days of data")
print(f"Total revenue (90 days): Rs.{ts_revenue.sum():.2f}")
print(f"Average daily revenue: Rs.{ts_revenue.mean():.2f}")

# Validate
is_valid, msg = validate_timeseries(ts_revenue)
print(f"Validation: {msg}")

if is_valid:
    # Fit model
    model = ARIMAForecast(name='revenue_daily')
    fit_result = model.fit(ts_revenue)
    print(f"Model fit result: {fit_result}")
    
    # Forecast 30 days ahead
    forecast = model.forecast(periods=30, include_conf_int=True)
    print(f"Forecast generated for {forecast['periods']} periods")
    print(f"Forecast values: {[round(v, 2) for v in forecast['forecast'][:5]]}... (showing first 5)")
    
    # Get statistics
    stats = get_forecast_statistics(forecast)
    print(f"Forecast statistics:")
    print(f"  Mean: Rs.{stats['mean']:.2f}")
    print(f"  Min: Rs.{stats['min']:.2f}")
    print(f"  Max: Rs.{stats['max']:.2f}")
    print(f"  Trend: {stats['trend']}")
    
    # Get diagnostics
    diag = model.get_diagnostics()
    print(f"Model diagnostics:")
    print(f"  AIC: {diag['aic']:.2f}")
    print(f"  BIC: {diag['bic']:.2f}")


# Example 2: Auto ARIMA with automatic parameter selection
print("\n\n2. Auto ARIMA Forecasting (Parameter Optimization)")
print("-" * 80)

ts_orders = get_order_timeseries(
    aggregation='daily',
    metric='count',
    days_back=90,
    use_history=True
)

print(f"Time series loaded: {len(ts_orders)} days of data")
print(f"Total orders (90 days): {int(ts_orders.sum())}")
print(f"Average daily orders: {ts_orders.mean():.1f}")

is_valid, msg = validate_timeseries(ts_orders)
print(f"Validation: {msg}")

if is_valid:
    print("Running auto_arima (this may take a moment)...")
    model = auto_arima_fit(ts_orders, name='orders_daily', trace=True)
    
    if model:
        forecast = model.forecast(periods=30, include_conf_int=True)
        stats = get_forecast_statistics(forecast)
        
        print(f"\nAuto ARIMA completed successfully")
        print(f"Forecast statistics:")
        print(f"  Mean orders: {stats['mean']:.1f}")
        print(f"  Max orders: {stats['max']:.1f}")
        print(f"  Trend: {stats['trend']}")


# Example 3: Multi-series forecasting (by order type)
print("\n\n3. Multi-Series Forecasting (By Order Type)")
print("-" * 80)

ts_dict = get_multi_series_forecast_data(aggregation='daily', days_back=90)

for name, ts_data in ts_dict.items():
    is_valid, _ = validate_timeseries(ts_data)
    
    if is_valid:
        try:
            model = ARIMAForecast(name=f'multi_{name}')
            fit_result = model.fit(ts_data)
            
            if fit_result['success']:
                forecast = model.forecast(periods=30, include_conf_int=False)
                forecast_sum = sum(forecast['forecast'])
                
                print(f"{name.upper()}: 30-day forecast total = {forecast_sum:.2f}")
        except Exception as e:
            print(f"{name.upper()}: Error - {e}")


# Example 4: Time series by category
print("\n\n4. Category-Based Forecasting")
print("-" * 80)

from restaurant.models import Category
from restaurant.ml import get_category_sales_timeseries

categories = Category.objects.all()[:3]  # Get first 3 categories

for category in categories:
    ts_category = get_category_sales_timeseries(category.id, aggregation='daily', days_back=90)
    
    if len(ts_category) > 0:
        is_valid, _ = validate_timeseries(ts_category)
        
        if is_valid:
            try:
                model = ARIMAForecast(name=f'category_{category.name}')
                fit_result = model.fit(ts_category)
                
                if fit_result['success']:
                    forecast = model.forecast(periods=30, include_conf_int=False)
                    forecast_sum = sum(forecast['forecast'])
                    
                    print(f"{category.name}: 30-day forecast = {forecast_sum:.0f} units")
            except Exception as e:
                print(f"{category.name}: Error - {e}")


print("\n" + "=" * 80)
print("FORECASTING EXAMPLES COMPLETE")
print("=" * 80)
print("\nNOTE: To use in your Django application:")
print("1. Import from restaurant.ml module")
print("2. Call get_order_timeseries() to load data")
print("3. Use ARIMAForecast or auto_arima_fit to fit models")
print("4. Call .forecast() to generate predictions")
print("5. Use the web dashboard at /restaurant/ml/forecast/")
