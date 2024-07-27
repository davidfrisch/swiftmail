import sys
import os 
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from simplegmail import Gmail
from simplegmail.query import construct_query

gmail = Gmail() # will open a browser window to ask you to log in and authenticate
path = "../tasks/dataset/"

for filename in os.listdir(path):
    if filename.endswith(".json") and "fake" in filename:
        with open(path+filename, 'r') as file:
            data = json.load(file)
            email = data['email']
            subject = email.split("\n\n")[0].split("Subject: ")[1]
            body = email.split("\n\n")[1]

            params = {
              "to": "xxx@gmail.com",
              "sender": "xxx@gmail.com",
              "subject": subject,
              "msg_plain": body,
            }
            
            message = gmail.send_message(**params)
            print(f"Sent email from file {filename}")