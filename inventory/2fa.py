import requests
import json

def send_sms_2fa(phone_number, code):
    url = "https://api.infobip.com/sms/1/text/single"
    headers = {
        "Authorization": "App YOUR_API_KEY",  # Remplace "YOUR_API_KEY" par ta clé API Infobip
        "Content-Type": "application/json"
    }
    payload = {
        "from": "YourSenderName",  # Remplace "YourSenderName" par le nom de l'expéditeur
        "to": phone_number,
        "text": f"Your 2FA code is {code}"
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        print("SMS sent successfully")
    else:
        print(f"Failed to send SMS: {response.status_code}, {response.text}")

# Exemple d'utilisation
send_sms_2fa("+212123456789", "123456")

