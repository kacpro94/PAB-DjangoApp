from django.shortcuts import render
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from .models import Product, Stock, Order

def place_order_service(product_id, requested_quantity):
    """
    Funkcja realizująca atomowy proces zamówienia.
    Zwraca: (True, order_object) w przypadku sukcesu
    Zwraca: (False, missing_quantity) w przypadku braku towaru
    """
    # Uruchamiamy transakcję atomową bazy danych
    with transaction.atomic():
        # .select_for_update() blokuje ten wiersz w bazie danych. 
        # Inny użytkownik próbujący kupić ten sam produkt poczeka, aż ta transakcja się zakończy.
        try:
            stock = Stock.objects.select_for_update().get(product_id=product_id)
        except Stock.DoesNotExist:
            return False, requested_quantity

        # Weryfikacja dostępności
        if stock.quantity >= requested_quantity:
            # Sukces: Zmniejszamy stan magazynowy
            stock.quantity -= requested_quantity
            stock.save()

            # Tworzymy zamówienie
            order = Order.objects.create(
                product_id=product_id,
                ordered_quantity=requested_quantity,
                status='COMPLETED'
            )
            return True, order
        else:
            # Porażka: Obliczamy ile brakuje
            missing_qty = requested_quantity - stock.quantity
            return False, missing_qty

def order_product_view(request, product_id):
    """
    Widok obsługujący wysłanie formularza zamówienia.
    URL: /Magazyn/order/<product_id>/
    """
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            quantity = 1

        # Wywołujemy funkcję z punktu 1.
        success, result = place_order_service(product.id, quantity)

        if success:
            # 'result' to obiekt nowo utworzonego zamówienia (Order)
            return render(request, 'Magazyn/success.html', {'order': result})
        else:
            # 'result' to liczba brakujących sztuk
            context = {
                'product': product,
                'missing_quantity': result,
                'requested_quantity': quantity
            }
            return render(request, 'Magazyn/error_no_stock.html', context)
            
    # Jeśli to żądanie GET, po prostu wyświetlamy stronę produktu z formularzem
    return render(request, 'Magazyn/product_detail.html', {'product': product})

def stock_list_view(request):
    """
    Widok wyświetlający listę wszystkich produktów i ich stanów magazynowych.
    """
    # Pobieramy produkty razem z ich stanami magazynowymi
    products = Product.objects.select_related('stock').all()
    return render(request, 'Magazyn/stock_list.html', {'products': products})


def order_list_view(request):
    """
    Widok wyświetlający historię wszystkich zamówień.
    """
    # Pobieramy zamówienia od najnowszych do najstarszych (-created_at)
    orders = Order.objects.select_related('product').all().order_by('-created_at')
    return render(request, 'Magazyn/order_list.html', {'orders': orders})