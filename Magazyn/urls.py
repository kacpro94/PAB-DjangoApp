from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    # np. http://127.0.0.1:8000/shop/product/5/
    path("", views.stock_list_view, name="stock_list"),
    path("product/<int:product_id>/", views.order_product_view, name="order_product"),
    path("orders/", views.order_list_view, name="order_list"),
]