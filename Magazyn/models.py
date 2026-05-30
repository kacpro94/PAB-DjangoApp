from django.db import models
from django.core.validators import MinValueValidator
# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nazwa produktu")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cena")
    description = models.TextField(blank=True, verbose_name="Opis")

    def __str__(self):
        return self.name
    

class Stock(models.Model):
    """
    Stan magazynowy przypisany do produktu. 
    Wydzielony, aby ułatwić operacje blokowania wierszy bazy danych (select_for_update).
    """
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="stock")
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name="Dostępna ilość")

    def __str__(self):
        return f"{self.product.name} - Stan: {self.quantity}"
    
class Order(models.Model):
    """Rejestr złożonych zamówień."""
    STATUS_CHOICES = [
        ('PENDING', 'Oczekujące'),
        ('COMPLETED', 'Zrealizowane'),
        ('FAILED', 'Anulowane/Błąd'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Produkt")
    ordered_quantity = models.PositiveIntegerField(verbose_name="Zamówiona ilość")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Data zamówienia")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Zamówienie #{self.id} - {self.product.name} ({self.ordered_quantity} szt.)"