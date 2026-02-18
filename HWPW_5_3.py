import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta
from pprint import pprint

class PrivatBankAPI:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates"

    async def fetch_rates(self, date_str: str):
        # Використовуємо params для автоматичного формування ?json&date=...
        params = {'json': '', 'date': date_str}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.BASE_URL, params=params, timeout=10) as response:
                    # Якщо сьогоднішня дата ще не в архіві, сервер може повернути 200 OK з HTML
                    if response.status == 200 and "application/json" in response.headers.get("Content-Type", ""):
                        return await response.json()
                    return None
            except Exception as e:
                print(f"Помилка мережі для {date_str}: {e}")
                return None

class RateService:
    def __init__(self, api_client: PrivatBankAPI):
        self.api_client = api_client

    async def get_currency_history(self, days: int, target_currencies: list):
        if days > 10:
            print("Обмеження: не більше 10 днів. Встановлено 10.")
            days = 10
        
        results = []
        for i in range(days):
            # Якщо за "сьогодні" (18.02.2026) даних ще немає, цикл перейде до вчора
            date_obj = datetime.now() - timedelta(days=i)
            date_str = date_obj.strftime("%d.%m.%Y")
            
            data = await self.api_client.fetch_rates(date_str)
            if data:
                rates = self._filter(data.get('exchangeRate', []), target_currencies)
                results.append({date_str: rates})
            else:
                print(f"Дані за {date_str} ще не доступні в архіві API.")
        
        return results

    def _filter(self, all_rates, targets):
        res = {}
        for r in all_rates:
            curr = r.get('currency')
            if curr in targets:
                # Пріоритет: комерційний курс -> курс НБУ
                res[curr] = {
                    'sale': r.get('saleRate', r.get('saleRateNB')),
                    'purchase': r.get('purchaseRate', r.get('purchaseRateNB'))
                }
        return res

async def main():
    try:
        days = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    except (ValueError, IndexError):
        days = 1

    extra = [c.upper() for c in sys.argv[2:]]
    currencies = ["USD", "EUR"] + extra

    api = PrivatBankAPI()
    service = RateService(api)

    print(f"Запит курсів для {currencies} за останні {days} дн.")
    result = await service.get_currency_history(days, currencies)
    
    if result:
        pprint(result)
    else:
        print("Спробуйте пізніше або виберіть дату за вчора (python script.py 2).")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())