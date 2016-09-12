# coding=utf-8
import requests
report = {
    'email': 'nightblizzard@sina.com',
    'password': 'sc07051989'
}
response = requests.post("http://52.197.23.9:4000/amazon-login", data=report, verify=False)

print response.status_code