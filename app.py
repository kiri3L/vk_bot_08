import time
import threading
import vk_methods
import requests

token_group = 'c77108dcb98bfcba34d6e1677a95f543b0f6f3de916b192392edaffda02653d57b28e464a0474a0b6f4b3'
token = '871c43f8871c43f8871c43f8e48775650d8871c871c43f8db9e1794b6a645f4b89b124b'
version_api = '5.95'
MAX_USERS_IN_EXECUTE = 25_000
MAX_USERS_IN_USERS_GET = 1_000
PERIOD_SEC = 20
CODE_TEMPLATE = ' var %s = API.users.get({ "user_ids": "%s", "fields": "online,last_seen"});\n'
RETURN_CODE_TEMPLATE = '[ %s@.id, %s@.online, %s@.last_seen@.time ]'
USERS_GET_URL = 'https://api.vk.com/method/users.get?'
EXECUTE_URL = 'https://api.vk.com/method/execute?'
FRIENDS_GET_URL = 'https://api.vk.com/method/friends.get?'

""" Код Лены """

import mysql.connector

db = {'host': 'localhost',
      'user': 'vsearch',
      'password': 'vsearchpasswd',
      'database': 'vkbotDB', }



def ins_CUR_DATE(values):
    conn = mysql.connector.connect(**db)
    cursor = conn.cursor()
    REQ = """insert into cur_date
            values(%s,%s,%s)"""
    cursor.execute(REQ, values)
    conn.commit()
    cursor.close()
    conn.close()


def ins_CUR_MONTH_from_CUR_DATE(d1,d2,d3):
    conn = mysql.connector.connect(**db)
    cursor = conn.cursor()
    print('__________________________insert__current___month_________________')
    REQ = """insert into cur_month (user_id,date,spent_time)
            select user_id,(%s) as date, sum(temp_session) from cur_date
            where (last_enter > %s and last_enter < %s)
            group by user_id""" % (d1, d2, d3)
    cursor.execute(REQ)
    conn.commit()
    cursor.close()
    conn.close()


def show_CUR_DATE():
    conn = mysql.connector.connect(**db)
    cursor = conn.cursor()
    print('__________________________show__current___date_________________')
    REQ = """select * from cur_date"""
    cursor.execute(REQ)
    for row in cursor.fetchall():
        print(row)
    cursor.close()
    conn.close()

def show_CUR_MONTH():
    conn = mysql.connector.connect(**db)
    cursor = conn.cursor()
    print('___________________________show__current_month_________________')
    REQ = """select * from cur_month"""
    cursor.execute(REQ)
    for row in cursor.fetchall():
        print(row)

    cursor.close()
    conn.close()

def delete(table):
    conn = mysql.connector.connect(**db)
    cursor = conn.cursor()
    if (table == 'month'):
        print('_____________________________DELETE__FROM__MONTH___________________')
        REQ = """delete from cur_month"""
    elif (table == 'date'):
        print('_____________________________DELETE__FROM__DATE___________________')
        REQ = """delete from cur_date"""
    cursor.execute(REQ)
    conn.commit()
    cursor.close()
    conn.close()

""" Код Лены """

class User:
    id: int
    online: int
    last_seen: int
    session_time: int

    def __init__(self, id):
        self.id = id
        self.online = 0
        self.last_seen = 0
        self.session_time = 0

    def add_new_info(self,id,online,last_seen):
        if self.id == id:
            if self.online > online:
                pass
                self.online = 0
                self.session_time = last_seen - self.last_seen
                print('ins_CUR_DATE(($s, $s , $s))'.format(id, self.last_seen, self.session_time))
                ins_CUR_DATE((id, self.last_seen, self.session_time))
            if self.online < online:
                self.online = 1
                self.last_seen = last_seen
        else:
            print(' Error ')

    def get_id_in_str(self):
        return str(self.id)


def app_start():
    global users
    connect = vk_methods.connect_to_server()
    r3 = vk_methods.get_updates(connect[0], connect[1], connect[2])
    print('app_start', r3.text)
    while True:
        sender = vk_methods.get_sender_id(r3.text)
        if sender:
            # vk_methods.get_attachments(r3.text)
            txt = vk_methods.get_message_text(r3.text)
            name = vk_methods.get_sender_info(sender)['first_name']
            if txt == 'добавь меня':
                vk_methods.send_messages(sender, 'Вы добавлены!')
                users.append(User(sender))
            elif txt == 'привет':
                vk_methods.send_messages(sender, 'Привет, ' + name + '. Хочешь узнать, как много времени ты роводишь в вк?\n'
                                                                     ' напиши "добавь меня"')

        ts = r3.json()['ts']
        time.sleep(10)
        r3 = vk_methods.get_updates(connect[0], ts, connect[2])
        print(r3.text)

users = []

t = threading.Thread(app_start())
t.start()

def code_create(ids_in_str: list):
    code_body = CODE_TEMPLATE
    code_return = RETURN_CODE_TEMPLATE
    code_body = code_body % ('a0', ids_in_str[0])
    code_return = code_return % ('a0', 'a0', 'a0')
    for i in range(1, len(ids_in_str)):
        code_body += CODE_TEMPLATE
        code_return += ',' + RETURN_CODE_TEMPLATE
        code_body = code_body % ('a' + str(i), ids_in_str[i])
        code_return = code_return % ('a' + str(i), 'a' + str(i), 'a' + str(i))
    return code_body + ' return [%s];' % code_return


def parse_response(r):
    id = []
    online = []
    t = []
    for i in r:
        id.extend(i[0])
        online.extend(i[1])
        t.extend(i[2])
    return [id, online, t]


def get_vk_response(code):
    print(code)
    r = requests.get(EXECUTE_URL, params={'code': code, 'access_token': token_group, 'v': version_api})
    print(r)
    print(r.text)
    r = r.json()
    if 'response' in r:
        return parse_response(r['response'])
    else:
        print(' ERROR get_vk_response ')
        exit(-1)


l = ''

while True:
    if users:
        l = users[0].get_id_in_str()
        for i in range(1, len(users)):
            l += ',' + users[i].get_id_in_str
            i += 1
        code = code_create(l)
        resp = get_vk_response()
        i = 0
        for u in users:
            u.add_new_info(resp[0][i],resp[1][i],resp[2][i])
    time.sleep(5)





