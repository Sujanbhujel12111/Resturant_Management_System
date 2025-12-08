"""
ML Module for Restaurant Management System
Time series forecasting using ARIMA and related statistical models.
"""

from .models import ARIMAForecast, auto_arima_fit, multi_step_forecast
from .utils import (
    prepare_timeseries_data,
    handle_missing_dates,
    validate_timeseries,
    get_seasonality_period,
    detrend_timeseries,
    get_stationarity_info,
)
from .data_preparation import (
    get_order_timeseries,
    get_category_sales_timeseries,
    get_menu_item_timeseries,
    get_multi_series_forecast_data,
    get_forecast_statistics,
    prepare_forecast_for_json,
)
from . import config

__all__ = [
    'ARIMAForecast',
    'auto_arima_fit',
    'multi_step_forecast',
    'prepare_timeseries_data',
    'handle_missing_dates',
    'validate_timeseries',
    'get_seasonality_period',
    'detrend_timeseries',
    'get_stationarity_info',
    'get_order_timeseries',
    'get_category_sales_timeseries',
    'get_menu_item_timeseries',
    'get_multi_series_forecast_data',
    'get_forecast_statistics',
    'prepare_forecast_for_json',
    'config',
]
