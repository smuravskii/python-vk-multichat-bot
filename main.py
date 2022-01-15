from decouple import config
from random import randint
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from db import DB

TOKEN = config('TOKEN')

vk = vk_api.VkApi(token=TOKEN)
give = vk.get_api()
longpoll = VkLongPoll(vk)


def command_check(command: str, msg: str) -> bool:
    if command == msg[:len(command)]:
        return True
    return False


def send_msg_to_user(vk_id: int, text: str) -> bool:
    try:
        vk.method('messages.send', {'user_id': vk_id, 'message': text, 'random_id': randint(0, 10000)})
        return True
    except Exception as e:
        print(e)
        return False


def send_msg_to_all(user, msg: str, style: str = 'Default') -> bool:
    receivers_list_cut = []
    receivers_list = DB.get_users_for_msg(user.id)
    x, y = divmod(len(receivers_list), 99)
    if y > 0:
        x += 1
    for i in range(x):
        list_str = []
        for r in receivers_list[-99:]:
            list_str.append(r)
        receivers_list_cut.append(list_str)
        del receivers_list[-99:]
    if style == 'Default':
        text = f"💬 [Global]{' [Admin]' if user.is_admin == 1 else ''} {user.username} ({user.id}):\n{msg}"
    else:
        text = msg
    for ids in receivers_list_cut:
        try:
            vk.method('messages.send', {'user_ids': ids, 'message': text, 'random_id': randint(0, 10000)})
            DB.add_massage(text, user.id)
        except Exception as e:
            print(e)
            return False
    return True


def set_user_nick(user, uid: int, nick: str):
    if len(nick) < 20:
        if user is False:
            query = DB.create_user_nick(uid, nick)
        else:
            query = DB.update_user_nick(uid, nick)

        if query:
            send_msg_to_user(uid, f'Отлично! Твой ник: {nick}')
        else:
            send_msg_to_user(uid, f'Что-то пошло не так! Попробуй еще раз!')
    else:
        send_msg_to_user(uid, f'Твой ник слишком длинный, сделай его короче 20 символов...')


def add_user_to_chat(uid) -> bool:
    if DB.set_in_chat(uid, True):
        send_msg_to_user(uid, 'Welcome to the club, buddy! Ты в чате!')
        return True
    else:
        send_msg_to_user(uid, 'Что-то пошло не так! Попробуй еще раз!')
        return False


def remove_user_from_chat(uid) -> bool:
    if DB.set_in_chat(uid, True):
        send_msg_to_user(uid, 'Иди нах! Ты нам больше не нужен!')
        return True
    else:
        send_msg_to_user(uid, 'Что-то пошло не так! Попробуй еще раз!')
        return False


def ban_user(uid, _id) -> bool:
    banned_user = DB.get_user_by_id(_id)
    if banned_user is False:
        send_msg_to_user(uid, 'Такого пользователя не существует!')
        return False
    if DB.set_ban(_id, True):
        send_msg_to_user(uid, f'ID:{_id} забанен!')
        send_msg_to_user(banned_user.vk_id, f'Пес, ты получил бан. Гавкай...')
        return True
    else:
        send_msg_to_user(uid, 'Что-то пошло не так! Попробуй еще раз!')
        return False


def unban_user(uid, _id) -> bool:
    banned_user = DB.get_user_by_id(_id)
    if banned_user is False:
        send_msg_to_user(uid, 'Такого пользователя не существует!')
        return False
    if DB.set_ban(_id, False):
        send_msg_to_user(uid, f'ID:{_id} разбанен!')
        send_msg_to_user(banned_user.vk_id, f'С тебя сняли бан! Переставай гавкать...')
        return True
    else:
        send_msg_to_user(uid, 'Что-то пошло не так! Попробуй еще раз!')
        return False


def start_direct_massaging(user, ls_id) -> bool:
    ls_user = DB.get_user_by_id(ls_id)
    if ls_user is False:
        send_msg_to_user(user.vk_id, 'Такого пользователя не существует!')
        return False
    if DB.user_direct_massaging(user.id, ls_user.vk_id):
        send_msg_to_user(user.vk_id, f'Открыт чат с {ls_user.username}')
        return True
    else:
        send_msg_to_user(user.vk_id, 'Что-то пошло не так! Попробуй еще раз!')
        return False


def stop_direct_massaging(user) -> bool:
    if DB.user_direct_massaging(user.id, 0):
        send_msg_to_user(user.vk_id, f'Ок, теперь твои сообщения идут в общий чат!')
        return True
    else:
        send_msg_to_user(user.vk_id, 'Что-то пошло не так! Попробуй еще раз!')
        return False


def send_ls_msg_to_user(user, message):
    text = f"💬 ЛС{' [Admin]' if user.is_admin == 1 else ''} {user.username} ({user.id}):\n{message}"
    return send_msg_to_user(user.ls_with, text)


def info_about_user(user):
    all_massages = DB.get_all_massages()
    if all_massages is not False:
        _all_massages = len(all_massages)
    else:
        _all_massages = 1
    if _all_massages == 0:
        _all_massages = 1

    user_massages = DB.get_massages_by_id(user.id)
    if user_massages is not False:
        _user_massages = len(user_massages)
    else:
        _user_massages = 1
    if _user_massages == 0:
        _user_massages = 1

    text = f'''
👤 Ник: {user.username}
Роль: {'Admin' if user.is_admin == 1 else 'Участник'}
Твой ID: {user.id}

Всего сообщений: {_all_massages}
Твоих сообщений: {_user_massages} ({round(_user_massages / _all_massages * 100)}%)
'''
    return send_msg_to_user(user.vk_id, text)


def online_users(user):
    text = 'Сейчас онлайн в чате: \n\n'
    users = DB.get_online_users()
    if users is not False:
        for _user in users:
            text += f'👤 {_user.username} (ID: {_user.id}) \n'
        return send_msg_to_user(user.vk_id, text)
    else:
        send_msg_to_user(user.vk_id, 'Что-то пошло не так! Попробуй еще раз!')
        return False


def main():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            vk_user_id = event.user_id
            message = event.text.strip()
            if message == '':
                send_msg_to_user(vk_user_id, 'Я не могу обработать такой тип сообщения!')
                continue
            print(message)
            user = DB.get_user_by_vk_id(vk_user_id)
            if message[0] == '/':
                if command_check('/nick', message):
                    user_nick = message.replace('/nick', '')
                    set_user_nick(user, vk_user_id, user_nick.strip())
                    continue
            if user is not False:
                if user.is_banned == 1:
                    send_msg_to_user(vk_user_id, 'Пес, ты в бане, нахуя пишешь?')
                    continue
                if message[0] == '/':
                    if command_check('/start', message):
                        add_user_to_chat(vk_user_id)
                        send_msg_to_all(user,
                                        f'❗ {user.username} (ID: {user.id}) - добавился к нам.', style='System')
                        continue
                    elif command_check('/stop', message):
                        remove_user_from_chat(vk_user_id)
                        send_msg_to_all(user,
                                        f'❗ {user.username} (ID: {user.id}) - эта тварь вышла из чата, время его обоссать.', style='System')
                        continue
                    elif command_check('/ls ', message):
                        ls_id = message.replace('/ls ', '')
                        try:
                            ls_id = int(ls_id)
                        except Exception as e:
                            print(e)
                            continue
                        start_direct_massaging(user, ls_id)
                        continue
                    elif command_check('/ls_stop', message):
                        stop_direct_massaging(user)
                        continue
                    elif command_check('/info', message):
                        info_about_user(user)
                        continue
                    elif command_check('/online', message):
                        online_users(user)
                        continue
                    elif command_check('/ban', message) and user.is_admin == 1:
                        user_id = message.replace('/ban ', '')
                        ban_user(vk_user_id, user_id)
                        continue
                    elif command_check('/unban', message) and user.is_admin == 1:
                        user_id = message.replace('/unban ', '')
                        unban_user(vk_user_id, user_id)
                        continue
                    else:
                        send_msg_to_user(vk_user_id, 'Нет такой команды :(')
                        continue
                elif user.in_chat == 1:
                    if user.ls_with == 0:
                        if send_msg_to_all(user, message) is False:
                            send_msg_to_user(vk_user_id, 'Не удалось отправить сообщение, уже все чиним.')
                        continue
                    else:
                        if send_ls_msg_to_user(user, message) is False:
                            send_msg_to_user(vk_user_id, 'Не удалось отправить сообщение, уже все чиним.')
                        continue
                else:
                    send_msg_to_user(vk_user_id, 'Вы не в чате, пишите /start')
            else:
                send_msg_to_user(vk_user_id, 'Нужно вначале войти, пиши /nick')
                continue


if __name__ == '__main__':
    main()
