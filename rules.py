import re
from enum import Enum
from typing import List

from phoneme import Consonant, Vowel, auto_complete_property, Phonemes


class FilterMode(Enum):
    must_have = 0
    must_be = 1
    at = 2


class PropertyFilter:
    def __init__(self, key, filter_mode, invert):
        self.key = key
        self.filter_mode = filter_mode
        self.invert = invert

    @staticmethod
    def from_string(string):
        literal = string.startswith("*")
        invert = string.startswith("!")
        key = string.strip("! *")

        if literal:
            return PropertyFilter(key, FilterMode.must_be, invert)

        key = auto_complete_property(key)

        if key == "start" or key == "end":
            return PropertyFilter(key, FilterMode.at, invert)

        return PropertyFilter(key, FilterMode.must_have, invert)

    def matches(self, phoneme, is_first, is_last):

        if self.filter_mode == FilterMode.must_have:
            result = phoneme.has_prop(self.key)
        elif self.filter_mode == FilterMode.must_be:
            result = phoneme.ipa == self.key
        elif self.filter_mode == FilterMode.at:
            if self.key == "start":
                result = is_first
            elif self.key == "end":
                result = is_last
            else:
                raise Exception(":(")
        else:
            raise Exception(":(")

        return result if not self.invert else not result

    def __str__(self):
        pre = "!" if self.invert else ""
        return pre + str(self.key)

    def __repr__(self):
        return self.__str__()


class PhonemeMatch:
    def __init__(self, filters):
        self.filters = filters

    @staticmethod
    def from_string(string):
        props = string.split(" ")
        filters = [PropertyFilter.from_string(s) for s in props]
        return PhonemeMatch(filters)

    def matches(self, phoneme, is_first, is_last):
        for filt in self.filters:
            if not filt.matches(phoneme, is_first, is_last):
                return False

        return True

    def __str__(self):
        return "({})".format(" ".join(map(str, self.filters)))

    def __repr__(self):
        return self.__str__()


class PhonemePattern:
    _term_finder = re.compile(r"[^() ][^)]*")

    def __init__(self, pattern):
        self.pattern = pattern

    @staticmethod
    def from_string(string):
        pattern = []
        matches = PhonemePattern._term_finder.findall(string)
        for match in matches:
            phoneme_match = PhonemeMatch.from_string(match)

            pattern.append(phoneme_match)

        return PhonemePattern(pattern)

    def match(self, phonemes):
        pattern_len = len(self.pattern)

        for phonemes_index in range(0, len(phonemes) - pattern_len + 1):
            found_match = True

            for i in range(0, pattern_len):
                pattern_match = self.pattern[i]
                phoneme = phonemes[phonemes_index + i]

                is_first = phonemes_index + i == 0
                is_last = phonemes_index + i == len(phonemes) - 1

                if not pattern_match.matches(phoneme, is_first, is_last):
                    found_match = False
                    break

            if found_match:
                return phonemes_index, pattern_len

        return -1, -1

    def __str__(self):
        return "".join(map(str, self.pattern))

    def __repr__(self):
        return self.__str__()


class MutableRulePhoneme:
    def __init__(self, phoneme):
        self.deleted = False
        self.type = Vowel if isinstance(phoneme, Vowel) else Consonant
        self.props = phoneme.as_dict()

    def rem(self):
        self.deleted = True

    def __setitem__(self, key, value):
        self.props[key] = value

    def __getitem__(self, key):
        return self.props[key]

    def to_phoneme(self):
        return None if self.deleted else self.type(**self.props)


class Rule:
    def __init__(self, pattern, action):
        self.pattern = pattern
        self.action = compile(action, "<string>", "exec")

    @staticmethod
    def from_string(string):
        pattern, action = string.split("  ", 1)
        pattern = pattern.strip()
        action = action.strip()

        phoneme_pattern = PhonemePattern.from_string(pattern)

        return Rule(phoneme_pattern, action)

    def apply(self, phonemes):
        index, length = self.pattern.match(phonemes)

        if index == -1:
            return False  # No match

        p = []

        for i in range(index, index + length):
            phoneme = phonemes[i]
            mrp = MutableRulePhoneme(phoneme)
            p.append(mrp)

        exec(self.action)

        for i in range(0, length):
            p_i = i + index
            phoneme = p[i].to_phoneme()

            if phoneme:
                phonemes[p_i] = phoneme
            else:
                index -= 1
                del phonemes[p_i]

        return True

    def __str__(self):
        return "{}\t{}".format(str(self.pattern), self.action)

    def __repr__(self):
        return self.__str__()


class RuleSet:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def apply(self, phonemes: Phonemes):
        for rule in self.rules:
            rule.apply(phonemes)

"""
r = Rule.from_string('(VOW)(VOW)          p[1].rem() ; p[0]["length"] = "long"')
roman = Romanization({"o": "o", "a": "a", "t": "t", "o:": "oː"})
word = roman.roman_to_phoneme("otoa")
print(roman.phoneme_to_roman(word))
r.apply(word)
print(roman.phoneme_to_roman(word))
"""
