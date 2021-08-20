import json
import threading
import time

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from webapp.models import User, Party, Invitation, Movie
from webapp.utils import get_client_ip, RedirectResponse, pass_auth, get_list

for party in Party.objects.all():
    if len(party.get_members()) == 0:
        party.delete()


def createParty(request: HttpRequest, user):
    if (user.party):
        return HttpResponse("Player is already in party", status=400)
    party = Party.objects.create(progress=0)
    party.episode = user.watching_episode
    user.join(party)

    user.save()
    party.save()

    user.set_need_reload(True)
    user.get_notifier().set()

    return HttpResponse("OK")


def joinParty(request: HttpRequest, user):
    party_id = request.GET["party"]

    party = get_object_or_404(Party, id=party_id)

    user.join(party)

    user.save()
    party.save()

    invitations = get_list(Invitation, user=user)
    for inv in invitations:
        inv.delete()

    user.set_need_reload(True)
    user.get_notifier().set()

    return HttpResponse("OK")


def inviteToParty(request: HttpRequest, user):
    other_user_id = request.GET["user_id"]

    party = user.party
    if party is None:
        # return HttpResponse("Not in party", status=400)
        createParty(request, user)
        user.refresh_from_db()
        party = user.party

    other_user = get_object_or_404(User, id=other_user_id)

    try:
        inv = get_object_or_404(Invitation, user=other_user, party=party)
    except:
        Invitation.objects.create(user=other_user, party=party)
        other_user.set_need_reload(True)
        other_user.get_notifier().set()

    return HttpResponse("OK")


def leaveParty(request: HttpRequest, user):
    party = user.party
    if party is not None:
        user.leaveParty()
        user.save()

    user.set_need_reload(True)
    user.get_notifier().set()

    return HttpResponse("OK")


def play(request: HttpRequest, user):
    play_time = request.GET["time"]

    party = user.party
    party.isPlaying = True
    party.progress = float(play_time)
    party.lastUpdateTime = time.time()
    party.save()

    for user1 in party.get_members():
        if user1 == user:
            continue
        notifier = user1.get_notifier()
        notifier.set()

    return HttpResponse("OK")


def pause(request: HttpRequest, user):
    play_time = request.GET["time"]

    party = user.party
    party.isPlaying = False
    party.progress = float(play_time)
    party.lastUpdateTime = time.time()
    party.save()

    for user1 in party.get_members():
        if user1 == user:
            continue
        notifier = user1.get_notifier()
        notifier.set()

    return HttpResponse("OK")


def update(request: HttpRequest, user):
    user.get_notifier().set()

    return HttpResponse("OK")

def change(request: HttpRequest, user):
    anime_id = request.GET["anime"]
    ep_id = request.GET["episode"]
    print(ep_id)

    if user.party:
        party = user.party

        movie = get_object_or_404(Movie, id=anime_id)
        episode = movie.get_episode(ep_id)

        party.episode = episode
        party.isPlaying = False
        party.progress = 0
        party.save()

        us: User
        for us in party.get_members():
            us.set_need_reload(True)
            us.get_notifier().set()

        return HttpResponse("OK")
    else:
        quality = user.watching_episode.quality if user.watching_episode else None

        movie = get_object_or_404(Movie, id=anime_id)
        episode = movie.get_episode(ep_id, quality)

        user.watching_episode = episode
        user.save()

        user.set_need_reload(True)
        user.get_notifier().set()

        return HttpResponse("OK")


def listen(request: HttpRequest, user):
    notifier = user.get_notifier()

    notifier.wait(30)
    if not notifier.is_set():
        return HttpResponse("Timeout", status=504)
    notifier.clear()

    user.refresh_from_db()

    party = user.party
    sid = user.id

    resp = []

    if (party and user.watching_episode and party.episode and user.watching_episode.id != party.episode.id):
        resp.append({
            "action": "redirect",
            "url": "/watch?sid={}&anime={}&ep={}&quality={}".format(
                sid,
                party.episode.movie.id,
                party.episode.ordinal,
                party.episode.quality
            )
        })
        user.set_need_reload(False)
    elif \
        not party \
        and not (
            str(user.watching_episode.movie.id) == str(request.GET["anime"])
            and
            str(user.watching_episode.ordinal) == str(request.GET["ep"])
        ) \
    :
        print("Redirecting")
        resp.append({
            "action": "redirect",
            "url": "/watch?sid={}&anime={}&ep={}&quality={}".format(
                sid,
                user.watching_episode.movie.id,
                user.watching_episode.ordinal,
                user.watching_episode.quality
            )
        })
        user.set_need_reload(False)
    elif user.get_need_reload():
        resp.append({
            "action": "redirect",
            "url": ""
        })
        user.set_need_reload(False)
    elif party:
        resp.append({
            "action": "play" if party.isPlaying else "pause",
            "time": party.getCurrentPlayTime()
        })

    return HttpResponse(json.dumps(resp), content_type="application/json")

def party(request: HttpRequest):
    actions = {
        "create": createParty,
        "join": joinParty,
        "invite": inviteToParty,
        "leave": leaveParty,
        "play": play,
        "pause": pause,
        "listen": listen,
        "update": update,
        "change": change
    }

    action = request.GET["action"]
    print(action)

    try:
        user = pass_auth(request)
    except:
        return RedirectResponse("/api/login")

    if action not in actions:
        return HttpResponse(status=400)

    if action in ["leave", "play", "pause"] and not user.party:
        return HttpResponse("Not in party", status=400)

    return actions[action](request, user)
