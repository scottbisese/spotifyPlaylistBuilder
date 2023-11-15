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
def APICall(sentence):
    # Define the API endpoint URL
    url = "https://langaisamueltrujillo.cognitiveservices.azure.com/language/:analyze-text?api-version=2023-04-15-preview"

    # Define the API key
    api_key = "9640d8a2503542daa89851a93feec843"

    # Define the headers, including the API key
    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": api_key
    }

    # Define the JSON data to be sent in the request body
    data = {
        "kind": "SentimentAnalysis",
        "parameters": {
            "modelVersion": "latest",
            "opinionMining": "True"
        },
        "analysisInput": {
            "documents": [
                {
                    "id": "1",
                    "language": "en",
                    "text": sentence
                }
            ]
        }
    }

    # ===========================
    # Try & Except for Response

    # Make the POST request
    response = requests.post(url, json=data, headers=headers)
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
    apiInfo = None
    # -------------------------------------------
    # Get Input from User
    form_data1 = request.form['userSentenceInput']

    # -------------------------------------------
    # Call API & Get Response
    try:
        # Trys to run User's Input
        apiInfo = APICall( removeSpecialChars(form_data1) )

    except:
        # If Fails runs default API Call that work
        apiInfo = APICall( "Your Sentence is not vaild" )

    sentence = form_data1
    sentimentResponse = apiInfo["results"]["documents"][0]["sentences"][0]["targets"][0]["sentiment"]
    postiveScore = apiInfo["results"]["documents"][0]["confidenceScores"]["positive"]
    neutralScore = apiInfo["results"]["documents"][0]["confidenceScores"]["neutral"]
    negativeScore = apiInfo["results"]["documents"][0]["confidenceScores"]["negative"]

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
         '{sentence}',
         '{sentimentResponse}',
         '{postiveScore}',
         '{neutralScore}',
         '{negativeScore}'
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