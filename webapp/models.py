import os
import threading
import time

from django.db import models, OperationalError
from django.shortcuts import get_object_or_404, get_list_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

# Create your models here.
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    def get_episodes(self, quality=None):
        if quality is None:
            return get_list_or_404(Episode, movie=self)
        else:
            return get_list_or_404(Episode, movie=self, quality=quality)

    def get_episode(self, ordinal, quality=None):
        if quality is None:
            episodes = get_list_or_404(Episode, movie=self, ordinal=ordinal)
            episode = max(episodes, key=lambda ep: ep.quality)
            return episode
        else:
            return get_object_or_404(Episode, movie=self, ordinal=ordinal, quality=quality)

class Episode(models.Model):
    id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    ordinal = models.IntegerField()
    quality = models.IntegerField(choices=[
        (1080, "1080p"),
        (720, "720p"),
        (480, "480p"),
        (360, "360p")
    ])
    file = models.FilePathField(path='/home/alex/temp-ftpfs/Animate', recursive=True)

    def __str__(self):
        try:
            return "Episode {} of {} ({})".format(self.ordinal, self.movie, self.quality)
        except ObjectDoesNotExist as e:
            return "Episode {} ({})".format(self.ordinal, self.quality)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = os.path.join(*(self.file.split(os.path.sep)[5:])) if self.file != "" else ""
        self.url = os.path.join(settings.VIDEO_STORAGE_URL, self.url)

class Party(models.Model):
    id = models.AutoField(primary_key=True)
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, null=True)
    progress = models.FloatField()
    lastUpdateTime = models.FloatField(default=0)
    isPlaying = models.BooleanField(default=False)

    def get_members(self, quiet=True):
        if quiet:
            try:
                return get_list_or_404(User, party=self)
            except:
                return []
        else:
            return get_list_or_404(User, party=self)

    def add_user(self, user):
        user.join(self)

    def getCurrentPlayTime(self):
        last_time = self.lastUpdateTime if self.lastUpdateTime != 0 else time.time()
        real_time = time.time()
        if self.isPlaying:
            return self.progress + real_time - last_time
        else:
            return self.progress

    def __str__(self):
        return "Party {} watching {}: <ul> {} </ul> ".format(
            self.id,
            self.episode,
            "\n".join(["<li>" + str(user) + "</li>" for user in self.get_members()]),
        )


user_notifiers = {}
user_need_reload = {}

class User(models.Model):
    id = models.AutoField(primary_key=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, null=True)
    watching_episode = models.ForeignKey(Episode, on_delete=models.CASCADE, null=True)
    vk = models.CharField(max_length=256, null=True)
    nickname = models.CharField(max_length=256, null=True)
    login_ip = models.GenericIPAddressField()

    def join(self, party):
        self.party = party
        self.watching_episode = party.episode

    def leaveParty(self):
        if len(self.party.get_members()) == 1:
            self.party.delete()
        self.party = None

    @staticmethod
    def new_user(ip):
        user = User.objects.create(login_ip=ip)
        user_notifiers[user.id] = threading.Event()
        user_need_reload[user.id] = False

        return user

    def get_notifier(self) -> threading.Event:
        return user_notifiers[self.id]

    def get_need_reload(self):
        return user_need_reload[self.id]

    def set_need_reload(self, val):
        user_need_reload[self.id] = val

    def __str__(self):
        if self.vk:
            return "<a href='https://vk.com/id{}'>{}</a>".format(self.vk, self.nickname)
        else:
            return "id {}, ip {}".format(self.id, self.login_ip)


try:
    for user in User.objects.all():
        user_notifiers[user.id] = threading.Event()
        user_need_reload[user.id] = False
except OperationalError as e:
    print("Failed to populate user list")



class Invitation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)

    def __str__(self):
        return "Invitation to party: {}".format(self.party)