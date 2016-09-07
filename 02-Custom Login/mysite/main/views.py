from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.messages import get_messages

from mysite import settings
from main.forms import LoginForm

import requests
import json

from auth0.v2.authentication import Database, Users
from auth0.v2.exceptions import Auth0Error

# Create your views here.

database = Database(settings.env["AUTH0_DOMAIN"])
users = Users(settings.env["AUTH0_DOMAIN"])

@require_http_methods(["GET"])
def home(request):
    form = LoginForm()
    storage = get_messages(request)
    login_error = None
    for message in storage:
        login_error = message
        break
    return render(request, "main/home.html", {"env" : settings.env, "form" : form, "login_error" : login_error})

@require_http_methods(["GET"])
def callback(request):
    json_header = {'content-type': 'application/json'}

    token_url = "https://{domain}/oauth/token".format(domain=settings.env["AUTH0_DOMAIN"])
    token_payload = {
        'client_id' : settings.env['AUTH0_CLIENT_ID'], \
        'client_secret' : settings.env['AUTH0_CLIENT_SECRET'], \
        'redirect_uri' : settings.env['AUTH0_CALLBACK_URL'], \
        'code' : request.GET.get('code'), \
        'grant_type': 'authorization_code' \
    }

    token_info = requests.post(token_url, data=json.dumps(token_payload), headers = json_header).json()
    user_url = "https://{domain}/userinfo?access_token={access_token}"  \
        .format(domain=settings.env["AUTH0_DOMAIN"], access_token=token_info['access_token'])
    
    user_info = requests.get(user_url).json()
    request.session['profile'] = user_info
    return redirect('/dashboard')

@require_http_methods(["GET"])
def dashboard(request):
    if request.session.get('profile'):
        return render(request, "main/dashboard.html", {"env" : settings.env})
    else:
        return redirect('/home')

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            try:
                login_result = database.login(client_id=settings.env["AUTH0_CLIENT_ID"],
                    username=form.cleaned_data['user_email'],
                    password=form.cleaned_data['user_password'],
                    connection='mlabcustomdb',
                    scope='openid profile')
            except Auth0Error as err:
                messages.add_message(request, messages.INFO, err.message)
                return redirect("/home")
            user_profile = users.tokeninfo(jwt=login_result["id_token"])
            return render(request, "main/dashboard.html", {"env" : settings.env, "user_profile" : user_profile})


