
import requests

def fetch_web_api(token,endpoint, method, body=None):
    headers = {
        'Authorization': f'Bearer {token}'
    }

    url = f'https://api.spotify.com/{endpoint}'
    print("URL HERE:", url)
    
    if method == 'GET':
        response = requests.get(url, headers=headers)
        return response.json()
    elif method == 'POST':
        print("Post Happens")
        headers['Content-Type'] = 'application/json'
        response = requests.post(url, headers=headers, json=body)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    response.raise_for_status()
    return response.json()

def get_top_tracks(token):
    # Endpoint reference: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
    return fetch_web_api(token,
        'v1/me/top/tracks?time_range=short_term&limit=10', 'GET'
    )['items']

top_tracks = get_top_tracks("BQBV3ke2uw6sHEoS1QQKzfs5z3WIH5id77raXtO33GX-7rO3HyM7KGuK6A5ejwkr20ITioTDcLoMO91TExh_HFitVdQWUO2wee0v9D9xv801aZHsD7e9xsHxhDSGc7_rxLMoSgkMHXaEO4WvYhROVpJiEeyYgx8gB3Y6n_Bg3_UOyKwh_Y3rPoeV-_dfyhypje7zbAxE7Mk8CW8xP8HWBRTYSAUhgrBKj6J_jaHya6rVQsgub9wIuf04VAsX42QubtsuL34aXg")


print(top_tracks[0]["artists"][0]["name"], "\n")
print(top_tracks[0]["name"])


