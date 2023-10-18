import os
import json
from flask import Flask, request, jsonify, render_template
from lxml import html
import requests
from datetime import datetime
from google.oauth2 import service_account
import gspread
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from selenium import webdriver
from selenium.webdriver.common.by import By

app = Flask(__name__)

# Google Sheets credentials (replace with your JSON file)
scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive']
creds = service_account.Credentials.from_service_account_file('credet.json', scopes=scope)
gc = gspread.authorize(creds)

# Open the Google Sheet by its title
sheet1 = gc.open_by_url("https://docs.google.com/spreadsheets/d/1K9CewgslVHqLqy9wwpazswR4jMk8mMK7hBedgd8dIDY/edit#gid=721899723")
sheet = sheet1.worksheet("WebScrap")
# Store scheduled jobs
scheduled_jobs = {}
row_index = 2  # Start from the second row (1st row for headers)
urls_data = []

# Load previously added URLs data from the JSON file
try:
    with open('urls_data.json', 'r') as json_file:
        urls_data = json.load(json_file)
except FileNotFoundError:
    urls_data = []  # Create an empty list if the file doesn't exist

def scrape_and_update_sheet(url, xpath, index):
    # Create a headless Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        elements = driver.find_elements(By.XPATH, xpath)

        if index < len(elements):
            extracted_text = elements[index].text
            print(f"Extracted text: {extracted_text} from URL: {url} at {datetime.now()}")
        else:
            extracted_text = driver.find_element(By.XPATH, xpath).text
        print(extracted_text)
        
        # Check if the URL is in urls_data.json
        url_exists = any(item['url'] == url for item in urls_data)

        # If the URL is not in urls_data.json or XPath doesn't match, create a new row
        if not url_exists or any(item['url'] == url and item['xpath'] != xpath for item in urls_data):
            # Update Google Sheet with URL, time, and extracted data
            data_to_update = [url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), extracted_text]
            sheet.insert_row(data_to_update, row_index)

            # Store the data in the urls_data list
            if url_exists:
                urls_data = [item for item in urls_data if item['url'] != url]
            urls_data.append({
                'url': url,
                'xpath': xpath,
                'text_content': extracted_text
            })

    except Exception as e:
        print(f"Error while scraping '{url}': {str(e)}")
    finally:
        driver.quit()

# Initialize a BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    TIME=datetime.now()
    if request.method == 'POST':
        data = request.form
        url = data['url']
        xpath = data['xpath']
        index = int(data.get('index', 0))  # Default index is 0 if not specified
        time_str = data['time']

        try:
            # Parse the time input from the form
            scheduled_time = datetime.strptime(time_str, '%H:%M').time()
            print(type(scheduled_time.hour), scheduled_time)
            # Create a job with a CronTrigger to run at the specified time daily
            trigger = CronTrigger(hour=scheduled_time.hour, minute=scheduled_time.minute)
            scheduled_job = scheduler.add_job(scrape_and_update_sheet, trigger=trigger, args=[url, xpath, index])

            # Store the scheduled job and URL in the respective lists
            scheduled_jobs[(url, xpath, index)] = scheduled_job

            return jsonify({'message': f"Task added for URL '{url}' with XPath '{xpath}' and index '{index}' daily at {time_str}"})
        except ValueError:
            return jsonify({'error': 'Invalid time format. Please use HH:MM.'}), 400

    # Display the index page with a form to input schedules
    return render_template('index.html',time=TIME)

@app.route('/view_schedules', methods=['GET'])
def view_schedules():
    # Retrieve and display the existing schedules
    schedules = [{'url': job.args[0], 'xpath': job.args[1], 'index': job.args[2], 'time': str(job.trigger.fields[1])} for job in scheduler.get_jobs()]
    return jsonify({'schedules': schedules})

if __name__ == '__main__':
    app.run(debug=True)
