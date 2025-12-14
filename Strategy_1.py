from abc import ABC, abstractmethod

# Стратегия оплаты
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

# Конкретные стратегии
class CreditCardPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Оплата {amount} руб. кредитной картой")

class PayPalPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Оплата {amount} руб. через PayPal")

class CryptoPayment(PaymentStrategy):
    def pay(self, amount):
        print(f"Оплата {amount} руб. криптовалютой")

# Контекст (корзина покупок)
class ShoppingCart:
    def __init__(self):
        self._items = []
        self._payment_strategy = None
    
    def add_item(self, item, price):
        self._items.append((item, price))
    
    def set_payment_strategy(self, strategy: PaymentStrategy):
        self._payment_strategy = strategy
    
    def checkout(self):
        total = sum(price for _, price in self._items)
        print(f"Итого: {total} руб.")
        if self._payment_strategy:
            self._payment_strategy.pay(total)
        else:
            print("Не выбран способ оплаты!")

# Использование
cart = ShoppingCart()
cart.add_item("Книга", 500)
cart.add_item("Наушники", 3000)

cart.set_payment_strategy(CreditCardPayment())
cart.checkout()
# Итого: 3500 руб.
# Оплата 3500 руб. кредитной картой

cart.set_payment_strategy(CryptoPayment())
cart.checkout()
# Итого: 3500 руб.
# Оплата 3500 руб. криптовалютой
