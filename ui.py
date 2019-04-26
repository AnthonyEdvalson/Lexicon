from dictionary import Word
from language import *
from tts import TTS


lang = Language("lang1")

tts = TTS()

for word in lang.dictionary:
    try:
        letters = lang.romanization.phonemes_to_roman(word.phonemes)
        raw_letters = lang.romanization.phonemes_to_roman(word.raw_phonemes)
        print("{}\t{}\t{}".format(raw_letters, letters, ", ".join(word.definitions)))
    except:
        print("FAIL: {} {}".format(word.phonemes, word.definitions))

#lang.dictionary.add_morpheme("_", "ahtokira", ["..."])
#word = lang.dictionary.add_word("_", ["..."])
#ipa = str(word)
#tts.say_ipa(ipa)

tts = TTS()
while True:
    try:
        command = input(": ")

        words = command.split(" ")

        all_ipa = []

        for word in words:
            word = lang.dictionary.to_word(word.split("+"), [])
            all_ipa.append(word.ipa)
            print(word.phonemes)
            print(lang.romanization.phonemes_to_roman(word.phonemes))

        tts.say_ipa(" ".join(all_ipa))
    except Exception as e:
        print(e)


