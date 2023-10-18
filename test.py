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

# app = Flask(__name)

# # Initialize the 'data' dictionary to store user data
# data = {}

# # Create a scheduler
# scheduler = BackgroundScheduler()

# # Load credentials from the JSON key file
# gc = None

# try:
#     gc = pygsheets.authorize(service_file='your-credentials.json')
# except exceptions.DefaultCredentialsError as e:
#     print("Error loading Google Sheets credentials. Make sure to set up Google Sheets API credentials.")

# # Open the Google Sheet by title or URL
# sheet = None  # Will be set in schedule_extraction

# def convert_xpath_to_bs_readable(xpath):
#     # A function to convert XPath to BeautifulSoup-readable format
#     return xpath.replace('>', ' ').replace('//', ' ').replace('@', '')

# def save_user_data(user_id):
#     user_data = data.get(user_id, {})
#     with open(os.path.join("user_data", f"{user_id}.json"), "w") as file:
#         json.dump(user_data, file)

# def save_data_to_google_sheet(url, xpath, time, extracted_text, sheet, sheet_title):
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
#         print(f"An error occurred while saving data to Google Sheet: {str(e}")

# def data_extraction_job(user_id, url, xpath, sheet_title, index=None):
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             soup = BeautifulSoup(response.text, 'html.parser')

#             if index is not None:
#                 elements = soup.select(convert_xpath_to_bs_readable(xpath))
#                 if 0 <= index < len(elements):
#                     extracted_text = elements[index].get_text()
#                 else:
#                     extracted_text = "Index out of range"
#             else:
#                 extracted_text = soup.select_one(convert_xpath_to_bs_readable(xpath)).get_text()
            
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
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")

# @app.route('/<user_id>/schedule')
# def schedule_page(user_id):
#     return render_template('schedule.html', user_id=user_id)

# @app.route('/<user_id>/schedule', methods=['POST'])
# def schedule_extraction(user_id):
#     user_data = data.get(user_id, {})
#     url = request.form.get('url')
#     xpath = request.form.get('xpath')
#     schedule_time = request.form.get('time')
#     sheet_title = request.form.get('sheet_title')
#     index = request.form.get('index')
    
#     # Schedule data extraction job
#     if schedule_time:
#         hour, minute = map(int, schedule_time.split(':'))
#         trigger = CronTrigger(hour=hour, minute=minute)
#         scheduler.add_job(data_extraction_job, trigger=trigger, args=(user_id, url, xpath, sheet_title, index))
    
#     user_data[url] = ""
#     data[user_id] = user_data
#     save_user_data(user_id)
#     return redirect(url_for('get_data', user_id=user_id))

# if __name__ == '__main__':
#     app.run(debug=True)


import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

# Get the URL from the user
url = input("Enter the URL to open: ")

# Get the XPath from the user
xpath = input("Enter the XPath: ")

# Get the index of the XPath from the user
index = input("Enter the index of the XPath: ")

# Create a new headless WebDriver instance
options = webdriver.ChromeOptions()

driver = webdriver.Chrome(options=options)

# Open the URL in the browser
driver.get(url)

# Find the element at the specified XPath and index
element = driver.find_element(By.XPATH,xpath)

# Get the text of the element
text = element.text

# Print the text to the terminal
print(text)

# Close the WebDriver instance
driver.quit()
