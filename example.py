import requests

response = requests.post(url="http://127.0.0.1:8000/users", json={
    "name": "Joe",
    "age": 20
})
print(response.json())