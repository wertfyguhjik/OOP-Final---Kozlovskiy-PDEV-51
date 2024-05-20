import requests
import json

class NegativeValueException(Exception):   # не пригодился в итоге
    pass
class NotDigitException(Exception):        # тоже не пригодился
    pass
class ConversionException(Exception):
    pass
class CryptoConverter:
    @staticmethod
    def get_price(quote, base, amount):
        if quote == base:
            raise ConversionException("Укажите разные валюты!")
        r = requests.get(f"https://min-api.cryptocompare.com/data/price?fsym={quote}&tsyms={base}")
        total_base = round((json.loads(r.content)[base] * amount), 4)
        return total_base

