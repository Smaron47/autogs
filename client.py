# import requests
# import hashlib
# import json

# # Flask API URL
# API_URL = "http://localhost:5000"  # Update with your actual API URL

# def generate_user_id(username, password):
#     # Combine the username and password, and hash the combination
#     user_id = hashlib.sha256(f"{username}:{password}".encode()).hexdigest()
#     return user_id

# def create_user(username, password, credentials_file):
#     # Generate the user_id
#     user_id = generate_user_id(username, password)

#     # Read credentials file content
#     with open(credentials_file, "r") as file:
#         credentials = file.read()

#     # Create a new user profile with credentials
#     response = requests.post(f"{API_URL}/{user_id}/create_user", json=json.loads(credentials))

#     if response.status_code == 200:
#         print(f"User created successfully with ID: {user_id}")
#         print(f"Access the URL: {API_URL}/{user_id}/schedule")
#     else:
#         print(f"Failed to create a user. Status Code: {response.status_code}")
#         print(response.text)

# if __name__ == "__main__":
#     # Input the username, password, and path to the credentials file
#     username = input("Enter your username: ")
#     password = input("Enter your password: ")
#     credentials_file_path = "credet.json"

#     create_user(username, password, credentials_file_path)




import requests

# Define the URL of your Flask app
FLASK_URL = 'http://127.0.0.1:5000/add_task'


url=input("Enter your URL: ")
xpath=input("Enter your xpath: ")
column_names=input("Enter your column names for your schedule: ")
time_to_run=input("Enter your time to run: ")



# Data to schedule data extraction
data = {
    'url': url,
    'xpath': xpath,  # Modify this XPath
    
    'time': time_to_run  # Specify the time to run data extraction
}

# Make a POST request to schedule data extraction
response = requests.post(FLASK_URL, json=data)

if response.status_code == 200:
    print("Done")
else:
    print("Error scheduling data extraction:", response.text)
