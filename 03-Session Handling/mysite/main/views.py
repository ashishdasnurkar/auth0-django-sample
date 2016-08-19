from django.shortcuts import render, redirect
from mysite import settings
import requests
import json
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, "main/home.html", {"env" : settings.env})

def callback(request):
    print('callback received')
    print(request.GET.get('code'))
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

def dashboard(request):
    if request.session.get('profile'):
        return render(request, "main/dashboard.html", {"env" : settings.env})
    else:
        return redirect('/home')
    
def logout(request):
    try:
        del request.session['profile']
    except KeyError:
        pass
    return redirect('/home')
