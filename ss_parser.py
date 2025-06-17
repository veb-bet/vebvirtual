# ss_parser.py
import base64


def parse_ss_link(ss_url: str):
    if not ss_url.startswith("ss://"):
        raise ValueError("Ссылка должна начинаться с ss://")

    ss_url = ss_url[5:]
    if '#' in ss_url:
        ss_url = ss_url.split('#')[0]

    try:
        if '@' not in ss_url:
            decoded = base64.urlsafe_b64decode(ss_url + '=' * (4 - len(ss_url) % 4)).decode()
            method_password, address = decoded.rsplit('@', 1)
        else:
            decoded = base64.urlsafe_b64decode(ss_url.split('@')[0] + '=' * (4 - len(ss_url.split('@')[0]) % 4)).decode()
            method_password = decoded
            address = ss_url.split('@')[1]
    except Exception as e:
        raise ValueError("Ошибка разбора ссылки") from e

    method, password = method_password.split(':', 1)
    host, port = address.split(':')

    return {
        "server": host,
        "server_port": int(port),
        "method": method,
        "password": password,
        "local_address": "127.0.0.1",
        "local_port": 1080,
        "timeout": 300
    }
