import httplib2
import os
from os.path import join as path_join

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import pickle


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
home_dir = os.path.expanduser('~')
credential_dir = path_join(home_dir, '.credentials')
client_secret = path_join(home_dir, 'client_secret.json')
processed_events = "processed_events"

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

        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)

    def get_events(self, calender_id):
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

        result = self.service.events().list(
            # calendarId='primary', timeMin=now, maxResults=10, singleEvents=True,
            calendarId=calender_id, timeMin=now, singleEvents=True,
            orderBy='startTime').execute()

        events = []
        for event in result.get('items', []):
            events += [{
                "id": event["id"],
                "summary": event["summary"],
                "start": event["start"]["dateTime"],
                "end": event["end"]["dateTime"],
                "attendees": [x["email"] for x in event["attendees"]]
            }]
        return events


if __name__ == '__main__':
    pattern = "[Yo]"
    now = datetime.datetime.utcnow().isoformat()
    api = CalenderAPI()
    cur_events = [x for x in api.get_events("primary") if x["summary"].startswith(pattern)]
    msg_buf = ""

    if os.path.isfile(processed_events):
        with open(processed_events, "rb") as fin:
            processed_events = pickle.load(fin)
            # Filter old data
            processed_events = [x for x in processed_events if now < x["end"]]

            processed_event_ids = [x["id"] for x in processed_events]
            cur_event_ids = [x["id"] for x in cur_events]
            del_event_ids = list(set(processed_event_ids) - set(cur_event_ids))
            new_event_ids = list(set(cur_event_ids) - set(processed_event_ids))
            remained_processed_event_ids = list(set(processed_event_ids) - set(del_event_ids))

            store_events = [x for x in cur_events if x["id"] in remained_processed_event_ids]
            for event in [x for x in processed_events if x["id"] in del_event_ids]:
                msg_buf += "Removed event '{}'\n".format(event["summary"])
                # Do something

            for event in [x for x in cur_events if x["id"] in new_event_ids]:
                msg_buf += "New event '{}'\n".format(event["summary"])
                # Do something
                store_events += [event]
            store_events = processed_events
    else:
        store_events = cur_events
        msg_buf += "Initialize...\n"
    with open(processed_events, "wb+") as fout:
        pickle.dump(store_events, fout)
    print msg_buf




    print str(api.get_events("primary"))
