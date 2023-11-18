
import requests

token = "BQBAm-vvAQOo2ONypetvm6H8ioTtU-fHZ7w1tJSIDtJNNeYmnsDxDC6UD1CmRzgmaMjM-wk6ee8gVGI9FDzTHzjeAUEp_zmfng9K8Dm_vxYAUvUGppisJ110Agpiy8v-MEgzu_9mgtE2sQZRtquYAgOC_hZgE7fwZ8JCENjVzvZzT_ER0DCPamM0yrXLJSXnM0wrdslA90V1gX02k0D9AHUCWVAbgI3uQkx79Xyewyc7PUYbx2JVO13J0XDdUNvSfheUrSkarQ"

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

def get_top_tracks(useToken):
    # Endpoint reference: https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks
    return fetch_web_api(useToken,'v1/me/top/tracks?time_range=short_term&limit=10', 'GET')

tokenInput = input("Enter Token: ")
top_tracks = get_top_tracks(str(tokenInput))

print(top_tracks['items'][0]["artists"][0]["name"], "\n")
print(top_tracks['items'][0]["name"])


