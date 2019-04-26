import espeakng
import kiershenbaum as kiersh


class TTS:
    def __init__(self):
        self.espeakng = espeakng.ESpeakNG()
        self.espeakng.voice = "en+f4"
        self.espeakng.speed = 110
        self.espeakng.word_gap = 5
        self.espeakng.pitch = 50

    def say_ipa(self, ipa):
        kiershenbaum = self.ipa_to_kiershenbaum(ipa)
        print("{} -> {}".format(ipa, kiershenbaum))
        self.say_kiershenbaum(kiershenbaum)

    def say_text(self, text):
        self.espeakng.say(text, True)

    def say_kiershenbaum(self, kiershenbaum):
        kiershenbaum = kiershenbaum.replace("&", "a")  # "&" doesn't send nicely over command line, "a" is close enough
        self.espeakng.say(kiershenbaum, True, True)

    @staticmethod
    def ipa_to_kiershenbaum(ipa):
        return kiersh.unicode_to_ascii(ipa)
