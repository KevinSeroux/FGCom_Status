# Helper functions


def phoneNumberToAirport(phonenumber):
    double_airport_id = phonenumber[2:10]
    string_aiport_id = "%c%c%c%c" % (int(double_airport_id[0:2]),
                                     int(double_airport_id[2:4]),
                                     int(double_airport_id[4:6]),
                                     int(double_airport_id[6:8]))
    return string_aiport_id


def phoneNumberToFrequency(phonenumber):
    return float(phonenumber[-6:]) / 1000
