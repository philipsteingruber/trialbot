import json
import os
import traceback

import discord
import discord.utils
from b2sdk.v2 import B2Api
from b2sdk.v2 import InMemoryAccountInfo

trials = ['piercing', 'swirling', 'crippling', 'burning', 'lingering', 'stinging']


class TrialBot(discord.Client):
    def __init__(self):
        filename = 'users_json.txt'
        if local:
            if not os.path.exists(filename):
                open(filename, mode='w').close()
            with open(filename, mode='r') as file:
                try:
                    self.registered_users = json.load(file)
                    print('Users loaded from JSON. Registered users: {}'.format(self.registered_users))
                except json.decoder.JSONDecodeError:
                    self.registered_users = {}
                    print('No registered users found.')
        else:
            info = InMemoryAccountInfo()
            b2_api = B2Api(info)
            b2_api.authorize_account("production", application_key_id, application_key)
            bucket = b2_api.get_bucket_by_name(bucket_name='discord-trialbot')
            bucket.download_file_by_name(file_name=filename).save_to(path_=filename)
            self.bucket = bucket
            with open(filename, mode='r') as file:
                self.registered_users = json.load(file)
                print('Users loaded from Backblaze. Registered users: {}'.format(self.registered_users))

        super(TrialBot, self).__init__(intents=discord.Intents.all())

    def users_as_str(self):
        user_list = []
        for user_id, uncompleted_trials in self.registered_users.items():
            user_list.append('{} has yet to complete: {}'.format(self.get_user_from_id(user_id).name, ', '.join(uncompleted_trials)))
        if not user_list:
            return 'No registered users'
        return '\n'.join(user_list)

    def get_user_from_id(self, id):
        return discord.utils.get(self.get_all_members(), id=int(id))

    def save_users_to_file(self):
        with open('users_json.txt', mode='w') as file:
            json.dump(fp=file, obj=self.registered_users)
            print('Successfully saved to local file')
        if not local:
            self.bucket.upload_local_file(local_file='users_json.txt', file_name='users_json.txt')
            print('Successfully saved to Backblaze')

    def users_who_need_trial(self, trial, author):
        mentions = []
        for user_id, uncompleted_trials in self.registered_users.items():
            if trial in uncompleted_trials and user_id != author.id:
                mentions.append(self.get_user_from_id(user_id).mention)
        return mentions

    async def on_ready(self):
        print('Bot initialized.')

    async def on_message(self, message):
        author, channel, content = message.author, message.channel, message.content

        if author.name != 'trialbot':
            if content.startswith('!register'):
                if str(author.id) not in self.registered_users:
                    try:
                        self.registered_users[str(author.id)] = trials.copy()
                        print('{} added to users.'.format(author.name))
                        self.save_users_to_file()
                    except Exception as e:
                        traceback.print_exc()
                        await channel.send('Registration of user {} failed. Try again.'.format(author.name))
                    else:
                        await channel.send('User {} registered successfully.'.format(author.name))
                        print('Registering user {}'.format(author.name))
                else:
                    await channel.send('User {} already registered.'.format(author.name))

            elif content.startswith('!users'):
                # print('!users')
                # await message.channel.send(content='hello')
                await channel.send(self.users_as_str())
                print('Listing registered users')

            elif content.startswith('!complete'):
                trial = content.split(' ')[1]
                if trial not in trials:
                    await channel.send('The entered trial, {}, is invalid.'.format(trial))
                else:
                    try:
                        self.registered_users[str(author.id)].remove(trial)
                        await channel.send('{} has now completed {}'.format(author.name, trial))
                        print('Marking {} as completed for {}'.format(trial, author.name))
                    except ValueError:
                        await channel.send('{} has already completed {}.'.format(author.name, trial))
                    else:
                        self.save_users_to_file()

            elif content.startswith('!reset'):
                try:
                    self.registered_users[str(author.id)] = trials.copy()
                    self.save_users_to_file()
                    await channel.send('All trials uncompleted for {}'.format(author.name))
                    print('Resetting completed trials for {}'.format(author.name))
                except Exception:
                    await channel.send('User not registered. Register with !register first.')

            elif content.startswith('!piercing'):
                mentions = self.users_who_need_trial(trial='piercing', author=author)
                if mentions:
                    await channel.send('{} {} has {} available. Remember to mark the trial completed using "!complete piercing" when done.'.format(' '.join(mentions), author.name, 'piercing truth'))
                else:
                    await channel.sent('Noone else needs {}.'.format('piercing'))

            elif content.startswith('!swirling'):
                mentions = self.users_who_need_trial(trial='swirling', author=author)
                if mentions:
                    await channel.send('{} {} has {} available. Remember to mark the trial completed using "!complete swirling" when done.'.format(' '.join(mentions), author.name, 'swirling fear'))
                else:
                    await channel.sent('Noone else needs {}.'.format('swirling'))

            elif content.startswith('!crippling'):
                mentions = self.users_who_need_trial(trial='crippling', author=author)
                if mentions:
                    await channel.send('{} {} has {} available. Remember to mark the trial completed using "!complete crippling" when done.'.format(' '.join(mentions), author.name, 'crippling grief'))
                else:
                    await channel.sent('Noone else needs {}.'.format('crippling'))

            elif content.startswith('!burning'):
                mentions = self.users_who_need_trial(trial='burning', author=author)
                if mentions:
                    await channel.send('{} {} has {} available. Remember to mark the trial completed using "!complete burning" when done.'.format(' '.join(mentions), author.name, 'burning rage'))
                else:
                    await channel.sent('Noone else needs {}.'.format('burning'))

            elif content.startswith('!lingering'):
                mentions = self.users_who_need_trial(trial='lingering', author=author)
                if mentions:
                    await channel.send('{} {} has {} available. Remember to mark the trial completed using "!complete lingering" when done.'.format(' '.join(mentions), author.name, 'lingering pain'))
                else:
                    await channel.sent('Noone else needs {}.'.format('lingering'))

            elif content.startswith('!stinging'):
                mentions = self.users_who_need_trial(trial='stinging', author=author)
                if mentions:
                    await channel.send('{} {} has {} available. Remember to mark the trial completed using "!complete stinging" when done.'.format(' '.join(mentions), author.name, 'stinging doubt'))
                else:
                    await channel.sent('Noone else needs {}.'.format('stinging'))

            elif content.startswith('!fullreset'):
                for user_id, uncompleted_trials in self.registered_users.items():
                    self.registered_users[user_id] = trials.copy()
                self.save_users_to_file()
                await channel.send('All users have been reset.')

            elif content.startswith('!help'):
                await channel.send('!register to register yourself.'
                                   '\n!complete <trial> to mark trial as completed for you.'
                                   '\n!<trial> to ping all users missing that trial.'
                                   '\n!users to print out all users and their uncompleted trials.'
                                   '\n!reset to mark all trials uncompleted for yourself.')


try:
    with open('config.txt', mode='r') as file:
        token = file.read()
        local = True
except FileNotFoundError:
    token = os.environ.get(key='TOKEN')
    application_key_id = os.environ.get(key='APPLICATION_KEY_ID')
    application_key = os.environ.get(key='APPLICATION_KEY')
    if not token or not application_key_id or not application_key:
        raise ValueError
    local = False
client = TrialBot()
client.run(token)
