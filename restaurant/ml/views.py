"""
Views and API endpoints for ML forecasting.
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from datetime import datetime

from restaurant.ml import (
    ARIMAForecast,
    auto_arima_fit,
    get_order_timeseries,
    get_multi_series_forecast_data,
    get_forecast_statistics,
    prepare_forecast_for_json,
    validate_timeseries,
)

logger = logging.getLogger(__name__)


@login_required
def forecast_dashboard(request):
    """
    Dashboard view for forecast visualization.
    """
    context = {
        'page_title': 'Demand Forecasting',
    }
    return render(request, 'restaurant/forecast_dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def generate_forecast(request):
    """
    API endpoint to generate forecast.
    
    Expected POST data:
    {
        'metric': 'total_amount' or 'count',
        'aggregation': 'daily', 'weekly', or 'monthly',
        'periods': 30,
        'order_type': null or 'delivery'/'takeaway'/'dine_in',
        'use_auto_arima': true/false,
        'days_back': 90
    }
    """
    try:
        data = json.loads(request.body)
        
        metric = data.get('metric', 'total_amount')
        aggregation = data.get('aggregation', 'daily')
        periods = int(data.get('periods', 30))
        order_type = data.get('order_type')
        use_auto_arima = data.get('use_auto_arima', True)
        days_back = int(data.get('days_back', 90))
        
        # Get time series data
        ts_data = get_order_timeseries(
            aggregation=aggregation,
            metric=metric,
            order_type=order_type,
            days_back=days_back,
            use_history=True
        )
        
        logger.info(f"Time series retrieved: {len(ts_data)} points, sum={ts_data.sum()}, mean={ts_data.mean():.2f}")
        
        # Validate
        is_valid, msg = validate_timeseries(ts_data, min_points=7)  # Relax to 7 points minimum
        if not is_valid:
            logger.warning(f"Validation failed: {msg}, data points: {len(ts_data)}")
            return JsonResponse({
                'success': False,
                'error': msg,
            }, status=400)
        
        # Fit model
        if use_auto_arima:
            model = auto_arima_fit(ts_data, name=f'forecast_{metric}_{order_type}')
            if model is None:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to fit auto_arima model',
                }, status=500)
        else:
            model = ARIMAForecast(name=f'forecast_{metric}_{order_type}')
            fit_result = model.fit(ts_data)
            if not fit_result['success']:
                return JsonResponse({
                    'success': False,
                    'error': fit_result.get('error', 'Model fit failed'),
                }, status=500)
        
        # Generate forecast
        forecast_dict = model.forecast(periods=periods, include_conf_int=True)
        
        # Get diagnostics
        diagnostics = model.get_diagnostics()
        
        # Calculate statistics
        stats = get_forecast_statistics(forecast_dict)
        
        return JsonResponse({
            'success': True,
            'forecast': prepare_forecast_for_json(forecast_dict),
            'diagnostics': diagnostics,
            'statistics': stats,
            'trained_at': model.last_trained.isoformat() if model.last_trained else None,
            'data_points': len(ts_data),
        })
    
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON',
        }, status=400)
    
    except Exception as e:
        logger.error(f"Error in generate_forecast: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@login_required
@require_http_methods(["POST"])
def multi_forecast(request):
    """
    Generate multiple forecasts (by order type, etc.).
    
    Expected POST data:
    {
        'aggregation': 'daily',
        'periods': 30,
        'days_back': 90,
        'use_auto_arima': true
    }
    """
    try:
        data = json.loads(request.body)
        
        aggregation = data.get('aggregation', 'daily')
        periods = int(data.get('periods', 30))
        days_back = int(data.get('days_back', 90))
        use_auto_arima = data.get('use_auto_arima', True)
        
        # Get all time series
        ts_dict = get_multi_series_forecast_data(aggregation=aggregation, days_back=days_back)
        
        results = {}
        for name, ts_data in ts_dict.items():
            is_valid, msg = validate_timeseries(ts_data)
            
            if not is_valid:
                results[name] = {'success': False, 'error': msg}
                continue
            
            try:
                if use_auto_arima:
                    model = auto_arima_fit(ts_data, name=f'multi_{name}')
                    if model is None:
                        results[name] = {'success': False, 'error': 'auto_arima failed'}
                        continue
                else:
                    model = ARIMAForecast(name=f'multi_{name}')
                    fit_result = model.fit(ts_data)
                    if not fit_result['success']:
                        results[name] = {'success': False, 'error': fit_result.get('error')}
                        continue
                
                forecast = model.forecast(periods=periods, include_conf_int=True)
                stats = get_forecast_statistics(forecast)
                
                results[name] = {
                    'success': True,
                    'forecast': prepare_forecast_for_json(forecast),
                    'statistics': stats,
                    'data_points': len(ts_data),
                }
            
            except Exception as e:
                logger.error(f"Error forecasting {name}: {e}")
                results[name] = {'success': False, 'error': str(e)}
        
        return JsonResponse({
            'success': True,
            'forecasts': results,
            'generated_at': datetime.now().isoformat(),
        })
    
    except Exception as e:
        logger.error(f"Error in multi_forecast: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@login_required
@require_http_methods(["GET"])
def forecast_status(request):
    """
    Get current forecasting status and model info.
    """
    return JsonResponse({
        'status': 'ready',
        'models_available': {
            'arima': True,
            'auto_arima': True,
            'sarimax': True,
        },
        'aggregations': ['daily', 'weekly', 'monthly'],
        'metrics': ['total_amount', 'count', 'average_amount', 'items_count'],
    })
