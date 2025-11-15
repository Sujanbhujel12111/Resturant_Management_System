# home/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from restaurant.models import Order, Table, MenuItem
from django.db.models import Sum
from datetime import datetime, timedelta

class HomeView(TemplateView):
    template_name = 'home/index.html'

@login_required
def dashboard_view(request):
    # Get today's date
    today = datetime.now().date()
    
    context = {
        'pending_orders': Order.objects.filter(status='pending').count(),
        'active_tables': Table.objects.filter(is_occupied=True).count(),
        'total_menu_items': MenuItem.objects.filter(is_available=True).count(),
        'today_sales': Order.objects.filter(
            created_at__date=today,
            status='completed'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'recent_orders': Order.objects.order_by('-created_at')[:5]
    }
    return render(request, 'home/dashboard.html', context)

def about_view(request):
    return render(request, 'home/about.html')

def contact_view(request):
    return render(request, 'home/contact.html')