import sys
from api import CalenderAPI


if __name__ == '__main__':
    channel_id = sys.argv[1]
    resource_id = sys.argv[2]
    api = CalenderAPI()
    print str(api.stop_events_watch(channel_id, resource_id))
