import httplib2
import os
from os.path import join as path_join

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
home_dir = os.path.expanduser('~')
credential_dir = path_join(home_dir, '.credentials')
client_secret = path_join(credential_dir, 'client_secret.json')

SCOPES = 'https://www.googleapis.com/auth/calendar'
APPLICATION_NAME = 'Google Calendar API Hook'


class CalenderAPI(object):

    def __init__(self):

        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = path_join(credential_dir, 'calendar-python-quickstart.json')
        store = Storage(credential_path)

        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(client_secret, SCOPES)
            flow.user_agent = APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)

        self.credentials = credentials
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

    def get_access_token(self):
        return self.credentials.access_token

    def stop_events_watch(self, channel_id, resource_id):
        result = self.service.channels().stop(body={
            "id": channel_id,  # A UUID for the channel
            # "resourceUri": "",  # The canonicalized ID of the watched resource.
            "kind": "api#channel",      # A channel watching an API resource
            "resourceId": resource_id,   # An opaque id that identifies the resource that is being watched. Stable across different API versions
            # "token": "A String", # An arbitrary string associated with the channel that is delivered to the target address with each event delivered over this channel.
            # "params": { # Additional parameters controlling delivery channel behavior
            #     "a_key": "A String", # Declares a new parameter by name.
            # },
            # "expiration": "A String", # The expiration instant for this channel if it is defined.
            # "address": "A String", # The address of the receiving entity where events are delivered. Specific to the channel type.
            # "type": "A String", # The type of delivery mechanism used by this channel
        }).execute()
        return result

    def set_events_watch(self, calender_id, channel_id, hook_address, hook_type="web_hook"):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        result = self.service.events().watch(calendarId=calender_id, timeMin=now, singleEvents=False, showDeleted=True, body={
            # "resourceUri": "A String",  # The canonicalized ID of the watched resource.
            "kind": "api#channel",  # A channel watching an API resource
            # "resourceId": "A String",
        # An opaque id that identifies the resource that is being watched. Stable across different API versions
        #     "token": "A String",
        # An arbitrary string associated with the channel that is delivered to the target address with each event delivered over this channel.
        #     "params": {  # Additional parameters controlling delivery channel behavior
        #         "a_key": "A String",  # Declares a new parameter by name.
        #     },
        #     "expiration": "A String",  # The expiration instant for this channel if it is defined.
            "address": hook_address,
        # The address of the receiving entity where events are delivered. Specific to the channel type.
            "type": hook_type,  # The type of delivery mechanism used by this channel
            "id": channel_id,  # A UUID for the channel
        }).execute()
        return result

    def get_events(self, calender_id):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        result = self.service.events().list(
            # calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
            calendarId=calender_id, timeMin=now, singleEvents=False, showDeleted=True).execute()

        all_raw_events = result.get('items', [])
        events = []
        for event in all_raw_events:
            events += [{
                "id": event["id"],
                "status": event["status"],
                "summary": event["summary"] if "summary" in event else "",
                "start": event["start"]["dateTime"] if "dateTime" in event["start"] else event["start"]["date"],
                "end": event["end"]["dateTime"] if "dateTime" in event["end"] else event["end"]["date"],
                "attendees": [x["email"] for x in event["attendees"]] if "attendees" in event else []
            }]
        return events


if __name__ == '__main__':
    api = CalenderAPI()
    print api.get_access_token()

