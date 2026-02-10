from django.db import models

class Order(models.Model):
    # Define your fields here
    order_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_id}"