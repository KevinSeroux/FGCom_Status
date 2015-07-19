#!/usr/bin/env python

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fgcom_site.settings")

from django.conf import settings
from status_page.utility import phoneNumberToAirport, phoneNumberToFrequency
from status_page.models import ActiveUser

import socket
import re
import time
import django


class BadServerResponse(Exception):
    pass


class AccessDenied(Exception):
    pass


rawdata = b''


def getMessage():
    # The purpose of this static variable is to keep datas between each
    # executions of this method
    global rawdata

    while True:
        # '\r\n\r\n' separate each messages
        index = rawdata.find(b'\r\n\r\n')

        if index == -1:
            rawdata += s.recv(settings.AMI_BUFFER_SIZE)

        else:  # If the end of the message has been found
            # We keep one '\r\n' for the parser
            trame = rawdata[:index + 2]
            trameDict = dict(re.findall(b"(?P<name>.*?): (?P<value>.*?)\r"
                                        b"\n", trame))

            # We remove the processed message
            rawdata = rawdata[index + 4:]
            return trameDict


def newChannel(event):
    print('New channel')
    print(event)
    print()

    frequency = phoneNumberToFrequency(event[b'Exten'])
    point = phoneNumberToAirport(event[b'Exten'])
    pk = float(event[b'Uniqueid'])

    ActiveUser.objects.create(pk=pk,
                              point=point,
                              frequency=frequency,
                              callsign=event[b'CallerIDName'],
                              version=event[b'CallerIDNum'])


def hangup(event):
    print('Hangup')
    print(event)
    print()

    pk = float(event[b'Uniqueid'])
    ActiveUser.objects.filter(pk=pk).delete()


if __name__ == "__main__":
    print('AMI Listener: started')

    # We wait until django is set up to use the models
    django.setup()

    # It is better to remove everything at start up to prevent residual users
    ActiveUser.objects.all().delete()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        try:
            s.connect((settings.AMI_IP, settings.AMI_PORT))
            server_version = s.recv(settings.AMI_BUFFER_SIZE)
            if server_version[-2:] == b'\r\n':
                query = b"Action: Login\r\n"
                query += b"Username: " + settings.AMI_USER + b"\r\n"
                query += b"Secret: " + settings.AMI_PASSWORD + b"\r\n"
                query += b"\r\n"
                s.send(query)

                response = getMessage()
                if response[b'Response'] == b'Success':
                    while True:
                        data = getMessage()
                        if b'Event' in data:
                            if data[b'Event'] == b'Newchannel':
                                # To register just one time the user
                                if data[b'Channel'][:5] == b'IAX2/':
                                    newChannel(data)

                            elif data[b'Event'] == b'Hangup':
                                # To register just one time the user
                                if data[b'Channel'][:5] == b'IAX2/':
                                    hangup(data)

                else:  # Bad username/password
                    raise AccessDenied()

            else:  # Server not reachable
                raise BadServerResponse()

        except ConnectionRefusedError:
            print('AMIListener: Server unreachable. Retrying in ' +
                  str(settings.AMI_TIME_BEFORE_RETRY) + 's...')
            time.sleep(settings.AMI_TIME_BEFORE_RETRY)
            continue

        except BadServerResponse:
            print('AMIListener: Server has not answered as expected!')
            break

        except AccessDenied:
            print('AMIListener: Access denied. Check username and '
                  'password !')
            break

    print('AMIListener: exiting')
