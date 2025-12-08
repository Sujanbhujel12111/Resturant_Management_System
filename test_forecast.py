from restaurant.ml import get_order_timeseries, ARIMAForecast

ts = get_order_timeseries()
print(f"Time series length: {len(ts)}")

model = ARIMAForecast()
result = model.fit(ts)
print(f"Fit result: {result}")

if result['success']:
    forecast = model.forecast(periods=30, include_conf_int=True)
    print(f"\nForecast generated successfully!")
    print(f"Forecast periods: {len(forecast['forecast'])}")
    print(f"First 5 forecasts: {forecast['forecast'][:5]}")
    print(f"\nForecast keys: {forecast.keys()}")
else:
    print(f"Error: {result}")
