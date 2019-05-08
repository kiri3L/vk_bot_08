import requests
import re

token_group = 'c77108dcb98bfcba34d6e1677a95f543b0f6f3de916b192392edaffda02653d57b28e464a0474a0b6f4b3'


def get_sender_id(updates):
    r = re.search(r'from_id\":\d+', updates)
    if r:
        return re.search(r'\d+', r[0])[0]
    else:
        return None


def get_message_text(updates):
    r = re.search(r'text":"[^"]+', updates)
    if r[0] is not None:
        r = r[0].replace('text":"','')
    return r.lower()


def get_attachments(updates):
    print("I work ")
    r = re.search(r"attachments\":\[.+\]", updates)
    if r:
        r = re.search(r"\[.+\]", r[0])

    else: print(" but i @#%^!")


def get_sender_info(id):
    print('get_sender_info')
    r = requests.get('https://api.vk.com/method/users.get?',
                     params={'access_token': token_group,
                             'v': '5.92',
                             'user_ids': id})
    print(r.json()['response'])
    return r.json()['response'][0]


def send_messages(id, text, image=None, music=None):
    if image:
        requests.get('https://api.vk.com/method/messages.send?',
                     params={'user_id': id,
                             'random_id': 0,
                             'message': text,
                             'attachment': image,
                             'group_id': '179378864',
                             'access_token': token_group,
                             'v': '5.92'})
    else:
        requests.get('https://api.vk.com/method/messages.send?',
                     params={'user_id': id,
                             'random_id': 0,
                             'message': text,
                             'group_id': '179378864',
                             'access_token': token_group,
                             'v': '5.92'})


def connect_to_server():
    r2 = requests.get('https://api.vk.com/method/groups.getLongPollServer?',
                      params={'group_id': '179378864',
                              'access_token': token_group,
                              'v': '5.92'})

    print(r2)
    print(r2.text)
    print(r2.json())

    serv = r2.json()['response']['server']
    key = r2.json()['response']['key']
    ts = r2.json()['response']['ts']

    serv += '?'
    return serv, ts, key


def get_updates(serv, ts, key):
    r3 = requests.get(serv, params={'act': 'a_check', 'key': key, 'ts': ts})
    return r3