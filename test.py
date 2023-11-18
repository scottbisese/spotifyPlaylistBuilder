
import requests


def fetch_web_api(useToken, endpoint, method, body=None):
    headers = {
        'Authorization': f'Bearer {useToken}'
    }

    url = f'https://api.spotify.com/{endpoint}'
    
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


tokenInput = input("Enter Token: ")
top_tracks = fetch_web_api(tokenInput,'v1/me/top/tracks?time_range=short_term&limit=10', 'GET')

print(top_tracks['items'][0]["artists"][0]["name"], "\n")
print(top_tracks['items'][0]["name"])


