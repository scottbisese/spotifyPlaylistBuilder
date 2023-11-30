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
# Function to Call Sentimental AI API
def APICall(useToken, endpoint, method, body=None):
    headers = {
            'Authorization': f'Bearer {useToken}',
            'Content-Type': 'application/json',
        }

    url = f'https://api.spotify.com/{endpoint}'
    response = requests.request(method, url, headers=headers, json=body)

    return response.json()

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

    playlist_data = {
            'name': 'CS 188 Builder',
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

    response = APICall(userToken, 'v1/me/top/tracks?time_range=short_term&limit=1', 'GET')

    artistName = response['items'][0]["artists"][0]["name"]
    songName = response['items'][0]["name"]

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
         '{artistName}'
         );
        """

    cursor.execute(sql_query)

    # -------------------------------------------
    print("Data submitted. . .")

    # IMPORTANT: The connection must commit the changes.
    conn.commit()

    print("Changes commited.")

    cursor.close()

    print("Redirecting. . .")

    # Redirect back to form page after the form is submitted
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