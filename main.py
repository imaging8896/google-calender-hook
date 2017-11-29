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
processed_events_file = "processed_events"

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
    pattern = "OTT Builder"
    now = datetime.datetime.utcnow().isoformat()
    api = CalenderAPI()
    # cur_events = [x for x in api.get_events("kkbox.com_5c6vv9p0ee4dk70cb6rmm54kao@group.calendar.google.com") if x["summary"].startswith(pattern)]
    cur_events = [x for x in api.get_events("kkbox.com_5c6vv9p0ee4dk70cb6rmm54kao@group.calendar.google.com")]
    msg_buf = ""

    if os.path.isfile(processed_events_file):
        with open(processed_events_file, "rb") as fin:
            processed_events = pickle.load(fin)
            # Filter old data
            cancelled_events = [x for x in cur_events if x["status"] == "cancelled"]
            non_cancelled_events = [x for x in cur_events if x["status"] != "cancelled"]

            processed_event_ids = [x["id"] for x in processed_events]
            non_cancelled_event_ids = [x["id"] for x in non_cancelled_events]
            cancelled_event_ids = [x["id"] for x in cancelled_events]
            del_event_ids = list(set(processed_event_ids) & set(cancelled_event_ids))
            # print str(set(processed_event_ids))
            # print str(set(cur_event_ids))
            new_event_ids = list(set(non_cancelled_event_ids) - set(processed_event_ids))
            remained_processed_event_ids = list(set(processed_event_ids) - set(del_event_ids))

            store_events = [x for x in cur_events if x["id"] in remained_processed_event_ids]
            for event in [x for x in processed_events if x["id"] in del_event_ids]:
                msg_buf += "Removed event '{}'\n".format(event["summary"])
                # Do something

            for event in [x for x in cur_events if x["id"] in new_event_ids]:
                msg_buf += "New event '{}'\n".format(event["summary"])
                # Do something
                store_events += [dict(event)]
    else:
        store_events = [x for x in cur_events if x["status"] != "cancelled"]
        msg_buf += "Initialize...\n"
    with open(processed_events_file, "wb+") as fout:
        pickle.dump(store_events, fout)
    print msg_buf
