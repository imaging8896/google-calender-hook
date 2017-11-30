from api import CalenderAPI


if __name__ == '__main__':
    api = CalenderAPI()
    print api.get_access_token()