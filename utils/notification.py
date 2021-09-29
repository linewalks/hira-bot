from json import dumps
from httplib2 import Http


def send_message(msg):
    url = 'https://chat.googleapis.com/v1/spaces/AAAARTaMFug/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=t-AsqJo52GoF0jiqVehUA1H5yojIRd0DbD8LSjdkuSg%3D'
    bot_message = {
        'text' : msg}

    message_headers = {'Content-Type': 'application/json; charset=UTF-8'}

    http_obj = Http()

    response = http_obj.request(
        uri=url,
        method='POST',
        headers=message_headers,
        body=dumps(bot_message),
    )
