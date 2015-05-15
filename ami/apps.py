from django.apps import AppConfig, apps
from django.conf import settings
from multiprocessing import Process
from status_page.utility import phoneNumberToAirport, phoneNumberToFrequency
import socket
import re
import time


class BadServerResponse(Exception):
    pass


class AccessDenied(Exception):
    pass


class AMIConfig(AppConfig):
    name = 'ami'
    verbose_name = "Asterisk Manager Interface"

    def ready(self):
        listener = AMIListener()
        listener.start()


# The model must be passed here
class AMIListener(Process):
    daemon = True
    BUFFER_SIZE = 1024
    data = b''

    def run(self):
        print('AMI Listener: started')
        self.ActiveUser = apps.get_model(app_label='status_page',
                                         model_name='ActiveUser')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                self.s.connect((settings.AMI_IP, settings.AMI_PORT))
                server_version = self.s.recv(AMIListener.BUFFER_SIZE)
                if server_version[-2:] == b'\r\n':
                    query = b"Action: Login\r\n"
                    query += b"Username: " + settings.AMI_USER + b"\r\n"
                    query += b"Secret: " + settings.AMI_PASSWORD + b"\r\n"
                    query += b"\r\n"
                    self.s.send(query)

                    response = self.getMessage()
                    if response[b'Response'] == b'Success':
                        while True:
                            data = self.getMessage()
                            if b'Event' in data:
                                if data[b'Event'] == b'Newchannel':
                                    self.newChannel(data)

                                elif data[b'Event'] == b'Hangup':
                                    self.hangup(data)

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

    def getMessage(self):
        while True:
            # '\r\n\r\n' separate each messages
            index = AMIListener.data.find(b'\r\n\r\n')

            if index == -1:
                # The purpose of this static variable is to keep datas between
                # each executions od this method
                AMIListener.data += self.s.recv(AMIListener.BUFFER_SIZE)

            else:  # If the end of the message has been found
                # We keep one '\r\n' for the parser
                trame = AMIListener.data[:index + 2]
                trameDict = dict(re.findall(b"(?P<name>.*?): (?P<value>.*?)\r"
                                            b"\n", trame))

                # We remove the processed message
                AMIListener.data = AMIListener.data[index + 4:]
                return trameDict

    def newChannel(self, event):
        print('New channel')
        print(event)
        print()

        frequency = phoneNumberToFrequency(event[b'Exten'])
        airport = phoneNumberToAirport(event[b'Exten'])
        pk = float(event[b'Uniqueid'])

        self.ActiveUser.objects.create(pk=pk,
                                       airport=airport,
                                       frequency=frequency,
                                       callsign=event[b'CallerIDName'],
                                       version=event[b'CallerIDNum'])

    def hangup(self, event):
        print('Hangup')
        print(event)
        print()

        pk = float(event[b'Uniqueid'])
        self.ActiveUser.objects.filter(pk=pk).delete()
