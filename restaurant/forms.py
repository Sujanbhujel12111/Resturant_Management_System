from django import forms
from .models import MenuItem, Category, Order, OrderItem, Payment
from .models import Table

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'category', 'is_available', 'preparation_area', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'})
        }



class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['number', 'capacity', 'is_occupied']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'is_active']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'special_notes']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['item', 'quantity']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': 1, 'value': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = MenuItem.objects.filter(is_available=True)
        # Add price data attribute to item choices
        self.fields['item'].widget.attrs['class'] = 'form-select'
        choices = []
        for item in self.fields['item'].queryset:
            choice = (item.id, f"{item.name} - ₹{item.price}")
            choices.append(choice)
        self.fields['item'].choices = [('', 'Select an item')] + choices

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'amount', 'transaction_id']