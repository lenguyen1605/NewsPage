import requests
#
# response = requests.post(url="http://127.0.0.1:8000/Signup", json={
#     "username": 'hihihi',
#     "password": '1234',
#     "email": 'nguyennhatle1605@gmail.com',
#     "id_post": []
#
#
# })
res = requests.get(url="http://127.0.0.1:8000/getAllPost")
print(res)
