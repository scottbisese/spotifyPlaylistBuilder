#This is the MVP Revert Here
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
# Remove Special Character Function

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
# Function to Call Sentimental AI API
def APICall(useToken, endpoint, method, body=None):
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
    # -------------------------------------------
    # Get Input from User
    form_data1 = request.form['userSentenceInput']

    token = "BQBAm-vvAQOo2ONypetvm6H8ioTtU-fHZ7w1tJSIDtJNNeYmnsDxDC6UD1CmRzgmaMjM-wk6ee8gVGI9FDzTHzjeAUEp_zmfng9K8Dm_vxYAUvUGppisJ110Agpiy8v-MEgzu_9mgtE2sQZRtquYAgOC_hZgE7fwZ8JCENjVzvZzT_ER0DCPamM0yrXLJSXnM0wrdslA90V1gX02k0D9AHUCWVAbgI3uQkx79Xyewyc7PUYbx2JVO13J0XDdUNvSfheUrSkarQ"
    response = APICall(token, 'v1/me/top/tracks?time_range=short_term&limit=10', 'GET')

    # -------------------------------------------
    # Initialize SQL connection
    conn = SQLConnection()
    conn = conn.getConnection()
    cursor = conn.cursor()

    # -------------------------------------------
    # Add AI API Response to SQL Database
    sql_query = f"""
        INSERT INTO SentimalAIResponseTable.AIResponseTable
        VALUES (
         '{"response"}',
         '{"response"}',
         '{"Example"}',
         '{"Example"}',
         '{"Example"}'
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

    # Initialize SQL connection
    conn = SQLConnection()
    conn = conn.getConnection()
    cursor = conn.cursor()

    sql_query = f"""
        SELECT * FROM SentimalAIResponseTable.AIResponseTable;
        """

    cursor.execute(sql_query)

    records = cursor.fetchall()
    print("Records")
    print(records)

    cursor.close()

    return render_template('table.html', records=records)

if __name__ == '__main__': 
    app.run()