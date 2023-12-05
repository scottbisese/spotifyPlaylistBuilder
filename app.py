#Absoulete Bare Minium
from flask import Flask, render_template, request, redirect, url_for
# The below handles some deprecated dependencies in Python > 3.10 that Flask Navigation needs
import requests
import collections
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable
from flask_navigation import Navigation
# Import Azure SQL helper code
from azuresqlconnector import *

userToken = None


# ============================================
def removeSpecialChars(sentence):
    # Black List:          ',  ",  ;,  %,  _,  [   ],  `,  -,  +,  /,  & 
    blacklistASCIICode = [39, 34, 59, 37, 95, 91, 93, 96, 45, 43, 47, 38]
    strippedSentence = ""

    # Loops through each character of the sentence
    for character in sentence:

        # Blacklist Chars
        if not (ord(character) in blacklistASCIICode):
            strippedSentence += character

    return strippedSentence

# ============================================
# Function to Call Spotify API
def APICall(useToken, endpoint, method, body=None):
    headers = {
            'Authorization': f'Bearer {useToken}',
            'Content-Type': 'application/json',
        }

    url = f'https://api.spotify.com/{endpoint}'
    response = requests.request(method, url, headers=headers, json=body)

    return response.json()

# =================================================================
# Add Parameters given to SQL DB
def addToSQLDB(songName, artistName, userName):
    
    # -------------------------------------------
    # Initialize SQL connection
    conn = SQLConnection()
    conn = conn.getConnection()
    cursor = conn.cursor()

    # -------------------------------------------
    # Add AI API Response to SQL Database
    sql_query = f"""
        INSERT INTO SpotifyBuilderFinalProject.MVPPlaylistTable
        VALUES (
         '{songName}',
         '{artistName}',
         '{userName}'
         );
        """

    cursor.execute(sql_query)

    conn.commit()
    cursor.close()

# ============================================
app = Flask(__name__)

nav = Navigation(app)

# Initialize navigations
# Navigations have a label and a reference that ties to one of the functions below
nav.Bar('top', [
    nav.Item('Enter Token', 'form'),
    nav.Item('API Responses', 'table')
])

# =================================================================
@app.route('/') 
def index():
    return render_template('setup.html')

@app.route('/SubmitToken') 
def form():
    return render_template('SubmitTokenPage.html')

@app.route('/CompletePlaylist') 
def CompletePlaylist():
    return render_template('CompletePlaylist.html')

@app.route('/optionsPage') 
def optionsPage():
    return render_template('optionsPage.html')

@app.route('/RecPlaylist')
def RecPlaylist():
    return redirect(url_for('generate_playlist'))

# This function handles data entry from the form
@app.route('/form_submit', methods=['POST']) 
def form_submit():
    global userToken
    # -------------------------------------------
    # Get Input from User
    userToken = request.form['userSentenceInput']
    return redirect(url_for('optionsPage'))

# =================================================================
@app.route('/CreateAddPlaylist') 
def CreateAddPlaylist():

    songURIs = []
    
    #----------------------------------------------
    # Get Top 10 Songs
    top10Songs = APICall(userToken, 'v1/me/top/tracks?time_range=short_term&limit=20', 'GET')

    # Get URI of Top 10 Songs
    for iteration in range(0, len(top10Songs["items"])):
        songURIs.append( top10Songs["items"][iteration]["uri"] )

    #----------------------------------------------
    # Get 10 Recommended Songs
    recommendedSong10 = APICall(userToken, "v1/recommendations?limit=20&market=ES&seed_artists=4NHQUGzhtTLFvgF5SZesLK&seed_genres=classical%2Ccountry&seed_tracks=0c6xIDDpzE81m2q797ordA",'GET')
    
    # Get URI of 10 Recommended Songs
    for iteration in range(0, len(recommendedSong10["tracks"])):
        songURIs.append( recommendedSong10["tracks"][iteration]["uri"] )

    #----------------------------------------------    
    # Create Playlist
    user_info = APICall(userToken, 'v1/me', 'GET')
    user_id = user_info['id']

    playlistName = 'CS 188 Playlist: '
    playlist_data = {
            'name': playlistName,
            'description': 'Playlist created by the tutorial on developer.spotify.com',
            'public': False
        }
    
    playlist = APICall(userToken, f'v1/users/{user_id}/playlists', 'POST', body=playlist_data)
    songURIs_str = ','.join(songURIs)

    #----------------------------------------------
    # Add Playlist
    APICall(userToken,f'v1/playlists/{playlist["id"]}/tracks?uris={songURIs_str}', 'POST')

    return redirect(url_for('CompletePlaylist'))

# =================================================================
@app.route('/Top1Song') 
def Top1Song():

    topSongs = APICall(userToken, 'v1/me/top/tracks?time_range=short_term&limit=10', 'GET')
    userInfo = APICall(userToken, 'v1/me', 'GET')


    for iteration in range(0, len(topSongs['items'])):
        tempSong = topSongs['items'][iteration]["artists"][0]["name"]
        tempSong = removeSpecialChars(tempSong)

        tempArtist = topSongs['items'][iteration]["name"]
        tempArtist = removeSpecialChars(tempArtist)

        tempUserName = userInfo['display_name']
        tempUserName = removeSpecialChars(tempUserName)

        addToSQLDB(tempSong, tempArtist, tempUserName)

    return redirect(url_for('table'))

# =====================ZAMA DEC 1============================================


def get_artist_id(access_token, artist_name):
    # Spotify search URL for artists
    search_url = f'https://api.spotify.com/v1/search?q={artist_name}&type=artist'

    # Authorization header with the access token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    try:
        # Make a GET request to search for the artist
        responses = requests.get(search_url, headers=headers)

        # Check if the request was successful (status code 200)
        if responses.status_code == 200:
            data = APICall(userToken, search_url, "GET")
            # Extract the artist ID from the response
            if 'artists' in data and 'items' in data['artists'] and data['artists']['items']:
                artist_id = data['artists']['items'][0]['id']  # Take the first artist's ID
                return artist_id
            else:
                # print(f"No artist found with the name '{artist_name}'")
                return None
        else:
            # print(f"Error: {responses.status_code} - {responses.text}")
            return None

    except requests.RequestException as e:
        # print(f"Error fetching data: {e}")
        return None
    
def get_track_id(access_token, track_name):
    # Spotify search URL for artists
    search_url = f'https://api.spotify.com/v1/search?q={track_name}&type=track'

    # Authorization header with the access token
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    try:
        # Make a GET request to search for the artist
        responses = requests.get(search_url, headers=headers)

        # Check if the request was successful (status code 200)
        if responses.status_code == 200:
            data = APICall(userToken, search_url, "GET")
            # Extract the artist ID from the response
            if 'tracks' in data and 'items' in data['tracks'] and data['tracks']['items']:
                track_id = data['tracks']['items'][0]['id']  # Take the first track's ID
                return track_id
            else:
                # print(f"No artist found with the name '{track_name}'")
                return None
        else:
            # print(f"Error: {responses.status_code} - {responses.text}")
            return None

    except requests.RequestException as e:
        # print(f"Error fetching data: {e}")
        return None

@app.route('/redirect2') 
def redirect2():
    return render_template('redirect2.html')

@app.route('/generate_playlist', methods=['POST'])
def generate_playlist():
    artist_names = request.form['artist_form']
    genre = request.form['genre_form']
    track_names = request.form['track_form']
    
    songURIs = []

    id_of_artist = get_artist_id(userToken, artist_names)
    id_of_track = get_track_id(userToken, track_names)
    
     #----------------------------------------------
    # Get 10 Recommended Songs
    ZamaRecommendedSong10 = APICall(userToken, f"v1/recommendations?seed_artists={id_of_artist}&seed_genres={genre}&seed_tracks={id_of_track}",'GET')   

    # Get URI of 10 Recommended Songs
    for iteration in range(0, len(ZamaRecommendedSong10["tracks"])):
        songURIs.append(ZamaRecommendedSong10["tracks"][iteration]["uri"] )

    #----------------------------------------------    
    # Create Playlist
    user_info = APICall(userToken, 'v1/me', 'GET')
    user_id = user_info['id']

    playlistName = 'Zama"s Playlist: ' 
    playlist_data = {
            'name': playlistName,
            'description': 'Playlist created by the tutorial on developer.spotify.com',
            'public': False
        }
    
    playlist = APICall(userToken, f'v1/users/{user_id}/playlists', 'POST', body=playlist_data)
    songURIs_str = ','.join(songURIs)

    #----------------------------------------------
    # Add Playlist
    APICall(userToken,f'v1/playlists/{playlist["id"]}/tracks?uris={songURIs_str}', 'POST')

    return redirect(url_for('redirect2'))


# =================================================================

@app.route('/table') 
def table():

    # Initialize SQL connection
    conn = SQLConnection()
    conn = conn.getConnection()
    cursor = conn.cursor()

    sql_query = f"""
        SELECT DISTINCT * FROM SpotifyBuilderFinalProject.MVPPlaylistTable;
        """

    cursor.execute(sql_query)

    records = cursor.fetchall()
    print("Records")
    print(records)

    cursor.close()

    return render_template('table.html', records=records)

if __name__ == '__main__': 
    app.run()