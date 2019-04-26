Lexicon is a tool for creating conlangs (constructed languages) for use in world building. The goal of this tool is to make it easy to create, manage, and modify conlangs in a way that reduces redundancy.

It comes with a sample language that I made for a D&D game, which was the inspiration for making this tool. It's not anything special, but shows a possible use for Lexicon.

# Why Lexicon
Most conlangs are created by people using written notes, text documents, or spreadsheets. These tools are effective, but are fairly primitive. There are many opportunities for optimization, simplification, and automation when using a customized tool to write a conlang when compared to a generic text document.

## Vocabulary

To show the advantages of this tool, I'm going to show how the english word "cuter" can be put in the system.

First, the word is broken into it's meaningful parts, also called morphemes. In this case there is two, "cute" and "-er"

```
# proto_dictionary.txt
cyut    CUTE    adorable, small
-er     MORE    modifies the root to mean more by comparison
 
CUTE+MORE   more cute than
```

The first line defines the morpheme "CUTE", and says what it sounds like, as well as it's definition. Cyut is the pronunciation, each sound is interpreted literally, which is why it looks a bit strange. "CUTE" is a tag that is used internally, it isn't the written representation of the word. In fact, nowhere in Lexicon is writing considered. Writing systems can be incredibly complex, and the focus of Lexicon is pronunciation and vocabulary, not writing.  
 
The next line define the morpheme "MORE". The dash shows that this is a bound morpheme, and cannot exist on it's own.

The last line is where it gets interesting. This is a word definition, it says to combine the CUTE and MORE morphemes into a word that means "more cute than". Notice how there is no pronunciation for this word, this is because Lexicon will make it for us.

After running lexicon it will show that CUTE+MORE = cyuter, and cyuter means "more cute than". There are several benefits to this system
 - Morphemes are only defined once, so changing -er to -es causes it to update everywhere at once.
 - Morphemes can be easily reused with custom tag names, making for more consistent prefixes and suffixes
 - Allow for structures such as grammatical gender to arise naturally, as explained in the rules section

The problem with the word "cuter" is its pronunciation, if spoken in it's current state, it sounds like "cyoo-ter". Although not technically wrong, it sounds a bit awkward. Most people say cuter as "cyoo-der", as it sounds more natural. This is where the linguistic rules are applied to create a more realistic pronunciation. 

## Rules

Languages have many complex rules that modify how words are pronounced. In English, if a "t" has a vowel before and after, and then an "r" at the end, the "t" is always pronounced as a "d", as in the word "cuter", although spelled with a "t" it's clear that everyone pronounces it as a "d".

In lexicon this change can be represented as:

```
# rules.txt
(VOW)(*t)(VOW)(*r)  p[1]["voicing"] = True
```

When a word is made in Lexicon, all the rules in rules.txt are applied in order. For each of the rules, it searches for a match in the word. In the example above, it looks for any vowel, the letter "t", another vowel, and then the letter "r". 

If anywhere in the word matches this pattern, the rule is applied. This rule, when applied, will take the sound at index 1, in this case "t". it then makes that sound voiced. In linguistics this means that thee vocal chords when making the sound. It turns out that "t" when voiced is just the sound "d". So the rule effectively replaces the "t" at index 1 with a "d"

This is repeated for all rules in rules.txt, giving a proper modified pronunciation of the original word.

Rules are often used to simulate time. 15-20 rules can be applied on top of each other to create a language that is completely different from the original. Also, adding and removing rules a few rules can create new dialects and accents.


## Phonology

In a constructed language, there may be unusual sounds, or need to distinguish between sounds that are ambiguous in english. This is where Lexicon's phonology system is used.

To deal with this Lexicon has a Phoneme class that contains the information necessary to produce a sound. Rather than storing the letter "t", it stores "unvoiced dental plosive", which is linguistic speak for releasing pressure built up by placing the tongue on the teeth.

In doing so, sounds can be manipulated far more flexibly, which becomes very useful with Lexicon's rule system, and allows for complex linguistic structures to be a breeze to deal with.

However, this system is great for developers and computers to deal with, but not particularly easy for an end user who has to type "unvoiced dental plosive" instead of "t". This is where romanization comes in 

When defining a language, a romanization is specified, which is a mapping from letters on the keyboard to specific sounds. This makes it much easier to read and write sounds.

```
# romanization.txt
a   a
'   ʔ
```

In this example, the language has two sounds. On the left is the romanized character, or user friendly character. On the right is the IPA character for the corresponding sound.

The IPA is the most popular way linguists record sounds unambiguously. One symbol makes one sound, no exceptions. The symbols tend to line up with English and other european languages, so in this language if "a" is typed, it reads it as "front open unrounded vowel", which sounds like a relaxing "ahhhhh".

The next once is more interesting, in the second mapping " ' " is used for "ʔ", which in IPA is the "voiced glottal stop". In English this sound is pretty rare, and does not make any sound. It represents the closing of the throat in the middle of "uh-oh".

This system means that special keyboards and alt-codes are not needed, and the mapping of characters to sounds is customizable.

This also mean that sounds can be changed universally. The language's sounds can be changed in one place, and everything will update accordingly. With this system, it is possible to make multiple languages by keeping the same vocabulary and rules, but modify the romanization to give it a different flavor.
 

## Text To Speech

Lexicon also includes the espeak TTS, which is a very robotic sounding, but flexible text to speech system. This allows it to say any word in the constructed language. This way the user can hear exactly how the words will sound without having to look up the IPA table. This is particularly helpful for very long words or sentences.


## Attributes

Attributes.txt is a file that holds some additional info about the language, namely, the syllable structure and syllable stress. The format for this file is very rough, so I won't go into a huge amount of detail since it's one of the first things I'd like to fix.
 
```
SYLLABLE: (C)V(C)(C)
PRIMARY_STRESS: l == 1 or i == l - 2
SECONDARY_STRESS: i < l - 4 and i % 3 == 1
```

The first line defines the syllable structure, in this case, (C)V(C)(C). This says that syllables contain a vowel with up to one consonant before, and up to two consonants after.

The second line defines the primary stress for the word. In this case, this is penultimate stress, meaning the stress is always on the second to last syllable. The only exception is if there is only one syllable, then the first syllable is stressed

The third line defines secondary stress. In this case, the second syllable, and every third syllable after are stressed. This rule only applies to long words, and no syllables have secondary stress unless they are at least 4 syllables from the end

The reason I don't like this system, is that the stresses are inserted directly into an if statement internally. There should at least be a way to enter PENULTIMATE, rather than "l == 1 or i == l - 2" for readability. 