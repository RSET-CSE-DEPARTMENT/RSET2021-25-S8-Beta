import requests

colab_api_url = "http://127.0.0.1:5000/process"  # Use the ngrok URL from Colab

data = {"text": "hello world"}
response = requests.post(colab_api_url, json=data)

if response.status_code == 200:
    print("Response from Colab:", response.json())
else:
    print("Error:", response.status_code)
