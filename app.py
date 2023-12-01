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
import time

userToken = None

current_time_seconds = time.time() + 21600 # Time is in Central US
current_struct_time = time.gmtime(current_time_seconds)
formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_struct_time)

# ============================================
def removeSpecialChars(sentence):

    sentence = sentence.lower()
    strippedSentence = ""

    # Loops through each character of the sentence
    for character in sentence:

        # (If character is between a to z on ASCII Table) or (character is a space " ")
        if (ord(character) > 96 and ord(character) < 123) or ord(character) == 32:
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

    playlistName = 'CS 188 Playlist: ' + str(formatted_time)
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