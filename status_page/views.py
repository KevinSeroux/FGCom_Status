from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from status_page.models import ActiveUser, Point, Frequency
from status_page.utility import extensionToPointName, extensionToFrequency
import json
import os
import glob
import datetime


# Create your views here.
def index(request):
    return render(request, template_name='index.html')


def users(request):
    myList = [
        dict(item) for item in ActiveUser.objects.all().values(
            'point', 'frequency', 'callsign', 'version')]

    for user in myList:
        try:
            frequency = Frequency.objects.get(point__name=user['point'],
                                              frequency=user['frequency'])
            user['latitude'] = frequency.point.latitude
            user['longitude'] = frequency.point.longitude
            user['description'] = frequency.description

        except Frequency.DoesNotExist:
            pass

        else:
            if user['frequency'] % 1000 > 0:
                user['frequency'] = str(user['frequency'] / 1000) + ' MHz'
            else:
                user['frequency'] = str(user['frequency']) + ' KHz'

    data = json.dumps(myList)

    return HttpResponse(data, content_type="application/json")


def auto_info(request):
    myList = []

    os.chdir(settings.ATIS_DIR)
    for file in glob.glob("*.gsm"):
        exten = file[:-4]  # To remove .gsm extension

        airport = extensionToPointName(exten)
        frequency = extensionToFrequency(exten) / 1000
        timestamp = os.path.getmtime(settings.ATIS_DIR + '/' + file)
        universal_time = datetime.datetime.utcfromtimestamp(timestamp)

        myDict = {'airport': airport,
                  'frequency': frequency,
                  'date': universal_time.strftime("%a, %d %b %Y %H:%M")}

        myList.append(myDict)

    return HttpResponse(json.dumps(myList), content_type="application/json")
