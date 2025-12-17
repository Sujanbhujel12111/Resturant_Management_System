from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

app_name = 'restaurant'

urlpatterns = [

    
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    path('kitchen/', views.kitchen_view, name='kitchen'),
    path('kitchen/orders/api/', views.kitchen_orders_api, name='kitchen_orders_api'),
    
    # Menu Management
    path('menu/', views.menu_view, name='menu'),
    path('menuitems/', views.MenuItemListView.as_view(), name='menuitem_list'),
    path('menuitem/create/', views.MenuItemCreateView.as_view(), name='menuitem_create'),
    path('menuitem/<int:pk>/', views.MenuItemDetailView.as_view(), name='menuitem_detail'),
    path('menuitem/<int:pk>/update/', views.MenuItemUpdateView.as_view(), name='menuitem_update'),
    path('menuitem/<int:pk>/delete/', views.MenuItemDeleteView.as_view(), name='menuitem_delete'),
    
    # Public Menu View
    path('menu/view/', views.public_menu_view, name='public_menu_view'),
    
    # QR Code Generation
    path('menu/qr-code/', views.generate_qr_code, name='generate_qr_code'),
    
    # Category Management
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('category/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('category/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Table Management
    path('tables/', views.TableListView.as_view(), name='table_list'),
    path('table/create/', views.TableCreateView.as_view(), name='table_create'),
    path('table/<int:pk>/update/', views.TableUpdateView.as_view(), name='table_update'),
    path('table/<int:pk>/delete/', views.TableDeleteView.as_view(), name='table_delete'),
    
    # Order Management - More specific patterns first
    path('order/close/<int:pk>/', views.close_order, name='close_order'),
    path('order/place/<int:table_id>/', views.place_order, name='place_order'),
    path('order/update_status/<int:pk>/', views.update_order_status, name='update_order_status'),
    path('order/process_payment/<int:pk>/', views.process_payment, name='process_payment'),
    path('order/bulk-cancel/', views.bulk_cancel_orders, name='bulk_cancel_orders'),
    
    # Order with primary key patterns
    path('order/<int:pk>/cancel/', views.cancel_order, name='cancel_order'),
    path('payment/<int:pk>/edit/', views.edit_payment, name='edit_payment'),
    path('payment/<int:pk>/delete/', views.delete_payment, name='delete_payment'),
    path('add_payment/<int:order_id>/', views.add_payment, name='add_payment'),
    
    # Order with string order_id patterns (less specific, come later)
    path('order_details/<str:order_id>/', views.order_details, name='order_details'),
    path('order/<str:order_id>/update_items/', views.update_order_items, name='update_order_items'),
    path('order/<str:order_id>/add_item/', views.add_order_item, name='add_order_item'),
    path('order/<str:order_id>/update_item/<int:item_id>/', views.update_order_item, name='update_order_item'),
    path('order/<str:order_id>/update_address/', views.update_order_address, name='update_order_address'),
    path('order/<str:order_id>/remove_item/<int:item_id>/', views.remove_order_item, name='remove_order_item'),
    
    # Other order lists
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    
    # Different Order Types
    path('place_order_takeaway/', views.place_order_takeaway, name='place_order_takeaway'),
    path('place_order_delivery/', views.place_order_delivery, name='place_order_delivery'),
    
    # Transaction History
    path('transaction_history/', views.transaction_history, name='transaction_history'),
    path('transaction_history/export/csv/', views.export_orders_csv, name='export_orders_csv'),
    path('transaction_history/export/pdf/', views.export_orders_pdf, name='export_orders_pdf'),
    path('order_history_details/<str:order_id>/', views.order_history_details, name='order_history_details'),
    path('order_update_notes/<str:order_id>/', views.order_update_notes, name='order_update_notes'),
    # serve a favicon shortcut to avoid 404 in dev
    path('favicon.ico', lambda request: __import__('django.shortcuts').shortcuts.redirect('/static/favicon.svg')),
    
    # ML / Forecasting
    path('ml/', include('restaurant.ml.urls')),




]