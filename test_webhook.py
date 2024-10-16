import requests
import json

url = "https://wazzup.superwidetrack.repl.co/wazzup/webhook"
payload = {
  "messages": [
    {
      "chatId": "test123",
      "text": "Привет, это тестовое сообщение",
      "fromMe": false
    }
  ]
}
headers = {
  "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)
print(response.status_code)
print(response.text)