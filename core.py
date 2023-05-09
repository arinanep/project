from datetime import datetime 

import vk_api
import requests
from vk_api.longpoll import VkLongPoll, VkEventType

from config import acces_token, comunity_token




class VkTools():
    def __init__(self, acces_token):
       self.api = vk_api.VkApi(token=acces_token)

    def get_profile_info(self, user_id):

        info, = self.api.method('users.get',
                            {'user_id': user_id,
                            'fields': 'city,bdate,sex,relation,home_town' 
                            }
                            )
        user_info = {'name': info['first_name'] + ' '+ info['last_name'],
                     'id':  info['id'],
                     'bdate': info['bdate'] if 'bdate' in info else None,
                     'home_town': info['home_town'] if 'home_town' in info else None,
                     'sex': info['sex'],
                     'city': info['city']['id']
                     }
        

        vk_session = vk_api.VkApi(token=comunity_token)
        longpoll = VkLongPoll(vk_session)
        vk = vk_session.get_api()

        if user_info['bdate'] == None:
            self.message_send(event.user_id, f'Напиши дату рождения в формате 00.00.0000')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    user_info['bdate'] = event.text

        if user_info['sex'] == None:
            self.message_send(event.user_id, f'Напиши свой пол')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    command = event.text.lower()

                    if command == 'мужской':
                        user_info['sex'] = 2
                    else:
                        user_info['sex'] = 1

        if user_info['home_town'] == None:
            self.message_send(event.user_id, f'Напиши родной город')
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    user_info['home_town'] = event.text


        return user_info
    
    def serch_users(self, params):

        sex = 1
        if params['sex'] == 2:
            sex = 1  
        else:
            sex = 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = int(params['bdate'].split('.')[2])
        age = curent_year - user_year
        age_from = age - 5
        age_to = age + 5
        offset = 0

        users = self.api.method('users.search',
                                {'count': 10,
                                 'offset': offset,
                                 'age_from': age_from,
                                 'age_to': age_to,
                                 'sex': sex,
                                 'city': city,
                                 'status': 6,
                                 'is_closed': False
                                }
                            )
        try:
            users = users['items']
        except KeyError:
            return []
        
        res = []

        for user in users:
            if user['is_closed'] == False:
                res.append({'id' : user['id'],
                            'name': user['first_name'] + ' ' + user['last_name']
                           }
                           )
        offset += 10
        
        return res

    def get_photos(self, user_id):
        photos = self.api.method('photos.get',
                                 {'user_id': user_id,
                                  'album_id': 'profile',
                                  'extended': 1
                                 }
                                )
        try:
            photos = photos['items']
        except KeyError:
            return []
        
        res = []

        for photo in photos:
            res.append({'owner_id': photo['owner_id'],
                        'id': photo['id'],
                        'likes': photo['likes']['count'],
                        'comments': photo['comments']['count'],
                        }
                        )
            
        res.sort(key=lambda x: x['likes']+x['comments']*10, reverse=True)

        return res


if __name__ == '__main__':
    bot = VkTools(acces_token)
    params = bot.get_profile_info(798095924)
    users = bot.serch_users(params)
    print(bot.get_photos(users[2]['id']))


