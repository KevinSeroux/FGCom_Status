from django.core.management.base import BaseCommand
from django.db import transaction
from status_page.models import Point, Frequency

import gzip


class Command(BaseCommand):
    help = 'Install airports, ndb and frequencies in the database'

    @transaction.atomic  # Batching for database
    def handle(self, *args, **options):
        apt_data_location = input('Location of apt.dat.gz: ')
        apt_data = gzip.open(apt_data_location)

        current_line_number = 0
        lines_count = self.getCountLines(apt_data)

        last_icao_code = ''
        last_latitudes = []
        last_longitudes = []

        # Replace the cursor at the begining after first read (line counts)
        apt_data.seek(0)
        for raw_line in apt_data:
            current_line_number += 1

            progress = int(current_line_number / lines_count * 100)
            self.stdout.write('\r-> Progress: ' + str(progress) +
                              '%', ending='')

            line = raw_line.decode(encoding='Windows-1252')

            words = line.split()

            if len(words) > 0:  # lines can be empty
                # Airport
                if words[0] == '1' or words[0] == '16' or words[0] == '17':
                    if last_icao_code != '':
                        self.updatePoint(last_icao_code,
                                         last_latitudes,
                                         last_longitudes)

                    last_icao_code = str(words[4])
                    last_latitudes = []
                    last_longitudes = []

                    self.savePoint(last_icao_code,
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

                # Frequency
                elif (words[0] == '50' or words[0] == '51' or
                      words[0] == '52' or words[0] == '53' or
                      words[0] == '53' or words[0] == '54' or
                      words[0] == '55' or words[0] == '56'):

                    frequency = float(words[1]) / 100
                    description = str.join(' ', words[2:])

                    self.saveFrequency(last_icao_code, frequency, description)

        # We don't forget the last point
        self.updatePoint(last_icao_code,
                         last_latitudes,
                         last_longitudes)
        apt_data.close()

    def savePoint(self, icao_code, latitudes, longitudes):
        # If the file is not well formated, it is possible that a
        # ZeroDivisionError exception is thrown
        try:
            latitude = sum(latitudes) / len(latitudes)
            longitude = sum(longitudes) / len(longitudes)

        except ZeroDivisionError:
            point = Point(pk=icao_code)
            point.save()

        else:
            point = Point(pk=icao_code,
                          longitude=longitude,
                          latitude=latitude)
            point.save()

    def updatePoint(self, icao_code, latitudes, longitudes):
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
            Point.objects.filter(pk=icao_code).update(latitude=latitude,
                                                      longitude=longitude)

    def saveFrequency(self, icao_code, frequency, description):
        instance = Point.objects.get(pk=icao_code)

        # Same frequency for same airport can happen
        sameFreqsPoints = Frequency.objects.filter(point=instance,
                                                   frequency=frequency)
        if sameFreqsPoints:
            # In this case, concatenate descriptions
            sameFreqPoint = sameFreqsPoints.first()
            sameFreqsPoints.update(description=sameFreqPoint.description +
                                   ' / ' + description)

        else:
            frequency = Frequency(point=instance,
                                  frequency=frequency,
                                  description=description)
            frequency.save()

    def getCountLines(self, file):
        countLines = 0
        for line in file:
            countLines += 1
        return countLines
