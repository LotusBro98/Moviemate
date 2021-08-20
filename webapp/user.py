import requests
from django.db import models
from threading import Event

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from webapp.models import User
from webapp.utils import get_client_ip, RedirectResponse, get_list
import vk_api

APP_ID = 7401654
CLIENT_SECRET = "y2GTAjnaW1XFcPQM4c47"
ACCESS_TOKEN = "5202ec755202ec755202ec759752721cc3552025202ec750c8d785e31e89a769d272e00"
DOMAIN = "moviemate.ru"

def start_vk_server_session():
    vk_session = vk_api.VkApi(app_id=APP_ID, client_secret=CLIENT_SECRET, token=ACCESS_TOKEN)
    vk_session.server_auth()
    vk_session.token = {'access_token': ACCESS_TOKEN, 'expires_in': 0}
    vk = vk_session.get_api()
    return vk

def start_vk_session(token):
    vk_session = vk_api.VkApi(app_id=APP_ID, token=token)
    # vk_session.auth(token_only=True)
    vk_session.token = {'access_token': token, 'expires_in': 0}
    vk = vk_session.get_api()
    return vk

def get_vk_name(user, vk):
    if user.vk is None:
        return None

    resp = vk.users.get(user_ids=user.vk, fields="screen_name")

    if len(resp) != 1:
        return None
    resp = resp[0]

    vk_id = resp["id"]
    vk_screen_name = resp["screen_name"]

    return vk_screen_name


def api_login(request: HttpRequest):
    if request.method != "GET":
        return JsonResponse({"error": "Wrong method"}, status=405)

    ip = get_client_ip(request)

    if "vk" in request.GET and request.GET["vk"] == "1":
        url = "https://oauth.vk.com/authorize?"\
              "client_id={}&"\
              "display=page&"\
              "redirect_uri=http://{}/api/login_callback&"\
              "scope=friends&"\
              "response_type=code&"\
              "v=5.103".format(APP_ID, DOMAIN)

        return RedirectResponse(url)

    # as guest or restore session from ip
    try:
        user = get_object_or_404(User, login_ip=ip)
    except:
        user = User.new_user(ip)

    return RedirectResponse("/?sid={}".format(user.id))

def api_login_callback(request: HttpRequest):
    if "error" in request.GET:
        return RedirectResponse("/login")

    code = request.GET["code"]

    resp = requests.get(url="https://oauth.vk.com/access_token", params={
        "client_id": APP_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": "http://{}/api/login_callback".format(DOMAIN),
        "code": code
    }).json()

    if "error" in resp:
        return RedirectResponse("/login")

    ip = get_client_ip(request)
    vk_id = resp["user_id"]
    vk_token = resp["access_token"]
    vk = start_vk_session(vk_token)

    try:
        user = get_object_or_404(User, vk=vk_id)
        user.login_ip = ip
        user.save()
    except:
        user = User.new_user(ip)
        user.vk = vk_id
        if user.nickname is None:
            user.nickname = get_vk_name(user, vk)
        user.save()

    for us in get_list(User, login_ip=ip):
        if us == user:
            continue
        us.delete()

    return RedirectResponse("/?sid={}".format(user.id))
