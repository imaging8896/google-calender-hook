import os
import datetime
import pickle

from api import CalenderAPI

processed_events_file = "processed_events"


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
