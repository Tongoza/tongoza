from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseBadRequest
from tongoza.settings import BASE_DIR


import os
import json

# Create your views here.

ROBOTS_PATH = os.path.join(BASE_DIR, 'marketing/robots.txt')


def robots(request):
    return HttpResponse(open(ROBOTS_PATH).read(), 'text/plain')
