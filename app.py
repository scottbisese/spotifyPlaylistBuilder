#just for a change
from flask import Flask, render_template, request, redirect, url_for
# The below handles some deprecated dependencies in Python > 3.10 that Flask Navigation needs
import requests
import collections
collections.MutableSequence = collections.abc.MutableSequence
collections.Iterable = collections.abc.Iterable
from flask_navigation import Navigation
# Import Azure SQL helper code
from azuresqlconnector import *

# ============================================
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

# ============================================
app = Flask(__name__)

nav = Navigation(app)

# Initialize navigations
# Navigations have a label and a reference that ties to one of the functions below
nav.Bar('top', [
    nav.Item('Home', 'index'),
    nav.Item('Modal Example', 'modal'), 
    nav.Item('Form Example', 'form'),
    nav.Item('Display Table Example', 'table')
])

@app.route('/') 
def index():
    return render_template('form-example-home.html')

@app.route('/modal') 
def modal():
    return render_template('modal.html')

@app.route('/form') 
def form():
    return render_template('form.html')

# This function handles data entry from the form
@app.route('/form_submit', methods=['POST']) 
def form_submit():
    

    top_tracks = get_top_tracks("BQBAm-vvAQOo2ONypetvm6H8ioTtU-fHZ7w1tJSIDtJNNeYmnsDxDC6UD1CmRzgmaMjM-wk6ee8gVGI9FDzTHzjeAUEp_zmfng9K8Dm_vxYAUvUGppisJ110Agpiy8v-MEgzu_9mgtE2sQZRtquYAgOC_hZgE7fwZ8JCENjVzvZzT_ER0DCPamM0yrXLJSXnM0wrdslA90V1gX02k0D9AHUCWVAbgI3uQkx79Xyewyc7PUYbx2JVO13J0XDdUNvSfheUrSkarQ")
    artist = top_tracks['items'][0]["artists"][0]["name"]
    songName = top_tracks['items'][0]["name"]

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
         '{artist}',
         '{songName}',
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
    return redirect(url_for('form'))

@app.route('/table') 
def table():
    """
    top_tracks = get_top_tracks("BQBAm-vvAQOo2ONypetvm6H8ioTtU-fHZ7w1tJSIDtJNNeYmnsDxDC6UD1CmRzgmaMjM-wk6ee8gVGI9FDzTHzjeAUEp_zmfng9K8Dm_vxYAUvUGppisJ110Agpiy8v-MEgzu_9mgtE2sQZRtquYAgOC_hZgE7fwZ8JCENjVzvZzT_ER0DCPamM0yrXLJSXnM0wrdslA90V1gX02k0D9AHUCWVAbgI3uQkx79Xyewyc7PUYbx2JVO13J0XDdUNvSfheUrSkarQ")
    artist = top_tracks['items'][0]["artists"][0]["name"]
    songName = top_tracks['items'][0]["name"]
    """
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
         '{"Example"}',
         '{"Example"}',
         );
        """

    cursor.execute(sql_query)

    # -------------------------------------------
    print("Data submitted. . .")

    # IMPORTANT: The connection must commit the changes.
    conn.commit()

    print("Changes commited.")

    cursor.close()
    
    # Initialize SQL connection
    conn = SQLConnection()
    conn = conn.getConnection()
    cursor = conn.cursor()

    sql_query = f"""
        SELECT * FROM SpotifyBuilderFinalProject.MVPPlaylistTable;
        """

    cursor.execute(sql_query)

    records = cursor.fetchall()


    cursor.close()

    return render_template('table.html', records=records)

if __name__ == '__main__': 
    app.run()