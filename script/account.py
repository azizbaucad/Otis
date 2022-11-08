import requests
from script.conf import configuration

CLIENT_ID = configuration()['CLIENT_ID']
CLIENT_SECRET = configuration()['CLIENT_SECRET']
URI = configuration()['URI']

# fonction adminToken
def adminToken():
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    url = URI
    response = requests.post(url, data=data)

    if response.status_code > 200:
        return {"message": "Username ou Password Incorrect", 'status': 'error'}
    tokens_data = response.json()
    ret = {
        'tokens': {"access_token": tokens_data['access_token'],
                   "token_type": tokens_data['token_type'],
                   },
        "status": 'success',
    }
    return ret
