from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from status_page.models import ActiveUser
from status_page.utility import phoneNumberToAirport, phoneNumberToFrequency
import json
import os
import glob
import datetime


# Create your views here.
def index(request):
    return render(request, template_name='index.html')


def users(request):
    data = json.dumps([
        dict(item) for item in ActiveUser.objects.all().values(
            'airport', 'frequency', 'callsign', 'version')])

    return HttpResponse(data, content_type="application/json")


def atis(request):
    myList = []

    os.chdir(settings.ATIS_DIR)
    for file in glob.glob("*.gsm"):
        phoneNumber = file[:-4]  # To remove .gsm extension

        airport = phoneNumberToAirport(phoneNumber)
        frequency = phoneNumberToFrequency(phoneNumber)
        timestamp = os.path.getmtime(settings.ATIS_DIR + '/' + file)
        universal_time = datetime.datetime.utcfromtimestamp(timestamp)

        myDict = {'airport': airport,
                  'frequency': frequency,
                  'date': universal_time.strftime("%a, %d %b %Y %H:%M")}

        myList.append(myDict)

    return HttpResponse(json.dumps(myList), content_type="application/json")
