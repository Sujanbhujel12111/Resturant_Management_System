from django import template
from django.db.models import Sum

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def sum_payments(payments):
    """Calculate the total sum of all payments"""
    return payments.aggregate(Sum('amount'))['amount__sum'] or 0

@register.filter
def subtract(value, arg):
    """Subtract the argument from the value"""
    return value - arg