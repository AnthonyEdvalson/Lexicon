from typing import List

from phoneme import Ipa, Phonemes, Stress, Length
from dictionary import Dictionary
from rules import Rule, RuleSet
import re


class Romanization:
    def __init__(self, roman_to_ipa):
        self.mapping = {}
        self.mapping_inv = {}

        for roman, ipa in roman_to_ipa.items():
            self.mapping[roman] = Ipa.ipa_to_phoneme(ipa)
            self.mapping_inv[ipa] = roman

    def roman_to_phonemes(self, roman: str):
        phonemes = []
        for char in roman:
            if char in self.mapping:
                phonemes.append(self.mapping[char].copy())
            else:
                raise Exception("Unmapped char '{}' in {}".format(char, roman))

        return Phonemes(phonemes)

    def phonemes_to_roman(self, phonemes: Phonemes):
        roman = ""
        prev_stress = Stress.unstressed

        stress_char_map = {
            Stress.unstressed: "",
            Stress.stressed: "`",
            Stress.secondary_stressed: ","
        }

        for phoneme in phonemes:
            ipa = phoneme.base_ipa

            if ipa in self.mapping_inv:
                char = self.mapping_inv[ipa]

                if phoneme.length == Length.long:
                    char += ":"

                if phoneme.stress == Stress.unstressed and prev_stress != Stress.unstressed:
                    char = stress_char_map[prev_stress] + char
                if phoneme.stress != Stress.unstressed and prev_stress == Stress.unstressed:
                    char = stress_char_map[phoneme.stress] + char
                prev_stress = phoneme.stress

                roman += char
            else:
                raise Exception("Unmapped phoneme '{}' in {}".format(ipa, phonemes))

        return roman


class SyllableData:
    def __init__(self, opt_onsets, req_onsets, opt_codas, req_codas, prime_stress, second_stress):
        regex = "^(c{{{},{}}}vc{{{},{}}}?)+$".format(req_onsets, req_onsets + opt_onsets,
                                                     req_codas, req_codas + opt_codas)
        self.syllable_regex = re.compile(regex)
        self.primary_stress = prime_stress
        self.secondary_stress = second_stress

    def stressify(self, ps: Phonemes):
        syllables = self.syllables(ps)

        syllable_count = len(syllables)

        for i in range(0, syllable_count):
            syllable = syllables[i]
            stress = Stress.unstressed

            if self.primary_stress(i, syllable_count):
                stress = Stress.stressed
            elif self.secondary_stress(i, syllable_count):
                stress = Stress.secondary_stressed

            for phoneme in syllable:
                phoneme.stress = stress

    def syllables(self, phonemes: Phonemes) -> List[Phonemes]:
        """
        syllables = []

        i = 0
        l = len(ps)
        while i < l:
            syllable = []

            for j in range(0, self.required_onsets + self.optional_onsets):
                if ps[i].has_prop("consonant"):
                    syllable.append(ps[i])
                    i += 1
                elif j < self.required_onsets:
                    raise Exception("{} has invalid syllable structure".format(ps))
                else:
                    break

            if ps[i].has_prop("vowel"):
                syllable.append(ps[i])
                i += 1
            else:
                raise Exception("{} has invalid syllable structure".format(ps))

            for j in range(0, self.required_codas + self.optional_codas):
                if i < l and ps[i].has_prop("consonant"):
                    syllable.append(ps[i])
                    i += 1
                elif j < self.required_codas:
                    raise Exception("{} has invalid syllable structure".format(ps))
                else:
                    break

            syllables.append(Phonemes(syllable))

        return syllables
        """
        ps = phonemes.phonemes
        cv_pattern = "".join(map(lambda p: "v" if p.has_prop("vowel") else "c", ps))
        full_cv_pattern = cv_pattern

        syllables = []

        while len(cv_pattern) > 0:
            # Because of regex limitations, we can only extract the last syllable's length
            # This is a bit of a hack, but the alternative is incredibly complex string parsing code
            result = self.syllable_regex.match(cv_pattern)

            if not result:
                raise Exception("{} could not be broken into syllables ({})".format(Phonemes(ps), full_cv_pattern))

            syllable_len = len(result.group(1))

            syllables.insert(0, ps[-syllable_len:])

            cv_pattern = cv_pattern[:-syllable_len]  # string slicing is O(n^2), optimize if needed
            ps = ps[:-syllable_len]

        return syllables


class Language:
    def __init__(self, path):
        path = path.rstrip("/")

        self.romanization = self._load_romanization(path + "/romanization.txt")
        self.syllable_data = self._load_attributes(path + "/attributes.txt")
        self.rules = self._load_rules(path + "/rules.txt")
        self.dictionary = self._load_dictionary(path + "/proto_dictionary.txt")

    def to_phonemes(self, text):
        return self.romanization.roman_to_phonemes(text)

    @staticmethod
    def _load_romanization(path):
        mapping = {}

        with open(path, encoding="utf-8") as f:
            for line in f:
                cells = list(filter(None, line.strip().split(" ")))
                mapping[cells[0]] = cells[-1]

        return Romanization(mapping)

    def _load_dictionary(self, path):
        dictionary = Dictionary(self)

        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.isspace() or line[0] == "#":
                    continue

                cells = list(map(lambda c: c.strip(), filter(None, line.replace("  ", "\t").split("\t"))))

                text = cells[0]
                definitions = list(map(lambda s: s.strip(" \n\t"), cells[-1].split(",")))

                if len(cells) == 2:
                    tags = text.split("+")
                    word = dictionary.to_word(tags, definitions)
                    dictionary.add_word(word)
                elif len(cells) == 3:
                    tag = cells[1]
                    dictionary.add_morpheme(tag, text, definitions)
                else:
                    raise Exception("Bad line '{}'".format(cells))

        return dictionary

    def _load_rules(self, path):
        rules = []

        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.isspace():
                    continue

                rule = Rule.from_string(line)
                rules.append(rule)

        return RuleSet(rules)

    def _load_attributes(self, path):
        syllable_data = {}

        with open(path, encoding="utf-8") as f:
            for line in f:
                k, v = line.split(":")
                k = k.strip().lower()
                v = v.strip().lower()

                if k == "syllable":
                    onset, coda = v.split("v")
                    syllable_data.update({
                        "opt_onsets": onset.count("("),
                        "req_onsets": onset.count("c") - onset.count("("),
                        "opt_codas": coda.count("("),
                        "req_codas": coda.count("c") - coda.count("(")
                    })
                elif k == "primary_stress":
                    code = compile(v, "<string>", "eval")
                    syllable_data["prime_stress"] = lambda i, l: eval(code)
                elif k == "secondary_stress":
                    code2 = compile(v, "<string>", "eval")
                    syllable_data["second_stress"] = lambda i, l: eval(code2)

        return SyllableData(**syllable_data)
