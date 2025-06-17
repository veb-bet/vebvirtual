# ss_parser.py
import base64
import re
from urllib.parse import unquote, urlparse

def parse_ss_link(ss_url: str):
    try:
        # Проверка формата ссылки
        if not ss_url.startswith("ss://"):
            raise ValueError("Ссылка должна начинаться с ss://")

        # Удаление префикса и анкора
        clean_url = ss_url[5:].split('#')[0]

        # SIP002 ссылка (base64 всей конфигурации)
        if '@' not in clean_url and clean_url.count(':') == 0:
            # Добавляем padding при необходимости
            padding = '=' * (4 - len(clean_url) % 4)
            decoded = base64.urlsafe_b64decode(clean_url + padding).decode('utf-8')
            
            # Проверяем наличие обязательных компонентов
            if '@' not in decoded or ':' not in decoded:
                raise ValueError("Неверный формат SIP002 ссылки")
                
            return parse_sip002(decoded)

        # Старый формат (base64 только метод:пароль)
        elif '@' in clean_url:
            return parse_legacy(clean_url)

        else:
            raise ValueError("Нераспознанный формат ссылки")

    except Exception as e:
        raise ValueError(f"Ошибка разбора ссылки: {str(e)}") from e


def parse_legacy(ss_url: str):
    """Парсинг старого формата: ss://base64(метод:пароль)@хост:порт"""
    parts = ss_url.split('@', 1)
    if len(parts) != 2:
        raise ValueError("Неверный формат ссылки (отсутствует @)")
    
    # Декодируем метод и пароль
    base64_part = parts[0]
    server_part = parts[1]
    
    # Добавляем padding при необходимости
    padding = '=' * (4 - len(base64_part) % 4)
    decoded = base64.urlsafe_b64decode(base64_part + padding)
    
    # Пробуем разные кодировки для пароля
    try:
        decoded_str = decoded.decode('utf-8')
    except UnicodeDecodeError:
        try:
            decoded_str = decoded.decode('latin-1')
        except:
            decoded_str = decoded.decode('utf-8', errors='replace')
    
    # Разделяем метод и пароль
    if ':' not in decoded_str:
        raise ValueError("Отсутствует разделитель метода и пароля")
    
    method, password = decoded_str.split(':', 1)
    host, port = parse_server_part(server_part)
    
    return build_config(method, password, host, port)


def parse_sip002(decoded: str):
    """Парсинг SIP002 формата: метод:пароль@хост:порт"""
    # Разделяем пользовательскую часть и серверную часть
    user_part, server_part = decoded.split('@', 1)
    
    # Разделяем метод и пароль
    if ':' not in user_part:
        raise ValueError("Отсутствует разделитель метода и пароля")
    
    method, password = user_part.split(':', 1)
    host, port = parse_server_part(server_part)
    
    # Декодируем URL-encoded пароль
    password = unquote(password)
    
    return build_config(method, password, host, port)


def parse_server_part(server_part: str):
    """Извлекает хост и порт из серверной части"""
    # Обработка IPv6 адресов
    if server_part.startswith('['):
        ipv6_match = re.match(r'^\[([\da-fA-F:]+)\]:(\d+)$', server_part)
        if not ipv6_match:
            raise ValueError("Неверный формат IPv6 адреса")
        host = ipv6_match.group(1)
        port = ipv6_match.group(2)
    else:
        if server_part.count(':') > 1:
            raise ValueError("Неверный формат адреса сервера")
        parts = server_part.split(':')
        if len(parts) < 2:
            raise ValueError("Отсутствует порт в ссылке")
        host = parts[0]
        port = parts[1]

    # Валидация порта
    if not port.isdigit():
        raise ValueError("Порт должен быть числом")
    if not (1 <= int(port) <= 65535):
        raise ValueError("Порт должен быть в диапазоне 1-65535")

    return host, int(port)


def build_config(method: str, password: str, host: str, port: int):
    """Собирает конечную конфигурацию"""
    return {
        "server": host,
        "server_port": port,
        "method": method,
        "password": password,
        "local_address": "127.0.0.1",
        "local_port": 1080,
        "timeout": 300,
        "mode": "tcp_and_udp"
    }