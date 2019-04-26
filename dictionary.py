import bisect
from typing import List

from phoneme import Phonemes


class Morpheme:
    def __init__(self, prefix: Phonemes, postfix: Phonemes, definitions):
        self.prefix = prefix
        self.postfix = postfix
        self.definitions = definitions

    def apply(self, ipa):
        return self.prefix.copy() + ipa + self.postfix.copy()

    def __str__(self):
        return "{}-{}".format(self.prefix, self.postfix)


class Word:
    def __init__(self, lang, morphemes: List[Morpheme], definitions):
        self.lang = lang
        self.morphemes = morphemes
        self.definitions = definitions

    @property
    def phonemes(self) -> Phonemes:
        ps = self.raw_phonemes
        self.lang.syllable_data.stressify(ps)  # Solve stressing for rules
        self.lang.rules.apply(ps)              # Apply phonetic rules
        self.lang.syllable_data.stressify(ps)  # Reapply stressing, since syllables may have moved / changed
        return ps

    @property
    def raw_phonemes(self) -> Phonemes:
        ps = Phonemes()
        for morpheme in self.morphemes:
            ps = morpheme.apply(ps)
        return ps

    @property
    def ipa(self):
        return self.phonemes.ipa

    def __lt__(self, other):
        if isinstance(other, Word):
            return self.phonemes < other.phonemes
        if isinstance(other, Phonemes):
            return self.phonemes < other
        if isinstance(other, str):
            for phoneme, char in zip(self.phonemes, other):
                if phoneme < char:
                    return True
                elif char < phoneme:
                    return False

            if len(self.phonemes) < other:
                return True

            return False

        raise TypeError("Cannot compare {} with word".format(other.type))

    def __str__(self):
        return str(self.phonemes)


class Dictionary:
    def __init__(self, lang):
        self.lang = lang
        self._morphemes = {}
        self._words = []

    def add_morpheme(self, tag: str, text, definitions):
        split = text.find("-")
        pre = self.lang.to_phonemes(text[:max(0, split)])
        post = self.lang.to_phonemes(text[split+1:])

        morpheme = Morpheme(pre, post, definitions)
        self._morphemes[tag] = morpheme

        if split < 0:  # check if free morpheme
            self.add_word(self.to_word([tag], morpheme.definitions))

        return morpheme

    def to_word(self, tags, definitions):
        morphemes = [self.get_morpheme(tag) for tag in tags]
        return Word(self.lang, morphemes, definitions)

    def add_word(self, word):
        bisect.insort_left(self._words, word)
        return word

    def get_morpheme(self, tag):
        return self._morphemes[tag]

    def get_word(self, text):
        phonemes = self.lang.to_phonemes(text)
        i = bisect.bisect_left(self._words, phonemes)

        if i != len(self._words) and self._words[i].phonemes == phonemes:
            return self._words[i]

        raise ValueError("Cannot find {} ({})".format(text, phonemes))

    def __iter__(self):
        return iter(self._words)