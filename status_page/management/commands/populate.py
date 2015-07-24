from django.core.management.base import BaseCommand
from django.db import transaction
from status_page.models import Point, Frequency

import gzip


class Command(BaseCommand):
    help = 'Install airports, ndb and frequencies in the database'

    @transaction.atomic  # Batching for database
    def handle(self, *args, **options):
        apt_data_location = input('Location of apt.dat.gz: ')
        apt_data_lines_count = self.getCountLines(apt_data_location)
        nav_data_location = input('Location of nav.dat.gz: ')
        nav_data_lines_count = self.getCountLines(nav_data_location)

        self.handleApt(apt_data_location, apt_data_lines_count)
        self.handleNav(nav_data_location, nav_data_lines_count)

    def handleApt(self, apt_data_location, lines_count):
        apt_data = gzip.open(apt_data_location)

        current_line_number = 0

        last_point = None
        last_latitudes = []
        last_longitudes = []

        for raw_line in apt_data:
            current_line_number += 1

            progress = int(current_line_number / lines_count * 50)
            self.stdout.write('\r-> [1/2] Progress: ' + str(progress) +
                              '%', ending='')

            line = raw_line.decode(encoding='Windows-1252')

            words = line.split()

            if len(words) > 0:  # lines can be empty
                try:
                    # Airport
                    if words[0] == '1' or words[0] == '16' or words[0] == '17':
                        if last_point is not None:
                            self.updatePoint(last_point,
                                             last_latitudes,
                                             last_longitudes)

                        icao_code = str(words[4])
                        last_latitudes = []
                        last_longitudes = []

                        last_point = self.savePoint(icao_code,
                                                    last_latitudes,
                                                    last_longitudes)

                    # Runway
                    elif words[0] == '100':
                        last_latitudes.append(float(words[9]))
                        last_longitudes.append(float(words[10]))
                        last_latitudes.append(float(words[18]))
                        last_longitudes.append(float(words[19]))

                    # Water runway
                    elif words[0] == '101':
                        last_latitudes.append(float(words[4]))
                        last_longitudes.append(float(words[5]))
                        last_latitudes.append(float(words[7]))
                        last_longitudes.append(float(words[8]))

                    # Helipad
                    elif words[0] == '102':
                        last_latitudes.append(float(words[2]))
                        last_longitudes.append(float(words[3]))

                    # Other frequencies
                    elif (words[0] == '50' or words[0] == '51' or
                          words[0] == '52' or words[0] == '53' or
                          words[0] == '53' or words[0] == '54' or
                          words[0] == '55' or words[0] == '56'):

                        auto_info = False
                        if words[0] == '50':  # ATIS, AWOS, ASOS frequencies
                            auto_info = True

                        frequency = float(words[1]) * 10  # In KHz
                        description = str.join(' ', words[2:])

                        self.saveFrequency(last_point, frequency, auto_info,
                                           False, description)

                except IndexError:
                    self.stdout.write('\n--> Line ' + str(current_line_number)
                                      + ' bad formatted:\n--> ' + line)

        # We don't forget the last point
        self.updatePoint(last_point,
                         last_latitudes,
                         last_longitudes)
        apt_data.close()

    def handleNav(self, nav_data_location, lines_count):
        nav_data = gzip.open(nav_data_location)

        current_line_number = 0

        for raw_line in nav_data:
            current_line_number += 1

            progress = int(current_line_number / lines_count * 50 + 50)
            self.stdout.write('\r-> [2/2] Progress: ' + str(progress) +
                              '%', ending='')

            line = raw_line.decode(encoding='Windows-1252')

            words = line.split()

            if len(words) > 0:  # lines can be empty
                try:
                    if (words[0] == '2' or words[0] == '3' or
                        words[0] == '4' or words[0] == '5' or
                        words[0] == '6' or words[0] == '12' or
                        words[0] == '13'):

                        latitude = float(words[1])
                        longitude = float(words[2])
                        frequency = float(words[4])

                        if words[0] != '2':  # Only NDB is in KHz
                            frequency *= 10

                        identifier = None
                        description = None

                        if (words[0] == '2' or words[0] == '3'):  # NDB, VOR
                            identifier = words[7]

                            # We don't use words[8:] to trigger an IndexError
                            description = words[8]
                            description += ' ' + str.join(' ', words[9:])

                        elif (words[0] == '4' or words[0] == '5' or
                              words[0] == '6'):  # LOC, GS
                            # Identifier is the airport ICAO code
                            identifier = words[8]

                            # Description = code + runway + ILS type
                            # We don't use words[10:] to trigger an IndexError
                            description = (words[7] + ' ' + words[9] + ' ' +
                                           words[10])
                            description += ' ' + str.join(' ', words[11:])

                        else:  # DME
                            if words[6] != '0.0':
                                # Identifier is the airport ICAO code
                                identifier = words[8]

                                # Description = code + runway + ILS type
                                description = (words[7] + ' ' + words[9] + ' '
                                               + str.join(' ', words[10:]))

                            else:
                                identifier = words[7]
                                description = str.join(' ', words[8:])

                        point = self.savePoint(identifier, [latitude],
                                               [longitude])
                        self.saveFrequency(point, frequency, False, True,
                                           description)

                # This can occur if the line is not well formated
                except IndexError:
                    self.stdout.write('\n--> Line ' + str(current_line_number)
                                      + ' bad formatted:\n--> ' + line)

        nav_data.close()

    def savePoint(self, name, latitudes, longitudes):

        latitude = None
        longitude = None

        # If the file is not well formated, it is possible that a
        # ZeroDivisionError exception is thrown
        try:
            latitude = sum(latitudes) / len(latitudes)
            longitude = sum(longitudes) / len(longitudes)

        except ZeroDivisionError:
            pass

        point = Point.objects.filter(name=name, latitude=latitude,
                                     longitude=longitude)
        if not point:
            point = Point(name=name, longitude=longitude, latitude=latitude)
            point.save()
            return point
        else:
            return point[0]

    def updatePoint(self, point, latitudes, longitudes):
        latitude = 0
        longitude = 0

        # If the file is not well formated, it is possible that a
        # ZeroDivisionError exception is thrown
        try:
            latitude = sum(latitudes) / len(latitudes)
            longitude = sum(longitudes) / len(longitudes)

        except ZeroDivisionError:
            pass

        else:
            point.latitude = latitude
            point.longitude = longitude
            point.save()

    def saveFrequency(self, point, frequency, auto_info, nav, description):
        # Same frequency for same airport can happen
        sameFreqsPoints = Frequency.objects.filter(point=point,
                                                   frequency=frequency)
        if sameFreqsPoints:
            # In this case, concatenate descriptions
            sameFreqPoint = sameFreqsPoints.first()

            # Case insensitive research
            if 'ILS' in sameFreqPoint.description.upper():
                # No need to add a GS and LOC frequency for an ILS system
                return

            if sameFreqPoint.auto_info:
                auto_info = True

            if sameFreqPoint.nav:
                nav = True

            description = sameFreqPoint.description + ' / ' + description

            sameFreqsPoints.update(description=description,
                                   auto_info=auto_info, nav=nav)

        else:
            frequency = Frequency(point=point,
                                  frequency=frequency,
                                  description=description,
                                  auto_info=auto_info,
                                  nav=nav)
            frequency.save()

    def getCountLines(self, file_location):
        file = gzip.open(file_location)

        countLines = 0
        for line in file:
            countLines += 1

        file.close()

        return countLines
