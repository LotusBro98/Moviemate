import time

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.http import HttpRequest, HttpResponse
from webapp.models import Movie, Invitation, Party, User


# Create your views here.
from webapp.utils import get_client_ip, get_list, RedirectResponse, pass_auth


def watch(request: HttpRequest):
    try:
        user = pass_auth(request)
    except:
        return RedirectResponse("/api/login")

    anime_id = request.GET["anime"]
    ep_i = request.GET["ep"] if "ep" in request.GET else 1
    quality = request.GET["quality"] if "quality" in request.GET else None

    anime = get_object_or_404(Movie, id=anime_id)
    episodes = anime.get_episodes(quality)
    episodes = sorted(episodes, key=lambda ep: ep.ordinal)
    episode = anime.get_episode(ep_i, quality)

    if not ("ep" in request.GET or "quality" in request.GET):
        return RedirectResponse(
            "/watch?"
            "sid={}&"
            "anime={}&"
            "ep={}&"
            "quality={}".format(
                user.id,
                anime_id,
                ep_i,
                episode.quality
            )
        )

    print(episode)
    user.watching_episode = episode
    user.save()

    user.get_notifier().set()

    return render(request, "anime.html", {
        "anime": anime,
        "episodes": episodes,
        "episode": episode,
        "user": user,
        "party": user.party,
        "invitations": get_list(Invitation, user=user),
        "users_watching": get_list(User, watching_episode=episode),
        "parties_watching": get_list(Party, episode=episode),
    })

def login(request: HttpRequest):
    return render(request, "login.html", {
    })

def index(request: HttpRequest):
    try:
        user = pass_auth(request)
    except:
        return RedirectResponse("/api/login")

    return render(request, "index.html", {
        "anime_list": Movie.objects.all(),
        "users": User.objects.all(),
        "parties": Party.objects.all(),
        "user": user
    })