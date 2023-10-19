import os
import json
from flask import Flask, request, jsonify, render_template, send_from_directory

import requests
from datetime import datetime
from google.oauth2 import service_account
import gspread
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

app = Flask(__name__)




# Initialize Google Sheets
def init_google():
    # Google Sheets credentials (replace with your JSON file)
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file('credet.json', scopes=scope)
    gc = gspread.authorize(creds)

    # Open the Google Sheet by its title
    sheet1 = gc.open_by_url("https://docs.google.com/spreadsheets/d/1K9CewgslVHqLqy9wwpazswR4jMk8mMK7hBedgd8dIDY/edit#gid=721899723")
    sheet = sheet1.worksheet("WebScrap")
    return sheet


def append_column(sheet, data, url):
    # Get the values in the first row to determine the last column with text
    
    
    

    cell = sheet.find(url)
    
    first_row = sheet.row_values(cell.row)
    last_col_index = len(first_row) + 1

    # Append a new column at the end
    sheet.add_cols(1)
    sheet.update_cell(first_row,last_col_index,data)

    # Update the header cell in the new column
    #sheet.update_cell(1, last_col_index, datetime.today())

    # Update the cells in the new column with data


# Function to check urls_data.json and update the Google Sheet
def update_google_sheet():
    # Load data from urls_data.json
    with open('urls_data.json', 'r') as json_file:
        urls_data = json.load(json_file)

    # Initialize Google Sheets
    sheet = init_google()

    for data in urls_data:
        url = data['url']
        data_value = data['data']

        # Check if the URL is in the Google Sheet
        try:
            cell = sheet.find(url)
            col_index = cell.col
        except gspread.exceptions.CellNotFound:
            print(f"URL '{url}' not found in the Google Sheet")
            continue

        append_column(sheet,data_value,url)


# Initialize a BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()
urls_data = []
scheduled_jobs = {}



@app.route('/', methods=['GET', 'POST'])
def index():
    global urls_data
    TIME = datetime.now()
    if request.method == 'POST':
        data = request.form
        url = data['url']
        xpath = data['xpath']
        index = int(data.get('index', 0))  # Default index is 0 if not specified
        time_str = data['time']
        urls_data.append({'url': url, 'time': time_str, 'index':index,'xpath':xpath,'data':'0'})
        with open('urls_data.json', 'w') as pre_json_file:
            json.dump(urls_data, pre_json_file)
        sheet = init_google()
        sheet.insert_row([url,xpath,time_str],2)
        try:
            # Parse the time input from the form
            scheduled_time = datetime.strptime(time_str, '%H:%M').time()
            # Create a job with a CronTrigger to run at the specified time daily
            trigger = CronTrigger(hour=scheduled_time.hour, minute=scheduled_time.minute)
            
            scheduled_job = scheduler.add_job(update_google_sheet, trigger=trigger)

            # Store the scheduled job and URL in the respective lists
            scheduled_jobs[(url, xpath, index)] = scheduled_job

            return jsonify({'message': f"Task added for URL '{url}' with XPath '{xpath}' and index '{index}' daily at {time_str}"})
        except ValueError:
            return jsonify({'error': 'Invalid time format. Please use HH:MM.'}), 400

    # Display the index page with a form to input schedules
    return render_template('index.html', time=TIME)


@app.route("/fuck", methods=['GET', 'POST'])
def fuck():
    return render_template('fuck.html')


# Additional server-side endpoints for downloading and uploading 'pre.json' file
@app.route('/download_pre_json', methods=['GET'])
def download_pre_json():
    try:
        # Serve the pre.json file for download
        return jsonify(urls_data)
    except FileNotFoundError:
        return jsonify({'error': 'pre.json file not found'}), 404

@app.route('/upload_pre_json', methods=['POST'])
def upload_pre_json():
    global urls_data
    try:
        # Handle JSON data sent in the request
        uploaded_data = request.get_json()
        if not uploaded_data or "url" not in uploaded_data or "data" not in uploaded_data:
            return jsonify({'error': 'Invalid JSON data format. Expected { "url": "your_url", "data": "your_data" }'}), 400

        # Find the URL in the urls_data list and update its "data" value
        for item in urls_data:
            if item["url"] == uploaded_data["url"]:
                item["data"] = uploaded_data["data"]
                break
        

        # Save the updated data to urls_data.json
        with open("urls_data.json", "w") as f:
            json.dump(urls_data, f)

        return jsonify({'message': f'Data for URL "{uploaded_data["url"]}" updated successfully'})
    except Exception as e:
        return jsonify({'error': f'Error while processing JSON data: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
