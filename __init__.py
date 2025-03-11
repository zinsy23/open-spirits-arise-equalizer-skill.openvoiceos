import os
from difflib import SequenceMatcher

from ovos_bus_client.message import Message
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill


def parse_intents(command):
    command = command.replace(" add ", " and ")
    command = command.replace(" air ", " and ")
    command = command.replace(" had ", " and ")
    command = command.replace(" at ", " and ")
    command = command.replace(" an ", " and ")
    command = command.replace(" on ", " and ")
    command = command.replace(" are ", " and ")
    command = command.replace(" a ", " and ")
    command = command.replace(" in ", " and ")
    return [intent.strip() for intent in command.split("and")]


def checkSleep(command):
    return " sleep" in command or "lay " in command or " down" in command or "light " in command or " out" in command


def loadQuantifiers(qPath):
    quantifiers = {}

    quantifiersFile = open(qPath, "r").read().split("\n")

    for i in range(len(quantifiersFile) - 1):
        quantifierItem = quantifiersFile[i].split(",")
        quantifiers[quantifierItem[0]] = int(quantifierItem[1])

    return quantifiers


def loadDictionary(qPath):
    quantifiers = {}

    quantifiersFile = open(qPath, "r").read().split("\n")

    for i in range(len(quantifiersFile) - 1):
        quantifierItem = quantifiersFile[i].split(",")
        quantifiers[quantifierItem[0]] = quantifierItem[1]

    return quantifiers


def hasQuantifier(utteranceCheck, quantifiers):
    for i in quantifiers.keys():
        if i in utteranceCheck:
            utteranceCheck = utteranceCheck.replace(i, "").replace("  ", " ").strip()
            return quantifiers[i], utteranceCheck
    return 1, utteranceCheck


def replaceBackslashes(file):
    for i in range(len(file) - 1):
        file[i] = file[i].split(",")
        file[i][1] = file[i][1].replace("\\", "\\\\\\\\")
        if not (file[i][1].find(":") == -1):
            file[i][1] = file[i][1].replace(" ", "\ ")
            colon_index = file[i][1].rfind(":")
            first_colon_index = file[i][1].find(":")
            last_space_index = file[i][1][: colon_index + 1].rfind(" ") - 1
            if not (colon_index == first_colon_index):
                file[i][1] = file[i][1][:last_space_index] + file[i][1][last_space_index + 1 :]
        file[i][1] = file[i][1].replace("(", "\(").replace(")", "\)")
        file[i] = ",".join(file[i])
    return file


class OpenSpiritsAriseEqualizer(OVOSSkill):
    def __init__(self, *args, bus=None, skill_id="", **kwargs):
        OVOSSkill.__init__(self, *args, bus=bus, skill_id=skill_id, **kwargs)
        self.commands = []
        self.locations = []
        self.devices = []

    def initialize(self):
        my_setting = self.settings.get("my_setting")

    @intent_handler("equalizer.arise.spirits.open.intent")
    def handle_equalizer_arise_spirits_open(self, message):
        routeCommands = loadDictionary("command_functions.txt")
        commandTranslations = loadDictionary("computer_systems.txt")
        openDevices = loadDictionary("open_devices.txt")

        file = open(openDevices[routeCommands["open"]], "r").read().split("\n")
        # addresses = open("/home/pi/Documents/mycroft/ip_address", "r").read().split("\n")
        addresses = ["joseph@192.168.2.10", "zinsy23@192.168.2.12"]  # placeholder for real file in above line
        quantifiers = loadQuantifiers("quantifiers.txt")

        file = replaceBackslashes(file)

        for i in range(len(file) - 2):
            line = file[i].split(",")
            self.commands.append(line[0])
            self.locations.append(line[1])
            if len(line) == 3:
                self.devices.append(line[2])
            else:
                self.devices.append(False)

        # os.system(f'echo {file[len(file) - 7]}')

        self.speak_dialog("equalizer.arise.spirits.open")

        result = message.data.get("utterance")
        result = result[result.find(" ") + 1 : len(result)]
        results = parse_intents(result)

        for i in range(len(results)):
            quantifier, results[i] = hasQuantifier(results[i], quantifiers)

            for j in range(quantifier):
                matcher = SequenceMatcher(a=results[i])  # get the variable name
                match = max(self.commands, key=lambda x: matcher.set_seq2(" ".join(x)) or matcher.ratio())
                index = self.commands.index(match)

                if not (checkSleep(results[i])):
                    if commandTranslations[routeCommands["open"]].lower() == "windows":
                        os.system(
                            rf'''ssh -n -p 2022 {addresses[0]} "/mnt/c/Windows/System32/cmd.exe /C {self.locations[index]}"'''
                        )
                    elif commandTranslations[routeCommands["open"]].lower() == "mac":
                        os.system(rf'''ssh -n {addresses[1]} """{self.locations[index]}"""''')
                else:
                    self.bus.emit(Message("recognizer_loop:utterance", {"utterances": ["lay down"], "lang": "en-us"}))

    def stop(self) -> bool:
        return False
