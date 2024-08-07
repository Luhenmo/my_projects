import requests
import base64

def write_string_in_base64(string:str)->str:
    bytes_string = string.encode('utf-8')
    base64_bytes = base64.b64encode(bytes_string)
    return base64_bytes.decode('utf-8')

credentials = {
    "client_id": "KTV0ko90RmNh",
    "client_secret":"SOgrVJiZ5WNG",
}

base64_credentials = write_string_in_base64(
    f"{credentials['client_id']}:{credentials['client_secret']}"
)

def get_anbima_token(base64_credentials):
    url="https://api.anbima.com.br/oauth/access-token"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {base64_credentials}",
    }
    data = {
        'grant_type': 'client_credentials'
    }
    return requests.post(url,headers=headers,json=data)

ANBIMA_TOKEN = get_anbima_token(base64_credentials)