"""
Utility functions for time series data preparation and preprocessing.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Sum, Count
import logging

logger = logging.getLogger(__name__)

def prepare_timeseries_data(orders_qs, aggregation='daily', metric='total_amount'):
    """
    Prepare time series data from order queryset.
    
    Args:
        orders_qs: Django ORM queryset of Order or OrderHistory objects
        aggregation: 'daily', 'weekly', or 'monthly'
        metric: 'total_amount', 'count', or 'average_amount'
    
    Returns:
        pandas.Series with DatetimeIndex and numeric values
    """
    logger.info(f"prepare_timeseries_data called: aggregation={aggregation}, metric={metric}, qs.count()={orders_qs.count()}")
    
    if not orders_qs.exists():
        logger.warning(f"No orders found for time series preparation")
        return pd.Series(dtype=float)
    
    # Map aggregation to pandas frequency
    freq_map = {'daily': 'D', 'weekly': 'W', 'monthly': 'MS'}
    freq = freq_map.get(aggregation, 'D')
    
    # Create base dataframe from queryset
    if metric == 'total_amount':
        df = pd.DataFrame(
            orders_qs.values('created_at').annotate(
                value=Sum('total_amount')
            ).values('created_at', 'value')
        )
    elif metric == 'count':
        df = pd.DataFrame(
            orders_qs.values('created_at').annotate(
                value=Count('id')
            ).values('created_at', 'value')
        )
    elif metric == 'average_amount':
        df = pd.DataFrame(
            orders_qs.values('created_at').annotate(
                value=Sum('total_amount') / Count('id')
            ).values('created_at', 'value')
        )
    else:
        raise ValueError(f"Unknown metric: {metric}")
    
    if df.empty:
        logger.warning(f"Empty dataframe for metric: {metric}")
        return pd.Series(dtype=float)
    
    # Convert to numeric, handle Decimal from Django
    df['value'] = pd.to_numeric(
        df['value'].apply(lambda x: float(x) if isinstance(x, Decimal) else x),
        errors='coerce'
    )
    
    # Set datetime index
    df['created_at'] = pd.to_datetime(df['created_at'])
    df.set_index('created_at', inplace=True)
    
    # Resample and aggregate
    ts_data = df['value'].resample(freq).sum()
    
    # Fill missing dates with 0 (no orders on that day)
    ts_data = ts_data.fillna(0)
    
    logger.info(f"Prepared time series: {len(ts_data)} periods, {ts_data.sum():.2f} total, freq={freq}")
    return ts_data


def handle_missing_dates(ts_data, method='forward_fill'):
    """
    Handle missing dates in time series.
    
    Args:
        ts_data: pandas.Series with DatetimeIndex
        method: 'forward_fill', 'backward_fill', 'interpolate', or 'zero'
    
    Returns:
        Cleaned pandas.Series
    """
    if ts_data.empty:
        return ts_data
    
    # Create complete date range
    date_range = pd.date_range(start=ts_data.index.min(), end=ts_data.index.max(), freq=ts_data.index.inferred_freq or 'D')
    ts_data = ts_data.reindex(date_range)
    
    if method == 'forward_fill':
        ts_data = ts_data.fillna(method='ffill')
    elif method == 'backward_fill':
        ts_data = ts_data.fillna(method='bfill')
    elif method == 'interpolate':
        ts_data = ts_data.interpolate(method='linear')
    elif method == 'zero':
        ts_data = ts_data.fillna(0)
    
    # Fill any remaining NaN at the start with backward fill
    ts_data = ts_data.bfill()
    
    return ts_data


def validate_timeseries(ts_data, min_points=14):
    """
    Validate time series data for forecasting.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if ts_data.empty:
        return False, "Time series is empty"
    
    if len(ts_data) < min_points:
        return False, f"Insufficient data points: {len(ts_data)} < {min_points}"
    
    if ts_data.isna().any():
        logger.warning(f"Time series contains NaN values: {ts_data.isna().sum()}")
    
    if (ts_data == 0).all():
        return False, "All values are zero"
    
    return True, "Valid"


def get_seasonality_period(ts_data):
    """
    Estimate seasonality period from time series data.
    
    Returns:
        int: Estimated seasonal period (7 for daily data with weekly pattern)
    """
    # For daily data, common seasonality is 7 (weekly)
    # For monthly data, common seasonality is 12 (yearly)
    freq = getattr(ts_data.index, 'inferred_freq', None)
    
    if freq == 'D':
        return 7
    elif freq in ['W', 'W-SUN', 'W-MON']:
        return 4  # ~4 weeks per month
    elif freq in ['MS', 'M']:
        return 12  # 12 months per year
    
    return 1  # No seasonality


def detrend_timeseries(ts_data, method='diff'):
    """
    Remove trend from time series.
    
    Args:
        ts_data: pandas.Series
        method: 'diff' (differencing) or 'detrend' (linear detrending)
    
    Returns:
        Detrended pandas.Series
    """
    if method == 'diff':
        return ts_data.diff().dropna()
    elif method == 'detrend':
        from scipy import signal
        detrended = signal.detrend(ts_data)
        return pd.Series(detrended, index=ts_data.index)
    
    return ts_data


def get_stationarity_info(ts_data):
    """
    Check stationarity of time series using ADF test.
    
    Returns:
        dict: {'stationary': bool, 'p_value': float, 'test_stat': float}
    """
    try:
        from statsmodels.tsa.stattools import adfuller
        result = adfuller(ts_data, autolag='AIC')
        
        return {
            'stationary': result[1] < 0.05,  # p-value < 0.05 means stationary
            'p_value': result[1],
            'test_stat': result[0],
            'critical_values': result[4],
        }
    except Exception as e:
        logger.error(f"Error in stationarity test: {e}")
        return {
            'stationary': None,
            'p_value': None,
            'test_stat': None,
            'critical_values': None,
        }
