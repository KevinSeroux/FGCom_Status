#!/usr/bin/env python

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fgcom_site.settings")

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.conf import settings
from status_page.utility import (extensionToPointName, extensionToFrequency,
                                 computeExtension)
from status_page.models import ActiveUser, Frequency, Point

import socket
import re
import time
import django


class AMIClient():

    def __init__(self, ip, port, username, password, buffer_size=1024):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.buffer_size = buffer_size
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.ip, self.port))

        connectQuery = ("Action: Login\r\n" +
                        "Username: " + self.username + "\r\n"
                        "Secret: " + self.password + "\r\n"
                        "\r\n")
        self.send(connectQuery)
        response = self.receive()

        if response['Response'] != 'Success':
            raise AMIClient.AccessDenied()

    def send(self, message):
        # Encode
        message = str.encode(message)
        self.socket.send(message)

    def receive(self):
        while True:
            # '\r\n\r\n' separate each messages
            index = AMIClient.data.find('\r\n\r\n')

            if index == -1:
                AMIClient.data += self.socket.recv(self.buffer_size).decode()

            else:  # If the end of the message has been found
                # We keep one '\r\n' for the parser
                trame = AMIClient.data[:index + 2]
                trameDict = dict(re.findall("(?P<name>.*?): (?P<value>.*?)\r"
                                            "\n", trame))

                # We remove the processed message
                AMIClient.data = AMIClient.data[index + 4:]
                return trameDict

    class AccessDenied(Exception):
        pass

    # Static variables
    data = ''


def newChannel(event, client, listOfOriginatedChannels):
    print()
    print('CONNECT')
    print(event)

    exten = event['Conference']
    frequency = extensionToFrequency(exten)
    point = extensionToPointName(exten)
    pk = float(event['Uniqueid'])

    ActiveUser.objects.create(pk=pk,
                              point=point,
                              frequency=frequency,
                              callsign=event['CallerIDName'],
                              version=event['CallerIDNum'])

    # CHANNEL MANAGEMENT

    # If there is already a playback (morse, atis) channel for the extension,
    # there is nothing more to do
    for channel in listOfOriginatedChannels:
        if channel.count(exten) > 0:
            return

    try:
        # If the point and the frequency are known
        frequency = Frequency.objects.get(point__name=point,
                                          frequency=frequency)
    except (ObjectDoesNotExist, MultipleObjectsReturned):
            pass

    else:
        if frequency.auto_info:
            query = ("Action: Originate\r\n"
                     "Channel: Local/" + exten + "\r\n"
                     "Context: macro-autoinfo\r\n"
                     "Exten: s\r\n"
                     "Priority: 1\r\n"
                     "Variable: MACRO_EXTEN=" + exten + "\r\n"
                     "Async: true\r\n"
                     "\r\n")
            client.send(query)

        elif frequency.nav:
            query = ("Action: Originate\r\n"
                     "Channel: Local/" + exten + "\r\n"
                     "Context: macro-morse\r\n"
                     "Exten: s\r\n"
                     "Priority: 1\r\n"
                     "Variable: CODE=" + point + "\r\n"
                     "Async: true\r\n"
                     "\r\n")
            client.send(query)


def hangup(event, client, listOfOriginatedChannels):
    print()
    print('DISCONNECT')
    print(event)

    pk = float(event['Uniqueid'])
    user = ActiveUser.objects.get(pk=pk)

    # CHANNEL MANAGEMENT
    frequency = user.frequency
    point = user.point
    exten = computeExtension(False, point, frequency)

    user.delete()

    print(exten)

    try:
        frequency = Frequency.objects.get(point__name=point,
                                          frequency=frequency)

    except (ObjectDoesNotExist, MultipleObjectsReturned):
        pass

    else:
        # We must hangup the channel only when it's an auto-info or nav freq
        if frequency.auto_info or frequency.nav:
            # And only when there is no more user on the frequency
            if not ActiveUser.objects.filter(point=point,
                                             frequency=frequency.frequency
                                             ).exists():
                i = 0
                while i < len(listOfOriginatedChannels):
                    if listOfOriginatedChannels[i].count(exten) > 0:
                        query = ("Action: Hangup\r\n"
                                 "Channel: " + listOfOriginatedChannels[i] +
                                 "\r\n\r\n")
                        client.send(query)
                        del listOfOriginatedChannels[i]
                    else:
                        i += 1


if __name__ == "__main__":
    ami = AMIClient(settings.AMI_IP, settings.AMI_PORT, settings.AMI_USER,
                    settings.AMI_PASSWORD, settings.AMI_BUFFER_SIZE)
    print('AMI: started')

    # We wait until django is set up to use the models
    print('AMI: Waiting for the models... ', end="")
    django.setup()
    print('Ready')

    # It is better to remove everything at start up to prevent residual users
    print('AMI: Flushing the table... ', end="")
    ActiveUser.objects.all().delete()
    print('Done')

    listOfOriginatedChannels = []

    while True:
        try:
            print('AMI: Connecting... ', end="")
            ami.connect()
            print('Connected')
            print('AMI: READY!')

            while True:
                data = ami.receive()
                if 'Event' in data:
                    if data['Event'] == 'ConfbridgeJoin':
                        if data['ConnectedLineNum'] != '<unknown>' or \
                           data['Channel'][0:5] == 'IAX2/':  # User
                            newChannel(data, ami, listOfOriginatedChannels)

                    elif data['Event'] == 'OriginateResponse':  # Playback
                        listOfOriginatedChannels.append(data['Channel'])

                    elif data['Event'] == 'ConfbridgeLeave':
                        if data['ConnectedLineNum'] != '<unknown>' or \
                           data['Channel'][0:5] == 'IAX2/':  # User
                            hangup(data, ami, listOfOriginatedChannels)

        except ConnectionRefusedError:
            print('AMI: Server unreachable. Retrying in ' +
                  str(settings.AMI_TIME_BEFORE_RETRY) + 's...')
            time.sleep(settings.AMI_TIME_BEFORE_RETRY)
            continue

        except AMIClient.AccessDenied:
            print('AMI: Access denied. Check username and password !')
            break

    print('AMIListener: exiting')
