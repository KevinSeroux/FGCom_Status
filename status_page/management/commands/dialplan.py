from django.core.management.base import BaseCommand
from status_page.models import Point, Frequency
from status_page.utility import computeExtension


class Command(BaseCommand):
    help = 'Generate the dialplan fgcom.conf for asterisk'

    def handle(self, *args, **options):
        self.stdout.write(
            "[globals]\n"
            "INFO_RECORDINGS=/var/fgcom-server/atis\n"
            ";Morse tone, 1020Hz for VOR and ILS but 1350Hz for DME, in Hz\n"
            "MORSETONE=1020\n"
            ";Dit length for morse code, in ms\n"
            ";MORSEDITLEN=300\n"
            "\n"
            "[macro-com]\n"
            "exten => s,1,Answer()\n"
            "exten => s,n,ConfBridge(${MACRO_EXTEN})\n"
            "exten => s,n,Hangup()\n"
            "\n"
            "[macro-autoinfo]\n"
            "exten => s,1,Answer()\n"
            "; Check if audio file exists\n"
            "exten => s,n,TrySystem(ls ${INFO_RECORDINGS}/99${MACRO_EXTEN:2}*"
            ")\n"
            "exten => s,n,Goto(${SYSTEMSTATUS})\n"
            "; If audio file exists, play it\n"
            "exten => s,n(SUCCESS),While($[1])\n"
            "exten => s,n,Playback(${INFO_RECORDINGS}/99${MACRO_EXTEN:2})\n"
            "exten => s,n,Wait(3)\n"
            "exten => s,n,EndWhile\n"
            "exten => s,n,Hangup()\n"
            "exten => s,n,(APPERROR),Hangup()\n"
            "exten => s,n,(FAILURE),Hangup()\n"
            "\n"
            "[macro-recordinfo]\n"
            "exten => s,1,Answer()\n"
            "exten => s,n,SendText(Record begin in 3s)\n"
            "exten => s,n,Wait(1)\n"
            "exten => s,n,SendText(Record begin in 2s)\n"
            "exten => s,n,Wait(1)\n"
            "exten => s,n,SendText(Record begin in 1s)\n"
            "exten => s,n,Wait(1)\n"
            "exten => s,n,Record(${INFO_RECORDINGS}/${MACRO_EXTEN}:gsm,,90,k)"
            "\n"
            "exten => s,n,Wait(2)\n"
            "exten => s,n,Playback(${INFO_RECORDINGS}/${MACRO_EXTEN})\n"
            "exten => s,n,Hangup()\n"
            "\n"
            "[macro-morse]\n"
            "exten => s,1,Answer()\n"
            "exten => s,n,While($[1])\n"
            "exten => s,n,Morsecode(${CODE})\n"
            "exten => s,n,Wait(2)\n"
            "exten => s,n,EndWhile\n"
            "exten => s,n,Hangup()\n"
            "\n"
            "[fgcom]\n"
            "; 910.000     Echo-Box\n"
            "exten => 0190909090910000,1,SendText(Echo Box - For testing FGCO"
            "M)\n"
            "exten => 0190909090910000,n,Answer()\n"
            "exten => 0190909090910000,n,Echo()\n"
            "exten => 0190909090910000,n,Hangup()\n"
            "\n"
            "; All the frequencies\n"
            "exten => _01XXXXXXXXZXXXXZ,1,Dial(Local/${EXTEN:0:15}0)\n"
            "exten => _01XXXXXXXXXXXXXX,1,Macro(com)\n"
            "\n"
            "exten => _99XXXXXXXXZXXXXZ,1,Dial(Local/${EXTEN:0:15}0)\n"
            "\n")

        frequencies = Frequency.objects.filter(auto_info=True)
        for frequency in frequencies:
            point_name = frequency.point.name
            exten = computeExtension(True, point_name, frequency.frequency)
            self.stdout.write("; " + point_name + ' ' + frequency.description)
            self.stdout.write("exten => " + str(exten) +
                              ",1,Macro(recordinfo)")
