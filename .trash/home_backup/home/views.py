# home/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from restaurant.models import Order, Table, MenuItem
from django.db.models import Sum
from datetime import datetime, timedelta

from django.views import View
from django.shortcuts import render

class HomeView(View):
    def get(self, request):
        return render(request, 'home/login.html')



@login_required
def dashboard_view(request):
    today = datetime.now().date()

    pending_orders = Order.objects.exclude(status__in=['completed', 'cancelled']).count()
    active_tables = Table.objects.filter(is_occupied=True).count()
    total_menu_items = MenuItem.objects.filter(is_available=True).count()
    today_revenue = Order.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    recent_orders = Order.objects.order_by('-created_at')[:5]

    context = {
        'pending_orders': pending_orders,
        'active_tables': active_tables,
        'total_menu_items': total_menu_items,
        'today_revenue': today_revenue,
        'orders': recent_orders,
    }
    return render(request, 'restaurant/dashboard.html', context)





@login_required
def profile_view(request):
    return render(request, 'home/profile.html')

@login_required
def LogoutView(request):
    return render(request, 'home/logout.html')




def about_view(request):
    return render(request, 'home/about.html')




def contact_view(request):
    if request.method == 'POST':
        # Handle form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        # You can add logic to send an email or save the message to the database
        context = {
            'name': name,
            'email': email,
            'message': message,
            'success': True,
        }
        return render(request, 'home/contact.html', context)
    return render(request, 'home/contact.html')