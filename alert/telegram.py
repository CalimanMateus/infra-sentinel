import requests

# Configuração do Telegram
TELEGRAM_BOT_TOKEN = "8677925355:AAHWjg3-FQnV9FvIVLlC7zi9Kt0mgJlgejw"
CHAT_ID = "-1003803781634"

def send_telegram_message(message):
    """Envia mensagem para o Telegram"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHAT_ID,
            'text': message
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print(f"[TELEGRAM ENVIADO] {message}")
        else:
            print(f"[ERRO TELEGRAM] {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"[ERRO TELEGRAM] Falha ao enviar: {e}")

def send_alert(message):
    """Função de alerta (imprime no terminal e envia para Telegram)."""
    print(f"[ALERTA] {message}")
    # Envia para Telegram reutilizando a mesma mensagem existente
    send_telegram_message(message)
