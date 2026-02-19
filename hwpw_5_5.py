import asyncio
import json
import sys
import aiohttp
from datetime import datetime, timedelta
from aiohttp import web
from aiofile import async_open
from pathlib import Path

# Чітко визначаємо шлях до папки зі скриптом
BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "exchange.log"

# Параметри валют з консолі: python main.py USD EUR PLN
EXTRA_CURRENCIES = sys.argv[1:] if len(sys.argv) > 1 else ['USD', 'EUR']

async def log_to_file(message):
    """Асинхронне логування команди через aiofile"""
    async with async_open(LOG_FILE, mode='a', encoding='utf-8') as f:
        await f.write(f"[{datetime.now()}] {message}\n")

async def get_rates(days=1):
    """Отримання курсів через PrivatBank API"""
    if days > 10: days = 10
    results = []
    async with aiohttp.ClientSession() as session:
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%d.%m.%Y")
            try:
                async with session.get(f"https://api.privatbank.ua{date}") as resp:
                    data = await resp.json()
                    rates = {ex['currency']: {"sale": ex.get('saleRate'), "buy": ex.get('purchaseRate')}
                             for ex in data.get('exchangeRate', []) 
                             if ex.get('currency') in EXTRA_CURRENCIES}
                    results.append({date: rates})
            except Exception:
                results.append({date: "Error fetching data"})
    return json.dumps(results, indent=2, ensure_ascii=False)

async def index_handler(request):
    """Віддача вашого наявного index.html"""
    path = BASE_DIR / 'index.html'
    if path.exists():
        return web.FileResponse(path)
    return web.Response(text=f"Файл index.html не знайдено за шляхом: {path}", status=404)

async def ws_handler(request):
    """WebSocket чат"""
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            text = msg.data.strip()
            if text.startswith('exchange'):
                await log_to_file(f"Виконано команду: {text}")
                parts = text.split()
                days = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                rates = await get_rates(days)
                await ws.send_str(f"Курси ({', '.join(EXTRA_CURRENCIES)}):\n{rates}")
            else:
                await ws.send_str(f"Ви написали: {text}")
    return ws

async def main():
    app = web.Application()
    app.router.add_get('/', index_handler)
    app.router.add_get('/ws', ws_handler)
    # Якщо у вас є CSS або картинки, сервер їх знайде тут:
    app.router.add_static('/static/', path=BASE_DIR, name='static')

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 3000)
    
    print(f"🚀 Сервер запущено на http://localhost:3000")
    print(f"💰 Валюти для відстеження: {EXTRA_CURRENCIES}")
    
    await site.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
