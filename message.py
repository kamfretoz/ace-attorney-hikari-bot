import hikari
import re
from emoji.core import demojize
import requests
from objection_engine.beans.comment import Comment

class Message:
    def __init__(self, update: hikari.Message):
        self.user = User(update.author)
        self.evidence = None
        print(update.content)
        tmp = re.sub(r'(https?)\S*', '(link)', update.content) # links
        tmp = demojize(tmp)
        tmp = re.sub(r'<[a]?:\w{2,32}:\d{18}>', '', tmp) # custom static and animated emojis
        tmp = re.sub(r':\w{2,32}:', '', tmp) # stock emojis
        tmp = re.sub(r'​', '', tmp) # @everyone, @here 
        for file in update.attachments: # attachments
            if file.filename.split('.')[-1] in {'jpg', 'jpeg', 'JPG', 'JPEG', 'png', 'PNG'}:
                tmp += ' (image)'
                name = str(file.id) + '.png'
                response = requests.get(file.url)
                print(response)
                with open(name, 'wb') as file:
                    file.write(response.content)
                self.evidence = name
            elif file.filename.split('.')[-1] in {'gif', 'gifv'}:
                tmp += ' (gif)'
            elif file.filename.split('.')[-1] in {'mp4', 'webm'}:
                tmp += ' (video)'
            elif file.filename.split('.')[-1] in {'mp3', 'wav', 'ogg'}:
                tmp += ' (audio)'
            else:
                tmp += ' (file)'
        for embed in update.embeds:
            if embed.type == 'image':
                tmp += ' (image)'
                url = embed.thumbnail.proxy_url
                name = url.split('/')[-1]
                response = requests.get(url)
                with open(name, 'wb') as file:
                    file.write(response.content)
                self.evidence = name
        self.text = tmp
    def to_Comment(self):
        return Comment(user_id=self.user.id, user_name=self.user.name, text_content=self.text, evidence_path=self.evidence)

class User:
    def __init__(self, user: hikari.Member):
        self.name = user.username
        self.id = user.id
