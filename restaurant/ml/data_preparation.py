"""
Data preparation for restaurant-specific time series forecasting.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q
from django.utils import timezone
from restaurant.models import Order, OrderHistory
import logging

logger = logging.getLogger(__name__)


def get_order_timeseries(
    aggregation='daily',
    metric='total_amount',
    order_type=None,
    days_back=90,
    use_history=False
):
    """
    Get order time series data for forecasting.
    
    Args:
        aggregation: 'daily', 'weekly', or 'monthly'
        metric: 'total_amount', 'count', 'average_amount', 'items_count'
        order_type: None (all), 'delivery', 'dine_in', 'takeaway'
        days_back: Number of days of historical data to include
        use_history: Include OrderHistory (completed/cancelled orders)
    
    Returns:
        pandas.Series with DatetimeIndex
    """
    from .utils import prepare_timeseries_data
    
    # Set date filter - use timezone-aware datetime
    start_date = timezone.now() - timedelta(days=days_back)
    
    # Get active orders
    qs = Order.objects.filter(created_at__gte=start_date)
    
    # Filter by order type if specified
    if order_type:
        if order_type == 'delivery':
            qs = qs.filter(order_type='delivery')
        elif order_type == 'dine_in':
            qs = qs.filter(table__isnull=False)
        elif order_type == 'takeaway':
            qs = qs.filter(order_type='takeaway')
    
    # Include history if requested
    if use_history:
        # When using history, just use OrderHistory instead
        qs = OrderHistory.objects.filter(created_at__gte=start_date)
        
        if order_type:
            if order_type == 'delivery':
                qs = qs.filter(order_type='delivery')
            elif order_type == 'dine_in':
                qs = qs.filter(table__isnull=False)
            elif order_type == 'takeaway':
                qs = qs.filter(order_type='takeaway')
    
    return prepare_timeseries_data(qs, aggregation=aggregation, metric=metric)


def get_category_sales_timeseries(category_id, aggregation='daily', days_back=90):
    """
    Get sales time series for specific menu category.
    
    Args:
        category_id: Menu category ID
        aggregation: 'daily', 'weekly', or 'monthly'
        days_back: Days of historical data
    
    Returns:
        pandas.Series with sales for that category
    """
    from restaurant.models import OrderItem
    from .utils import prepare_timeseries_data
    
    start_date = datetime.now() - timedelta(days=days_back)
    
    qs = OrderItem.objects.filter(
        item__category_id=category_id,
        order__created_at__gte=start_date
    ).values('order__created_at').annotate(
        value=Sum('quantity')
    )
    
    df = pd.DataFrame(list(qs))
    if df.empty:
        return pd.Series(dtype=float)
    
    df.columns = ['created_at', 'value']
    df['created_at'] = pd.to_datetime(df['created_at'])
    df.set_index('created_at', inplace=True)
    
    freq_map = {'daily': 'D', 'weekly': 'W', 'monthly': 'MS'}
    freq = freq_map.get(aggregation, 'D')
    ts_data = df['value'].resample(freq).sum().fillna(0)
    
    return ts_data


def get_menu_item_timeseries(item_id, aggregation='daily', days_back=90):
    """
    Get sales time series for specific menu item.
    
    Args:
        item_id: Menu item ID
        aggregation: 'daily', 'weekly', 'monthly'
        days_back: Days of historical data
    
    Returns:
        pandas.Series with quantities sold
    """
    from restaurant.models import OrderItem
    
    start_date = datetime.now() - timedelta(days=days_back)
    
    qs = OrderItem.objects.filter(
        item_id=item_id,
        order__created_at__gte=start_date
    ).values('order__created_at').annotate(
        value=Sum('quantity')
    )
    
    df = pd.DataFrame(list(qs))
    if df.empty:
        return pd.Series(dtype=float)
    
    df.columns = ['created_at', 'value']
    df['created_at'] = pd.to_datetime(df['created_at'])
    df.set_index('created_at', inplace=True)
    
    freq_map = {'daily': 'D', 'weekly': 'W', 'monthly': 'MS'}
    freq = freq_map.get(aggregation, 'D')
    ts_data = df['value'].resample(freq).sum().fillna(0)
    
    return ts_data


def get_multi_series_forecast_data(aggregation='daily', days_back=90):
    """
    Get multiple time series for ensemble forecasting.
    
    Returns:
        dict: Multiple time series keyed by name
    """
    return {
        'total_revenue': get_order_timeseries(aggregation=aggregation, metric='total_amount', days_back=days_back),
        'total_orders': get_order_timeseries(aggregation=aggregation, metric='count', days_back=days_back),
        'delivery': get_order_timeseries(aggregation=aggregation, metric='total_amount', order_type='delivery', days_back=days_back),
        'takeaway': get_order_timeseries(aggregation=aggregation, metric='total_amount', order_type='takeaway', days_back=days_back),
        'dine_in': get_order_timeseries(aggregation=aggregation, metric='total_amount', order_type='dine_in', days_back=days_back),
    }


def get_forecast_statistics(forecast_dict):
    """
    Calculate statistics from forecast results.
    
    Args:
        forecast_dict: Dict with 'forecast', 'dates', etc. from model.forecast()
    
    Returns:
        dict: Summary statistics
    """
    if 'error' in forecast_dict:
        return {'error': forecast_dict['error']}
    
    forecast_values = np.array(forecast_dict['forecast'])
    
    return {
        'mean': float(np.mean(forecast_values)),
        'std': float(np.std(forecast_values)),
        'min': float(np.min(forecast_values)),
        'max': float(np.max(forecast_values)),
        'sum': float(np.sum(forecast_values)),
        'trend': 'increasing' if forecast_values[-1] > forecast_values[0] else 'decreasing',
        'volatility': float(np.std(np.diff(forecast_values))),
    }


def prepare_forecast_for_json(forecast_dict):
    """
    Prepare forecast results for JSON serialization.
    
    Args:
        forecast_dict: Forecast results from model.forecast()
    
    Returns:
        JSON-serializable dict
    """
    result = {}
    
    for key, value in forecast_dict.items():
        if isinstance(value, (list, tuple)):
            result[key] = [float(v) if isinstance(v, (int, float, np.number)) else v for v in value]
        elif isinstance(value, (int, float, np.number)):
            result[key] = float(value)
        else:
            result[key] = value
    
    return result
