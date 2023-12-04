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
import logging

logging.basicConfig(filename='error.log', level=logging.DEBUG)

userToken = None
recently_created_playlist = None

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

# This function handles data entry from the form
@app.route('/form_submit', methods=['POST']) 
def form_submit():
    global userToken
    # -------------------------------------------
    # Get Input from User
    userToken = request.form['userSentenceInput']
    return redirect(url_for('optionsPage'))

# =================================================================
@app.route('/CreateAddPlaylist', methods=['POST'])
def CreateAddPlaylist():
    global recently_created_playlist

    if request.method == 'POST':
        playlist_name = request.form.get('playlistName')

        # ----------------------------------------------
        # Get Top 10 Songs
        songURIs = []  # Define the songURIs list

        top10Songs = APICall(userToken, 'v1/me/top/tracks?time_range=short_term&limit=20', 'GET')

        if 'items' in top10Songs:
            # Get URI of Top 10 Songs
            for iteration in range(0, len(top10Songs["items"])):
                songURIs.append(top10Songs["items"][iteration]["uri"])
        else:
            print("Unexpected response structure:", top10Songs)

        # ---------------------------- Create Playlist ---------------

        user_info = APICall(userToken, 'v1/me', 'GET')

        if 'id' in user_info:
            user_id = user_info['id']
        else:
            print("Unexpected response structure for user_info:", user_info)
            return redirect(url_for('CompletePlaylist'))  # or handle this error in a way that fits your application's logic

        playlist_data = {
            'name': playlist_name,  # Use the playlist name obtained from the form
            'description': 'Playlist created by Team 8 Ballers',
            'public': False
        }

        # Create Playlist
        playlist = APICall(userToken, f'v1/users/{user_id}/playlists', 'POST', body=playlist_data)

        songURIs_str = ','.join(songURIs)

        # Add Playlist
        APICall(userToken, f'v1/playlists/{playlist["id"]}/tracks?uris={songURIs_str}', 'POST')

        # Store the recently created playlist data
        recently_created_playlist = {'id': playlist["id"], 'name': playlist_name}

        # Render the playlist preview page with the iframe
        return render_template('CompletePlaylist.html', playlist_id=playlist["id"])

    # Redirect to CompletePlaylist in case of a GET request or other scenarios
    return redirect(url_for('CompletePlaylist.html'))

# =================================================================
@app.route('/playlist_preview', methods=['GET', 'POST'])
def playlist_embed():
    global recently_created_playlist

    # Use the recently created playlist data or any other logic to get the desired playlist data
    playlist_data = recently_created_playlist or {'id': '0Pg6rxgKT92ZxESm2zHaqh', 'name': 'Default Playlist'}
    playlist_url = f'https://open.spotify.com/embed/playlist/{playlist_data["id"]}?utm_source=generator&theme=0'
    print(f'Playlist URL: {playlist_url}')  # Add this line for debugging
    return render_template('playlist_preview.html', playlist_url=playlist_url, playlist_name=playlist_data["name"])


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