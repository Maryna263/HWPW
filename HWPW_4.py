import json
import socket
import urllib.parse
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread

# Налаштування шляхів та портів
BASE_DIR = Path(__file__).parent
STORAGE_DIR = BASE_DIR / 'storage'
STORAGE_FILE = STORAGE_DIR / 'data.json'

HTTP_PORT = 3000
SOCKET_PORT = 5000

class MyHTTPHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Маршрутизація для сторінок та статичних ресурсів"""
        pr_url = urllib.parse.urlparse(self.path)
        path = pr_url.path

        if path == '/':
            self.send_static('index.html')
        elif path == '/message':
            self.send_static('message.html')
        else:
            # Обробка статики (style.css, logo.png) або помилка 404
            filename = path.lstrip('/')
            if (BASE_DIR / filename).exists() and filename != "":
                self.send_static(filename)
            else:
                self.send_static('error.html', 404)

    def do_POST(self):
        """Обробка форми та пересилка даних через Socket (UDP)"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        
        # Відправка байт-рядка на Socket сервер
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(body.encode(), ('127.0.0.1', SOCKET_PORT))
        sock.close()

        # Редирект на головну після успішної відправки
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_static(self, filename, status=200):
        """Метод для відправки файлів клієнту"""
        file_path = BASE_DIR / filename
        
        # Визначення типу контенту
        mimetype = 'text/html'
        if filename.endswith('.css'): mimetype = 'text/css'
        elif filename.endswith('.png'): mimetype = 'image/png'
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            self.send_response(status)
            self.send_header('Content-type', mimetype)
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            # Якщо навіть error.html зник, віддаємо простий текст
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

def run_socket_server():
    """Socket сервер для збереження даних у JSON"""
    STORAGE_DIR.mkdir(exist_ok=True)
    if not STORAGE_FILE.exists():
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('127.0.0.1', SOCKET_PORT))
    
    while True:
        data, _ = sock.recvfrom(1024)
        parse_data = urllib.parse.parse_qs(data.decode())
        
        # Формуємо запис: витягуємо перший елемент списку для чистого рядка
        new_entry = {
            str(datetime.now()): {
                "username": parse_data.get('username', [''])[0],
                "message": parse_data.get('message', [''])[0]
            }
        }
        
        # Читання та оновлення файлу data.json
        try:
            with open(STORAGE_FILE, 'r+', encoding='utf-8') as f:
                try:
                    current_data = json.load(f)
                except json.JSONDecodeError:
                    current_data = {}
                
                current_data.update(new_entry)
                f.seek(0)
                f.truncate()
                json.dump(current_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Помилка запису в JSON: {e}")

def run_http_server():
    """HTTP сервер на порту 3000"""
    server = HTTPServer(('0.0.0.0', HTTP_PORT), MyHTTPHandler)
    print(f"Веб-додаток запущено на http://localhost:{HTTP_PORT}")
    server.serve_forever()

if __name__ == '__main__':
    # Перевірка наявності файлів перед стартом
    required = ['index.html', 'message.html', 'error.html', 'style.css', 'logo.png']
    for f in required:
        if not (BASE_DIR / f).exists():
            print(f"ПОМИЛКА: Файл {f} не знайдено в папці зі скриптом!")

    # Запуск серверів у різних потоках
    Thread(target=run_http_server, daemon=True).start()
    run_socket_server()