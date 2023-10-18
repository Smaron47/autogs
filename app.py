# import os
# import requests
# from flask import Flask, request, render_template, redirect, url_for, jsonify, send_from_directory
# from bs4 import BeautifulSoup
# import csv
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# from datetime import datetime
# import json
# import pygsheets
# from google.auth import exceptions
# from lxml import etree
# import re

# app = Flask(__name__)

# # Initialize the 'data' dictionary to store user data
# data = {}

# # Create a scheduler
# scheduler = BackgroundScheduler()

# # Load credentials from the JSON key file
# gc = None

# try:
#     gc = pygsheets.authorize(service_file='credet.json')
# except exceptions.DefaultCredentialsError as e:
#     print("Error loading Google Sheets credentials. Make sure to set up Google Sheets API credentials.")

# # Open the Google Sheet by title or URL
# sheet = None  # Will be set in schedule_extraction

# def save_user_data(user_id):
#     user_data = data.get(user_id, {})
#     with open(f"{user_id}.json", "w") as file:
#         json.dump(user_data, file)

# def save_data_to_google_sheet(url, xpath, time, extracted_text, sheet, sheet_title="sheet1"):
#     try:
#         if not sheet:
#             return

#         # Find the worksheet based on sheet_title
#         worksheet = None
#         for ws in sheet.worksheets():
#             if ws.title == sheet_title:
#                 worksheet = ws
#                 break

#         if not worksheet:
#             print(f"Failed to find the worksheet with title: {sheet_title}")
#             return

#         row = [url, xpath, time, extracted_text]
#         worksheet.append_table(values=row)
#     except Exception as e:
#         print(f"An error occurred while saving data to Google Sheet: {str(e)}")
# def processxpath(xpath):
#     tag = re.match(r'//([\w-]+)', xpath).group(1)
#     attrs = re.findall(r'@([\w-]+)="([^"]+)"', xpath)
#     attrs_dict = {attr[0]: attr[1] for attr in attrs}
#     return tag, attrs_dict
# def data_extraction_job(user_id, url, xpath, sheet_title="sheet1", index=None):
    
#         response = requests.get(url)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.content, 'html.parser')
#             tag,attr=processxpath(xpath)
#             elements = soup.findAll(tag, attr)
#             if index is not None:
#                 if 0 <= index < len(elements):
#                     extracted_text = elements[index].text
#                 else:
#                     extracted_text = "Index out of range"
#             else:
#                 extracted_text = elements[0].text
            
#             # Get the current time in HH:MM format
#             current_time = datetime.now().strftime('%H:%M')
            
#             # Save the extracted data to the Google Sheet
#             save_data_to_google_sheet(url, xpath, current_time, extracted_text, sheet, sheet_title)
            
#             # Update user data with the latest extracted text
#             user_data = data.get(user_id, {})
#             user_data[url] = extracted_text
#             data[user_id] = user_data
#             save_user_data(user_id)
#         else:
#             print(f"Failed to fetch the URL: {url}")
    

# @app.route('/<user_id>/schedule')
# def schedule_page(user_id):
#     return render_template('schedule.html', user_id=user_id)

# @app.route('/<user_id>/schedule', methods=['POST'])
# def schedule_extraction(user_id):
#     user_data = data.get(user_id, {})
#     url = request.form.get('url')
#     xpath = str(request.form.get('xpath'))
    
#     schedule_time = request.form.get('time')
#     sheet_title = request.form.get('sheet_title')
#     index = request.form.get('index')
#     print(sheet_title)
#     data_extraction_job(user_id,url,xpath,sheet_title,index=None)
#     # Schedule data extraction job
#     if schedule_time:
#         hour, minute = map(int, schedule_time.split(':'))
#         trigger = CronTrigger(hour=hour, minute=minute)
#         scheduler.add_job(data_extraction_job, trigger=trigger, args=(user_id, url, xpath, sheet_title, index))
    
#     user_data[url] = ""
#     data[user_id] = user_data
#     save_user_data(user_id)
#     return redirect(url_for('get_data', user_id=user_id))









# @app.route('/<user_id>/delete', methods=['POST'])
# def delete_data(user_id):
#     user_data = data.get(user_id, {})
#     url = request.form.get('url')
#     if url in user_data:
#         del user_data[url]
#         data[user_id] = user_data
#         save_user_data(user_id)
#         # Remove the scheduled job if it exists
#         scheduler.remove_job(f"{user_id}_{url}")
#     return redirect(url_for('get_data', user_id=user_id))

# @app.route('/<user_id>/update', methods=['POST'])
# def update_data(user_id):
#     user_data = data.get(user_id, {})
#     url = request.form.get('url')
#     xpath = request.form.get('xpath')
#     user_data[url] = ""
#     data[user_id] = user_data

#     # Remove the scheduled job if it exists
#     scheduler.remove_job(f"{user_id}_{url}")

#     # Schedule data extraction job for the updated URL and XPath
#     schedule_time = request.form.get('time')
#     if schedule_time:
#         hour, minute = map(int, schedule_time.split(':'))
#         trigger = CronTrigger(hour=hour, minute=minute)
#         scheduler.add_job(data_extraction_job, trigger=trigger, args=(user_id, url, xpath))

#     save_user_data(user_id)
#     return redirect(url_for('get_data', user_id=user_id))

# @app.route('/<user_id>/get_data')
# def get_data(user_id):
#     user_data = data.get(user_id, {})
#     return render_template('data.html', user_id=user_id, user_data=user_data)

# @app.route('/<user_id>')
# def user_home(user_id):
#     return render_template('user_home.html', user_id=user_id)

# @app.route('/<user_id>/schedule_jobs')
# def schedule_jobs_page(user_id):
#     job_list = []
#     for job in scheduler.get_jobs():
#         if job.args[0] == user_id:
#             url = job.args[1]
#             xpath = job.args[2]
#             time = job.trigger.fields_as_string
#             job_list.append({'url': url, 'xpath': xpath, 'time': time})
#     return jsonify(job_list)

# @app.route('/<user_id>/create_user', methods=['POST'])
# def create_user(user_id):
#     user_data_path = f"{user_id}.json"

#     # Check if the user data already exists
#     if os.path.exists(user_data_path):
#         with open(user_data_path, "r") as file:
#             user_data = json.load(file)
#         print(f"User data already exists with ID: {user_id}")
#         return "User data already exists."

#     # Read credentials file content
#     credentials = request.get_json()

#     user_data = {}
#     data[user_id] = user_data

#     # Save the credentials file with the user ID
#     with open(f"{user_id}_credentials.json", "w") as file:
#         json.dump(credentials, file)

#     # Schedule data extraction jobs based on provided credentials
#     for url, xpath in credentials.get('data', {}).items():
#         schedule_time = credentials.get('schedule', {}).get(url)
#         if schedule_time:
#             hour, minute = map(int, schedule_time.split(':'))
#             trigger = CronTrigger(hour=hour, minute=minute)
#             scheduler.add_job(data_extraction_job, trigger=trigger, args=(user_id, url, xpath))

#     save_user_data(user_id)

#     return "User created successfully."


# @app.route('/<user_id>/add_google_sheet', methods=['POST'])
# def add_google_sheet(user_id):
#     user_data = data.get(user_id, {})
#     user_data['google_sheet'] = request.form.get('google_sheet')
#     data[user_id] = user_data
#     save_user_data(user_id)
#     return redirect(url_for('user_home', user_id=user_id))

# @app.route('/<user_id>/get_google_sheet')
# def get_google_sheet(user_id):
#     user_data = data.get(user_id, {})
#     return jsonify({'google_sheet': user_data.get('google_sheet', '')})

# if __name__ == '__main__':
#     app.run(debug=True)


# import os
# from flask import Flask, request, jsonify
# from lxml import html
# import requests
# from datetime import datetime
# from google.oauth2 import service_account
# import gspread
# from apscheduler.schedulers.background import BackgroundScheduler
# from apscheduler.triggers.cron import CronTrigger
# import json

# app = Flask(__name)

# # Google Sheets credentials (replace with your JSON file)
# scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://spreadsheets.google.com/feeds',
#         'https://www.googleapis.com/auth/drive']
# creds = service_account.Credentials.from_service_account_file('credet.json', scopes=scope)
# gc = gspread.authorize(creds)

# # Open the Google Sheet by its title
# sheet = gc.open('email').sheet1

# # Store scheduled jobs
# scheduled_jobs = {}
# row_index = 2  # Start from the second row (1st row for headers)
# urls_data = []

# def scrape_and_update_sheet(url, xpath):
#     # Make an HTTP request to the URL
#     response = requests.get(url)
#     if response.status_code == 200:
#         page = html.fromstring(response.text)
#         extracted_text = page.xpath(xpath)
        
#         if extracted_text:
#             extracted_text1 = extracted_text[0].text_content()  # Get the actual text content
#             print(f"Extracted text: {extracted_text1} from URL: {url} at {datetime.now()}")

#             # Update Google Sheet with URL, time, and extracted data
#             data_to_update = [url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), extracted_text1]
#             sheet.insert_row(data_to_update, row_index)

#             # Store the data in the URLs_data list
#             urls_data.append({
#                 'url': url,
#                 'xpath': xpath,
#                 'text_content': extracted_text1
#             })f

#         else:
#             print(f"XPath '{xpath}' did not match any elements on '{url}' at {datetime.now()}")
#     else:
#         print(f"Request to '{url}' failed with status code {response.status_code} at {datetime.now()}")

# # Initialize a BackgroundScheduler
# scheduler = BackgroundScheduler()
# scheduler.start()

# @app.route('/add_task', methods=['POST'])
# def add_task():
#     data = request.get_json()
#     url = data['url']
#     xpath = data['xpath']
#     time_str = data['time']
#     print(time_str, url, xpath)
#     try:
#         # Parse the time input from the request
#         scheduled_time = datetime.strptime(time_str, '%H:%M').time()

#         # Create a job with a CronTrigger to run at the specified time daily
#         trigger = CronTrigger(hour=scheduled_time.hour, minute=scheduled_time.minute)
#         scheduled_job = scheduler.add_job(scrape_and_update_sheet, trigger=trigger, args=[url, xpath])

#         # Store the scheduled job and URL in the respective lists
#         scheduled_jobs[(url, xpath)] = scheduled_job

#         return jsonify({'message': f"Task added for URL '{url}' with XPath '{xpath}' daily at {time_str}"})
#     except ValueError:
#         return jsonify({'error': 'Invalid time format. Please use HH:MM.'}), 400

# if __name__ == '__main__':
#     # Load previously added URLs data from the JSON file
#     try:
#         with open('urls_data.json', 'r') as json_file:
#             urls_data = json.load(json_file)
#     except FileNotFoundError:
#         urls_data = []  # Create an empty list if the file doesn't exist

#     # Find the next row index to append data in the Google Sheet
#     if urls_data:
#         row_index = len(urls_data) + 2  # Start from the next empty row
#     app.run(debug=True)



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
sheet = gc.open('111').sheet1

# Store scheduled jobs
scheduled_jobs = {}
row_index = 2  # Start from the second row (1st row for headers)
urls_data = []

def scrape_and_update_sheet(url, xpath):
    # Create a headless Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        extracted_element = driver.find_element(By.XPATH,xpath)
        extracted_text = extracted_element.text

        if extracted_text:
            print(f"Extracted text: {extracted_text} from URL: {url} at {datetime.now()}")

            # Update Google Sheet with URL, time, and extracted data
            data_to_update = [url, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), extracted_text]
            sheet.insert_row(data_to_update, row_index)

            # Store the data in the URLs_data list
            urls_data.append({
                'url': url,
                'xpath': xpath,
                'text_content': extracted_text
            })

        else:
            print(f"XPath '{xpath}' did not match any elements on '{url}' at {datetime.now()}")
    except Exception as e:
        print(f"Error while scraping '{url}': {str(e)}")
    finally:
        driver.quit()

# Initialize a BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form
        url = data['url']
        xpath = data['xpath']
        time_str = data['time']

        try:
            # Parse the time input from the form
            scheduled_time = datetime.strptime(time_str, '%H:%M').time()
            print(type(scheduled_time.hour), scheduled_time.minute)
            # Create a job with a CronTrigger to run at the specified time daily
            trigger = CronTrigger(hour=scheduled_time.hour, minute=scheduled_time.minute)
            scheduled_job = scheduler.add_job(scrape_and_update_sheet, trigger=trigger, args=[url, xpath])

            # Store the scheduled job and URL in the respective lists
            scheduled_jobs[(url, xpath)] = scheduled_job

            return jsonify({'message': f"Task added for URL '{url}' with XPath '{xpath}' daily at {time_str}"})
        except ValueError:
            return jsonify({'error': 'Invalid time format. Please use HH:MM.'}), 400

    # Display the index page with a form to input schedules
    return render_template('index.html')

@app.route('/view_schedules', methods=['GET'])
def view_schedules():
    # Retrieve and display the existing schedules
    schedules = [{'url': job.args[0], 'xpath': job.args[1], 'time': str(job.trigger.fields[1])} for job in scheduler.get_jobs()]
    return jsonify({'schedules': schedules})

if __name__ == '__main__':
    # Load previously added URLs data from the JSON file
    try:
        with open('urls_data.json', 'r') as json_file:
            urls_data = json.load(json_file)
    except FileNotFoundError:
        urls_data = []  # Create an empty list if the file doesn't exist

    # Find the next row index to append data in the Google Sheet
    if urls_data:
        row_index = len(urls_data) + 2  # Start from the next empty row
    app.run(debug=True)
