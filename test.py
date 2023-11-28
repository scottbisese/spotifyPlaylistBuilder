import requests
import json

# Authorization token that must have been created previously. See: https://developer.spotify.com/documentation/web-api/concepts/authorization
token = 'BQCE0S9wEYeRVD6mMBbPr8_8zR1IZskIrDbx8q8aw_npb9ZXW46NpFMxW2ywEN7tXS12GSU5uJXPwXCdDHrM6Tdj35crf9mZ9ui-3jD23jlcXKYai5rSiU850GVuW1ob0MJD2JChxdUPhoJWZubQHciAwLoMoiBhbAEZmoKqkPjTu912A_7Cr1evtxL10NAbT2jVj9NPtl4z8p42H2y145S9z550CH_z7q1pYAKI7QziSvoOZr41qTWWbpQUSvUYtDqy6eWCT20EKoNSCstleaz_XSrw'

def fetch_web_api(endpoint, method, body=None):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    url = f'https://api.spotify.com/{endpoint}'
    response = requests.request(method, url, headers=headers, json=body)

    return response.json()

tracks_uri = [
    'spotify:track:5d3lYp7cZtXtlYXXHlPUcB', 'spotify:track:4YnxkxkrmyuJnf8DZIULEX', 'spotify:track:0VjBlyHOKvMwbSdMmyiFEp',
    'spotify:track:218sf8KIzzfPSbdjpYC9X2', 'spotify:track:3IX0yuEVvDbnqUwMBB3ouC', 'spotify:track:7dyi7AorhfCTJvGFjXwpyU',
    'spotify:track:0EF1EE8zusg3Y869e56JFd', 'spotify:track:05UdmOwDMr4LsAk56AFfsE', 'spotify:track:53BA0ZcWvgJZxGyjo7ahJQ',
    'spotify:track:1gIXgeL8KPbRCnWvPfZyUJ'
]

def create_playlist(tracks_uri):
    user_info = fetch_web_api('v1/me', 'GET')
    user_id = user_info['id']

    playlist_data = {
        'name': 'My recommendation playlist',
        'description': 'Playlist created by the tutorial on developer.spotify.com',
        'public': False
    }
    playlist = fetch_web_api(f'v1/users/{user_id}/playlists', 'POST', body=playlist_data)

    tracks_uri_str = ','.join(tracks_uri)
    fetch_web_api(f'v1/playlists/{playlist["id"]}/tracks?uris={tracks_uri_str}', 'POST')

    return playlist

created_playlist = create_playlist(tracks_uri)
print(created_playlist['name'], created_playlist['id'])



"""import requests

# Authorization token that must have been created previously. See: https://developer.spotify.com/documentation/web-api/concepts/authorization
token = 'BQCE0S9wEYeRVD6mMBbPr8_8zR1IZskIrDbx8q8aw_npb9ZXW46NpFMxW2ywEN7tXS12GSU5uJXPwXCdDHrM6Tdj35crf9mZ9ui-3jD23jlcXKYai5rSiU850GVuW1ob0MJD2JChxdUPhoJWZubQHciAwLoMoiBhbAEZmoKqkPjTu912A_7Cr1evtxL10NAbT2jVj9NPtl4z8p42H2y145S9z550CH_z7q1pYAKI7QziSvoOZr41qTWWbpQUSvUYtDqy6eWCT20EKoNSCstleaz_XSrw'


def fetch_web_api(endpoint, method, body=None):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }

    url = f'https://api.spotify.com/{endpoint}'
    response = requests.request(method, url, headers=headers, json=body)

    return response.json()


top_tracks_ids = [
    '5d3lYp7cZtXtlYXXHlPUcB', '0VjBlyHOKvMwbSdMmyiFEp', '3IX0yuEVvDbnqUwMBB3ouC', '0EF1EE8zusg3Y869e56JFd', '53BA0ZcWvgJZxGyjo7ahJQ'
]


def get_recommendations():
    # Endpoint reference: https://developer.spotify.com/documentation/web-api/reference/get-recommendations
    return fetch_web_api(
        "v1/recommendations?limit=10&market=ES&seed_artists=4NHQUGzhtTLFvgF5SZesLK&seed_genres=classical%2Ccountry&seed_tracks=0c6xIDDpzE81m2q797ordA", 'GET'
    )['tracks']


recommended_tracks = get_recommendations()

for track in recommended_tracks:
    artists = ", ".join(artist['name'] for artist in track['artists'])
    print(f"{track['name']} by {artists}")"""
