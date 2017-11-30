import sys
from api import CalenderAPI
import pickle


if __name__ == '__main__':
    calendar_id = sys.argv[1]
    channel_id = sys.argv[2]
    web_hook_addr = sys.argv[3]
    api = CalenderAPI()
    result = api.set_events_watch(calendar_id, channel_id, web_hook_addr)
    print str(result)
    with open("channel_info", "w+") as fout:
        pickle.dump(result, fout)
