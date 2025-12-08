"""
Configuration for ML models and forecasting.
"""

# ARIMA Configuration
ARIMA_CONFIG = {
    'order': (1, 1, 1),  # (p, d, q) - default; auto_arima will optimize
    'seasonal_order': (1, 1, 1, 7),  # (P, D, Q, s) for weekly seasonality
    'auto_arima_enabled': True,
    'max_p': 5,
    'max_d': 2,
    'max_q': 5,
    'seasonal': True,
    'stepwise': True,
    'trace': False,
}

# Forecasting Configuration
FORECAST_CONFIG = {
    'default_periods': 30,  # forecast 30 days ahead by default
    'min_data_points': 14,  # minimum 14 data points to start forecasting
    'confidence_interval': 0.95,
}

# Data Aggregation
AGGREGATION_CONFIG = {
    'daily': 'D',      # daily aggregation
    'weekly': 'W',     # weekly aggregation
    'monthly': 'MS',   # monthly aggregation
}

# Feature Configuration
FEATURE_CONFIG = {
    'include_delivery': True,
    'include_dine_in': True,
    'include_takeaway': True,
    'by_category': False,  # forecast by menu category
}
