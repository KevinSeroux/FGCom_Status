# Helper functions


def extensionToPointName(exten):
    double_airport_id = exten[2:10]
    string_aiport_id = "%c%c%c%c" % (int(double_airport_id[0:2]),
                                     int(double_airport_id[2:4]),
                                     int(double_airport_id[4:6]),
                                     int(double_airport_id[6:8]))
    string_aiport_id = string_aiport_id.replace(' ', '')
    return string_aiport_id


def extensionToFrequency(exten):  # Get in KHz
    return float(exten[-6:])


def computeExtension(isRecordingFrequency, point, frequency):
    exten = ''

    if isRecordingFrequency:
        exten += '99'
    else:
        exten += '01'

    if len(point) == 3:
        point = ' ' + point

    elif len(point) == 2:
        point = '  ' + point

    elif len(point) == 1:
        point = '   ' + point

    exten += "%d%d%d%d" % (ord(point[0]), ord(point[1]),
                           ord(point[2]), ord(point[3]))
    exten += str(int(frequency))
    return exten
