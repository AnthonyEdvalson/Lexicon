import csv
from abc import ABC, abstractmethod
from enum import Enum
from typing import List


class POA(Enum):
    bilabial = 0
    labiodental = 1
    dental = 2
    alveolar = 3
    postalveolar = 4
    retroflex = 5
    palatal = 6
    velar = 7
    uvular = 8
    pharyngeal = 9
    glottal = 10


class MOA(Enum):
    plosive = 0
    nasal = 1
    trill = 2
    tap = 3
    fricative = 4
    lateral_fricative = 5
    approximate = 6
    lateral_approximant = 7

    click = 8
    implosive = 9
    ejective = 10
    affricate = 11


class Height(Enum):
    close = 0
    near_close = 1
    close_mid = 2
    mid = 3
    open_mid = 4
    near_open = 5
    open = 6


class Frontness(Enum):
    front = 0
    central = 1
    back = 2


class Rounding(Enum):
    unrounded = 0
    rounded = 1


class Voicing(Enum):
    unvoiced = 0
    voiced = 1


class Length(Enum):
    normal = 0
    long = 1

class Stress(Enum):
    unstressed = 0
    secondary_stressed = 1
    stressed = 2


class Phoneme(ABC):
    def __init__(self, length, stress):
        self.length = enum_clean(Length, length)
        self.stress = enum_clean(Stress, stress)

    @abstractmethod
    def as_dict(self):
        pass

    @property
    def props(self):
        return Ipa.phoneme_to_ipa(self)

    def has_prop(self, key):
        if key == self.stress.name:
            return True
        if key == self.length.name:
            return True

        return False

    @property
    def ipa(self):
        return Ipa.phoneme_to_ipa(self)

    @property
    def base_ipa(self):
        return Ipa.phoneme_to_base_ipa(self)

    def __str__(self):
        return self.ipa

    def __repr__(self):
        attrs = ", ".join(map(lambda e: e.name, self.as_dict().values()))
        return "{}<{}>".format(self.ipa, attrs)

    @abstractmethod
    def copy(self):
        pass


class Phonemes:
    def __init__(self, phonemes: List[Phoneme]=None):
        if phonemes is not None:
            self.phonemes = phonemes
        else:
            self.phonemes = []

    @property
    def ipa(self):
        return Ipa.phonemes_to_ipa(self)

    def __repr__(self):
        items = ", ".join(map(repr, self.phonemes))
        return "[{}]".format(items)

    def __str__(self):
        return self.ipa

    def __add__(self, other):
        a = self.phonemes.copy()
        b = other.phonemes.copy()
        a.extend(b)
        return Phonemes(a)

    def __bool__(self):
        return len(self.phonemes) > 0

    def __contains__(self, item):
        for phoneme in self.phonemes:
            if phoneme == item:
                return True

        return False

    def copy(self):
        return Phonemes([p.copy() for p in self.phonemes])

    def __delitem__(self, key):
        del self.phonemes[key]

    def __eq__(self, other):
        if len(self) != len(other):
            return False

        for i in range(0, len(self)):
            if self[i] != other[i]:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, item):
        return self.phonemes[item]

    def __hash__(self):
        return hash(self.ipa)

    def __iter__(self):
        return iter(self.phonemes)

    def __len__(self):
        return len(self.phonemes)

    def __setitem__(self, key, value):
        self.phonemes[key] = value

    def __lt__(self, other):
        return self._compare(other) < 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def _compare(self, other):
        if isinstance(other, Phonemes):
            for p1, p2 in zip(self.phonemes, other.phonemes):
                ipa1 = p1.ipa
                ipa2 = p2.ipa

                if not ipa1 or not ipa2:
                    raise Exception("Unknown ipa for {} / {}".format(p1, p2))

                if ipa1 < ipa2:
                    return -1
                elif ipa1 > ipa2:
                    return 1

            l1 = len(self.phonemes)
            l2 = len(other.phonemes)

            if l1 < l2:
                return -1
            elif l1 > l2:
                return 1

            return 0

        raise TypeError("Cannot compare {} with Phonemes".format(type(other)))


def enum_clean(enum, value):
    if isinstance(value, enum):
        return value

    if isinstance(value, str):
        return enum[value]

    if isinstance(value, int):
        return enum(value)

    if isinstance(value, bool):
        return enum(1 if value else 0)

    raise TypeError("Cannot convert {} of type {} to {}".format(value, type(value), enum))


class Vowel(Phoneme):
    def __init__(self, length, stress, height, frontness, rounding):
        super().__init__(length, stress)
        self.height = enum_clean(Height, height)
        self.frontness = enum_clean(Frontness, frontness)
        self.rounding = enum_clean(Rounding, rounding)

    def has_prop(self, key):
        if super().has_prop(key):
            return True
        if key == "vowel":
            return True
        if key == "consonant":
            return False
        if key == self.height.name:
            return True
        if key == self.frontness.name:
            return True
        if key == self.rounding.name:
            return True

        return False

    def as_dict(self):
        return {
            "height": self.height,
            "frontness": self.frontness,
            "rounding": self.rounding,
            "length": self.length,
            "stress": self.stress
        }

    def __eq__(self, other):
        if isinstance(other, Vowel):
            return self.height == other.height and \
                   self.frontness == other.frontness and \
                   self.rounding == other.rounding and \
                   self.length == other.length

    def copy(self):
        return Vowel(**self.as_dict())


class Consonant(Phoneme):
    def __init__(self, length, stress, manner, place, voicing):
        super().__init__(length, stress)
        self.place = enum_clean(POA, place)
        self.manner = enum_clean(MOA, manner)
        self.voicing = enum_clean(Voicing, voicing)

    def has_prop(self, key):
        if super().has_prop(key):
            return True
        if key == "vowel":
            return False
        if key == "consonant":
            return True
        if key == self.place.name:
            return True
        if key == self.manner.name:
            return True
        if key == self.voicing.name:
            return True
        if key == "obstruent":
            return self.manner in {MOA.plosive, MOA.fricative, MOA.affricate}
        if key == "sibilant":
            return self.manner == MOA.fricative and self.place in {POA.alveolar, POA.postalveolar, POA.retroflex}
        if key == "sonorant":
            return self.manner in {MOA.approximate, MOA.nasal, MOA.tap, MOA.trill}
        if key == "vibrant":
            return self.manner in {MOA.tap, MOA.trill}
        if key == "lateral":
            return self.manner in {MOA.lateral_approximant, MOA.lateral_fricative}
        if key == "occlusive":
            return self.manner in {MOA.plosive, MOA.nasal, MOA.affricate, MOA.implosive, MOA.ejective, MOA.click}

        return False

    def as_dict(self):
        return {
            "place": self.place,
            "manner": self.manner,
            "voicing": self.voicing,
            "length": self.length,
            "stress": self.stress
        }

    def __eq__(self, other):
        if isinstance(other, Consonant):
            return self.place == other.place and \
                   self.manner == other.manner and \
                   self.voicing == other.voicing

    def copy(self):
        return Consonant(**self.as_dict())


class IPA:
    def __init__(self):
        self._vowel_data = {}
        self._consonant_data = {}
        self._ipa_phoneme_data = {}
        self._load_vowels()
        self._load_consonants()
        print()

    def _load_vowels(self):
        rows = list(csv.reader(open('vowels.txt', 'r', encoding="utf-8"), delimiter='\t'))
        for y in range(1, 8):
            height = Height(y - 1)
            self._vowel_data[height] = {}

            for x in range(1, 7):
                char = rows[y][x]

                frontness = Frontness((x - 1) // 2)
                rounding = Rounding((x - 1) % 2)

                if frontness not in self._vowel_data[height]:
                    self._vowel_data[height][frontness] = {}

                self._vowel_data[height][frontness][rounding] = char
                self._ipa_phoneme_data[char] = (Vowel, height, frontness, rounding)

    def _load_consonants(self):
        rows = list(csv.reader(open('consonants.txt', 'r', encoding="utf-8"), delimiter='\t'))
        for y in range(1, 13):
            manner = MOA(y - 1)
            self._consonant_data[manner] = {}
            for x in range(1, 22):
                char = rows[y][x]

                place = POA((x - 1) // 2)
                voicing = Voicing((x - 1) % 2)

                if place not in self._consonant_data[manner]:
                    self._consonant_data[manner][place] = {}

                self._consonant_data[manner][place][voicing] = char
                self._ipa_phoneme_data[char] = (Consonant, manner, place, voicing)

    @staticmethod
    def diacritic_filter(text, chars):
        found = False

        for char in chars:
            if char in text:
                found = True
                text = text.replace(char, "")

        return text, found

    def ipa_to_phoneme(self, ipa):
        ipa, voiceless = self.diacritic_filter(ipa, "̥̊")
        ipa, voiced = self.diacritic_filter(ipa, "̬")
        ipa, long = self.diacritic_filter(ipa, "ː")

        data = self._ipa_phoneme_data[ipa]

        args = [Length.normal] + [Stress.unstressed] + list(data[1:])
        phoneme = data[0](*args)

        if voiceless:
            phoneme.voicing = Voicing.unvoiced
        if voiced:
            phoneme.voicing = Voicing.voiced
        if long:
            phoneme.length = Length.long

        return phoneme

    def phoneme_to_ipa(self, phoneme):
        ipa = self.phoneme_to_base_ipa(phoneme)
        if not ipa:
            return None

        if phoneme.length == Length.long:
            ipa += "ː"

        return ipa

    def phonemes_to_ipa(self, phonemes):
        ipa = ""
        prev_stress = Stress.unstressed
        UNSTRESS = Stress.unstressed  # UNSTRESS is short for Stress.unstressed

        stress_char_map = {
            Stress.unstressed: "",
            Stress.stressed: "ˈ",
            Stress.secondary_stressed: "ˌ"
        }

        for phoneme in phonemes:
            char = phoneme.ipa

            if phoneme.stress == UNSTRESS and prev_stress != UNSTRESS:
                char = stress_char_map[prev_stress] + char

            if phoneme.stress != UNSTRESS and prev_stress == UNSTRESS:
                char = stress_char_map[phoneme.stress] + char

            prev_stress = phoneme.stress

            ipa += char

        ipa += stress_char_map[prev_stress]

        return ipa

    def phoneme_to_base_ipa(self, phoneme):
        ipa = None
        if isinstance(phoneme, Vowel):
            ipa = self._vowel_data[phoneme.height][phoneme.frontness][phoneme.rounding]
        if isinstance(phoneme, Consonant):
            ipa = self._consonant_data[phoneme.manner][phoneme.place][phoneme.voicing]

        return ipa


def auto_complete_property(prop_key):
    prop_key = prop_key.strip().lower()

    keys = ["vowel",
            "consonant",
            "front",
            "central",
            "back",
            "close",
            "close_mid",
            "mid",
            "open_mid",
            "open",
            "vowel",
            "consonant",
            "obstruent",
            "plosive",
            "affricate",
            "fricative",
            "sibilant",
            "sonorant",
            "nasal",
            "approximant",
            "vibrant",
            "tap",
            "trill",
            "occlusive",
            "voiced",
            "unvoiced",
            "velar",
            "unstressed",
            "stressed",
            "start",
            "end"]

    for k in keys:
        if k.startswith(prop_key):
            return k

    raise KeyError("Unknown key {}".format(prop_key))


Ipa = IPA()
