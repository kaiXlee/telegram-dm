import logging
from telethon import sync, TelegramClient, events
from telethon.tl.types import InputPeerChannel, PeerUser, DocumentAttributeVideo
from telethon.tl.types import InputPeerUser
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.errors.rpcerrorlist import PeerFloodError, UserPrivacyRestrictedError, FloodWaitError
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
import time
import traceback
import datetime
import os
import json




class MemberManager:
    myMsg = '''🤡ClownX🤡 is a project that aims to develop a WEB3 decentralized community brand with fashion. 

They aim to create a “real community brand” within the NFT world. They plan to attract like minded people who appreciate their art but stay for the community. A community with culture, shared value, and dope profile picture. 

⭐️HIgh Quality Art
🏁Large and detailed Roadmap in coming
🎁Free NFTs in contests

🎉🎉CLOWNLIST GIVEAWAY IS OPEN RIGHT NOW + FREE MINT SPOTS🎉🎉

To Enter: 
Go to their newest post on twitter do the following:

https://twitter.com/clownxnft/status/1526970874729009152?s=21&t=NWa2VAyVIfQ1GW4IlnXytw

1. Follow @ClownXnft
2. Like +RT + Tag Friends 
3. There is a code hidden in the video above which consist of several alphabets and numbers. Find out the exact code with the exact letter case and order then dm the official twitter account the answer to earn your FREE MINT SPOT.  1st and 50th will receive a free mint spot (We will announce once the free mint spots are taken, and we will provide proof in the thread)

Giveaway Ends in 72 hours!!!

There will be more giveaway in the future'''

    def __init__(self):
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config = json.loads(f.read())

        self.root_path = os.path.dirname(os.path.abspath(__file__))
        print("script path" + self.root_path)
        self.clients = []
        self.from_date_active = '19700101'
        if 'from_date_active' in self.config:
            self.from_date_active = self.config['from_date_active']
        logging.basicConfig(level=logging.WARNING)

    def get_group_by_id(self, groups, group_id):
        for group in groups:
            if group_id == int(group['group_id']):
                return group
        return None

    def init_clients(self):
        accounts = self.config['accounts']
        print("Total account: " + str(len(accounts)))
        folder_session = 'session/'

        for account in accounts:
            api_id = account['api_id']
            api_hash = account['api_hash']
            phone = account['phone']

            client = TelegramClient(folder_session + phone, api_id, api_hash)
            client.connect()

            if client.is_user_authorized():
                print(phone + ' login success')
                self.clients.append({
                    'phone': phone,
                    'client': client
                })
            else:
                print(phone + ' login fail')

    def get_users(self):
        group_source_id = self.config['group_source']
        client = self.clients[0]
        phone = client['phone']
        users_to_add_file = self.root_path + '\\data\\user\\' + phone + "_" + str(group_source_id) + '.json'
        with open(users_to_add_file, encoding='utf-8') as f:
            client['target_users'] = json.loads(f.read())
        send_count = 0
        video_file = 'C:/Projects/telegram-dm/telegram/data/items/promo_vid.mp4'
        metadata = extractMetadata(createParser(video_file))
        for user in client['target_users']:
            try:
                send_count += 1
                # count_add if added 35 user
                if send_count % 35 == 0:
                    print('sleep 15 minute')
                    time.sleep(15 * 60)
                entity = client['client'].get_entity(user['username'])
                # client['client'].send_message(entity=entity, message=self.myMsg)
                # time.sleep(0.5)
                # client['client'].send_file(entity=entity, file='C:/Projects/telegram-dm/telegram/data/items/picture.jpg')
                # time.sleep(0.5)
                # client['client'].send_file(entity=entity, file=video_file, attributes=(
                #                   DocumentAttributeVideo(
                #                       (0, metadata.get('duration').seconds)[metadata.has('duration')],
                #                       (0, metadata.get('width'))[metadata.has('width')],
                #                       (0, metadata.get('height'))[metadata.has('height')]
                #                   )))
                client['client'].send_file(entity=entity, file=video_file, attributes=(DocumentAttributeVideo(0, 0, 0),))
                time.sleep(0.5)
                print(f"messaged sent to: {user['username']}")

            except Exception as e:
                print(f"Error sending message to {user['user_id']}: {e}")

    def process_clients(self):
        filter_clients = []
        group_target_id = self.config['group_target']
        group_source_id = self.config['group_source']

        for my_client in self.clients:
            phone = my_client['phone']
            source_group_file = self.root_path + '/data/group/' + phone + '.json'
            users_to_add_file = self.root_path + '/data/user/' + phone + "_" + str(group_source_id) + '.json'

            if not os.path.isfile(source_group_file):
                print('This account with phone do not have data. Please run get_data or init_session')
                continue
            if not os.path.isfile(users_to_add_file):
                print('This account with phone ' + str(phone) + ' is not in source group')
                continue

            with open(source_group_file, 'r', encoding='utf-8') as f:
                groups = json.loads(f.read())
            current_target_group = self.get_group_by_id(groups, group_target_id)
            if not current_target_group:
                print('This account with phone ' + str(phone) + ' is not in target group')
                continue

            group_access_hash = int(current_target_group['access_hash'])
            target_group_entity = InputPeerChannel(group_target_id, group_access_hash)
            my_client['target_group_entity'] = target_group_entity      # add target_group_entity key value

            with open(users_to_add_file, encoding='utf-8') as f:
                my_client['users'] = json.loads(f.read())
            filter_clients.append(my_client)

        return filter_clients

    def run(self, filter_clients):
        start_time = datetime.datetime.now()
        # run
        previous_count = 0
        count_add = 0

        try:
            with open(self.root_path + '/current_count.txt') as f:
                previous_count = int(f.read())
        except Exception as e:
            pass

        print('From index: ' + str(previous_count))
        total_client = len(filter_clients)

        total_user = filter_clients[0]['users'].__len__()

        i = 0
        while i < total_user:
            # previous run
            if i < previous_count:
                i += 1
                continue

            # count_add if added 35 user
            if count_add % (35 * total_client) == (35 * total_client - 1):
                print('sleep 15 minute')
                time.sleep(15 * 60)

            total_client = filter_clients.__len__()
            print("remain client: " + str(total_client))
            if total_client == 0:
                with open(self.root_path + '/current_count.txt', 'w') as g:
                    g.write(str(i))
                    g.close()

                print('END: accounts is empty')
                break

            current_index = count_add % total_client
            print("current_index: " + str(current_index))
            current_client = filter_clients[current_index]
            client = current_client['client']
            user = current_client['users'][i]

            if user['date_online'] != 'online' and user['date_online'] < self.from_date_active:
                i += 1
                print('User ' + user['user_id'] + ' has time active: ' + user['date_online'] + ' is overdue')
                continue

            target_group_entity = current_client['target_group_entity']

            try:
                print('Adding member: ' + user['username'])
                user_to_add = InputPeerUser(int(user['user_id']), int(user['access_hash']))
                client(InviteToChannelRequest(target_group_entity, [user_to_add]))
                print('Added member '+ user['username'] +' successfully ;-)')
                count_add += 1
                print('sleep: ' + str(120 / total_client))
                time.sleep(120 / total_client)

            except PeerFloodError as e:
                print("Error Fooling cmnr")
                traceback.print_exc()
                print("remove client: " + current_client['phone'])
                client.disconnect()
                filter_clients.remove(current_client)

                # not increate i
                continue
            except UserPrivacyRestrictedError:
                print("Error Privacy")
            except FloodWaitError as e:
                print("Error Fooling cmnr")
                traceback.print_exc()
                print("remove client: " + current_client['phone'])
                client.disconnect()
                filter_clients.remove(current_client)

                continue
            except:
                print("Error other")
            # break
            i += 1

        with open(self.root_path + '/current_count.txt', 'w') as g:
            g.write(str(i))
            g.close()
        print("disconnect")
        for cli in self.clients:
            cli['client'].disconnect()
        end_time = datetime.datetime.now()
        print("total: " + str(count_add))
        print("total run time: " + str(end_time - start_time))


if __name__ == "__main__":
    manager = MemberManager()
    manager.init_clients()
    manager.get_users()
    #
    # filter_clients = manager.process_clients()
    # manager.run(filter_clients)
