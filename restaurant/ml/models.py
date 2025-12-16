"""
ARIMA and time series forecasting models.
"""

import pandas as pd
import numpy as np
import logging
import pickle
import json
from datetime import datetime, timedelta
from pathlib import Path
from django.conf import settings
import os

logger = logging.getLogger(__name__)

# Lazy imports to avoid issues if statsmodels not installed
try:
    from statsmodels.tsa.arima.model import ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from statsmodels.tsa.stattools import adfuller
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    logger.warning("statsmodels not installed. ARIMA models will not be available.")

try:
    from pmdarima import auto_arima
    AUTO_ARIMA_AVAILABLE = True
except ImportError:
    AUTO_ARIMA_AVAILABLE = False
    logger.warning("pmdarima not installed. auto_arima will not be available.")


class ARIMAForecast:
    """
    ARIMA forecasting model wrapper.
    
    Handles model training, forecasting, and prediction.
    """
    
    def __init__(self, order=(1, 1, 1), seasonal_order=(1, 1, 1, 7), name='default'):
        """
        Initialize ARIMA model.
        
        Args:
            order: (p, d, q) tuple
            seasonal_order: (P, D, Q, s) tuple for SARIMAX
            name: Model identifier
        """
        if not STATSMODELS_AVAILABLE:
            raise ImportError("statsmodels is required for ARIMA models. Install it with: pip install statsmodels")
        
        self.order = order
        self.seasonal_order = seasonal_order
        self.name = name
        self.model = None
        self.model_fit = None
        self.ts_data = None
        self.forecast_results = None
        self.last_trained = None
        
    def fit(self, ts_data):
        """
        Fit ARIMA model to time series data.
        
        Args:
            ts_data: pandas.Series with DatetimeIndex
        
        Returns:
            dict: Training results with AIC, BIC, etc.
        """
        if ts_data.empty or len(ts_data) < 2:
            raise ValueError("Time series must have at least 2 data points")
        
        self.ts_data = ts_data
        
        try:
            # Use SARIMAX for seasonal data, ARIMA for non-seasonal
            if self.seasonal_order[3] > 1:  # s > 1 means seasonal
                self.model = SARIMAX(
                    ts_data,
                    order=self.order,
                    seasonal_order=self.seasonal_order,
                    enforce_stationarity=False,
                    enforce_invertibility=False,
                )
            else:
                self.model = ARIMA(ts_data, order=self.order)
            
            self.model_fit = self.model.fit()
            self.last_trained = datetime.now()
            
            logger.info(f"Model '{self.name}' fitted successfully. AIC: {self.model_fit.aic:.2f}")
            
            return {
                'success': True,
                'aic': float(self.model_fit.aic),
                'bic': float(self.model_fit.bic),
                'loglik': float(self.model_fit.llf),
                'message': 'Model fitted successfully',
            }
        
        except Exception as e:
            logger.error(f"Error fitting model: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to fit model',
            }
    
    def forecast(self, periods=30, include_conf_int=True):
        """
        Generate forecast.
        
        Args:
            periods: Number of periods to forecast
            include_conf_int: Include confidence intervals
        
        Returns:
            dict: Forecast results with dates and values
        """
        if self.model_fit is None:
            raise ValueError("Model must be fitted before forecasting. Call fit() first.")
        
        try:
            # Handle both statsmodels and pmdarima ARIMA objects
            model_type = type(self.model_fit).__name__
            
            # Check if this is a statsmodels model (has get_forecast method)
            if hasattr(self.model_fit, 'get_forecast') and model_type not in ['ARIMA', 'AutoArimaModel']:
                # statsmodels ARIMA
                forecast_result = self.model_fit.get_forecast(steps=periods)
                forecast_values = forecast_result.predicted_mean.values
                
                # Get confidence intervals from statsmodels
                try:
                    conf_int = forecast_result.conf_int(alpha=0.05)
                    conf_int_results = (conf_int.iloc[:, 0].values, conf_int.iloc[:, 1].values)
                except Exception as e:
                    logger.warning(f"Could not get confidence intervals: {e}")
                    conf_int_results = None
                
                logger.info(f"Used statsmodels forecast method (model type: {model_type})")
                
            elif hasattr(self.model_fit, 'predict'):
                # pmdarima ARIMA uses predict for out-of-sample forecasts
                try:
                    forecast_values, conf_int_results = self.model_fit.get_forecast(steps=periods, return_conf_int=True, alpha=0.05)
                    logger.info(f"Used pmdarima get_forecast method (model type: {model_type})")
                except (AttributeError, TypeError):
                    # Fallback: use simple predict
                    forecast_values = self.model_fit.predict(n_periods=periods)
                    conf_int_results = None
                    logger.info(f"Used pmdarima predict method (model type: {model_type})")
            else:
                raise ValueError(f"Unknown model type: {model_type}")
            
            # Generate future dates
            last_date = self.ts_data.index[-1]
            freq = self.ts_data.index.inferred_freq or 'D'
            future_dates = pd.date_range(start=last_date, periods=periods + 1, freq=freq)[1:]
            
            # Convert forecast values to list
            if hasattr(forecast_values, 'tolist'):
                forecast_list = forecast_values.tolist()
            else:
                forecast_list = list(forecast_values)
            
            # Prepare results
            results = {
                'forecast': forecast_list,
                'dates': [d.isoformat() for d in future_dates],
                'periods': periods,
            }
            
            # Add confidence intervals if requested
            if include_conf_int and conf_int_results is not None:
                lower, upper = conf_int_results
                results['lower_bound'] = lower.tolist() if hasattr(lower, 'tolist') else list(lower)
                results['upper_bound'] = upper.tolist() if hasattr(upper, 'tolist') else list(upper)
            elif include_conf_int:
                # Fallback: use +/- standard error
                try:
                    std_err = np.std([forecast_list[i] - forecast_list[i-1] if i > 0 else forecast_list[0] for i in range(len(forecast_list))])
                    results['lower_bound'] = [v - 1.96 * std_err for v in forecast_list]
                    results['upper_bound'] = [v + 1.96 * std_err for v in forecast_list]
                except Exception as e:
                    logger.debug(f"Could not compute confidence interval bounds: {e}")
            
            self.forecast_results = results
            logger.info(f"Generated forecast for {periods} periods")
            
            return results
        
        except Exception as e:
            logger.error(f"Error during forecasting: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
            }
    
    def get_diagnostics(self):
        """
        Get model diagnostics.
        
        Returns:
            dict: Model diagnostics (AIC, BIC, residuals, etc.)
        """
        if self.model_fit is None:
            return {'error': 'Model not fitted'}
        
        try:
            # Handle both statsmodels and pmdarima - they have different attribute/method types
            # resid can be a property or method
            if callable(self.model_fit.resid):
                residuals = self.model_fit.resid()
            else:
                residuals = self.model_fit.resid
            
            try:
                aic_val = self.model_fit.aic() if callable(self.model_fit.aic) else float(self.model_fit.aic)
            except (AttributeError, TypeError):
                aic_val = None
            
            try:
                bic_val = self.model_fit.bic() if callable(self.model_fit.bic) else float(self.model_fit.bic)
            except (AttributeError, TypeError):
                bic_val = None
            
            try:
                llf_val = self.model_fit.llf() if callable(self.model_fit.llf) else float(self.model_fit.llf)
            except (AttributeError, TypeError):
                llf_val = None
            
            diagnostics = {
                'aic': aic_val,
                'bic': bic_val,
                'loglik': llf_val,
                'residuals_mean': float(residuals.mean()),
                'residuals_std': float(residuals.std()),
                'ljungbox_pvalue': None,
            }
            
            # Try to get Ljung-Box test p-value
            try:
                from statsmodels.stats.diagnostic import acorr_ljungbox
                lb_result = acorr_ljungbox(residuals, lags=10, return_df=True)
                diagnostics['ljungbox_pvalue'] = float(lb_result['lb_pvalue'].mean())
            except Exception as e:
                logger.debug(f"Could not compute Ljung-Box test: {e}")
            
            return diagnostics
        except Exception as e:
            logger.error(f"Error getting diagnostics: {e}", exc_info=True)
            return {'error': str(e)}
    
    def summary(self):
        """Get model summary as string."""
        if self.model_fit is None:
            return "Model not fitted"
        return str(self.model_fit.summary())
    
    def save(self, filepath=None):
        """
        Save model to disk.
        
        Args:
            filepath: Path to save model (default: settings.MEDIA_ROOT/models/model_name.pkl)
        """
        if self.model_fit is None:
            raise ValueError("Model not fitted")
        
        if filepath is None:
            model_dir = Path(settings.MEDIA_ROOT) / 'ml_models'
            model_dir.mkdir(parents=True, exist_ok=True)
            filepath = model_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self.model_fit, f)
            logger.info(f"Model saved to {filepath}")
            return {'success': True, 'filepath': str(filepath)}
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def load(cls, filepath):
        """Load model from disk."""
        try:
            with open(filepath, 'rb') as f:
                model_fit = pickle.load(f)
            instance = cls()
            instance.model_fit = model_fit
            logger.info(f"Model loaded from {filepath}")
            return instance
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None


def auto_arima_fit(ts_data, name='auto_arima', **kwargs):
    """
    Fit ARIMA model using auto_arima for automatic parameter selection.
    
    Args:
        ts_data: pandas.Series with DatetimeIndex
        name: Model identifier
        **kwargs: Additional arguments for pmdarima.auto_arima
    
    Returns:
        ARIMAForecast instance or None if error
    """
    if not AUTO_ARIMA_AVAILABLE:
        raise ImportError("pmdarima is required for auto_arima. Install it with: pip install pmdarima")
    
    if ts_data.empty or len(ts_data) < 14:
        logger.error("Time series too short for auto_arima (min 14 points)")
        return None
    
    try:
        # Default parameters for auto_arima
        # DISABLED seasonal=True because it causes "no more samples after seasonal differencing" error
        # For restaurant data, daily seasonality is less important than capturing trend
        default_params = {
            'max_p': 5,
            'max_d': 2,
            'max_q': 5,
            'seasonal': False,  # Disable seasonal differencing to avoid error
            'stepwise': True,
            'trace': False,
            # 'm': 7,  # Removed: not used when seasonal=False
            'suppress_warnings': True,  # Suppress deprecation warnings
        }
        default_params.update(kwargs)
        
        # Run auto_arima
        best_model = auto_arima(ts_data, **default_params)
        
        # Create ARIMAForecast instance with found parameters
        order = best_model.order
        seasonal_order = best_model.seasonal_order
        
        logger.info(f"auto_arima found: order={order}, seasonal_order={seasonal_order}")
        
        forecast_model = ARIMAForecast(order=order, seasonal_order=seasonal_order, name=name)
        
        # Use the fitted model directly
        forecast_model.ts_data = ts_data
        forecast_model.model_fit = best_model
        forecast_model.last_trained = datetime.now()
        
        return forecast_model
    
    except Exception as e:
        logger.error(f"Error in auto_arima: {e}")
        return None


def multi_step_forecast(ts_data_dict, periods=30):
    """
    Create forecasts for multiple time series (e.g., by order type).
    
    Args:
        ts_data_dict: dict with keys as series names and values as pandas.Series
        periods: Forecast periods
    
    Returns:
        dict: Forecasts for each series
    """
    results = {}
    
    for name, ts_data in ts_data_dict.items():
        try:
            model = ARIMAForecast(name=name)
            fit_result = model.fit(ts_data)
            
            if fit_result['success']:
                forecast = model.forecast(periods=periods)
                results[name] = forecast
            else:
                results[name] = {'error': fit_result.get('error', 'Unknown error')}
        
        except Exception as e:
            logger.error(f"Error forecasting {name}: {e}")
            results[name] = {'error': str(e)}
    
    return results
