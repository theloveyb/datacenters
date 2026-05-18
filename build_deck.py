"""
Build Punjabi_Reading.apkg — a four-subdeck Anki deck for a fluent Punjabi
speaker learning to read the Gurmukhi script.

No English glosses on vocabulary cards: the learner already speaks the
language. Romanization unlocks pronunciation; fluency supplies meaning.
"""

import os
import sys
import textwrap

import genanki


# ---------------------------------------------------------------------------
# Deterministic IDs (random but fixed so re-imports update the same notes).
# ---------------------------------------------------------------------------
TOP_DECK_ID = 1820471101
LETTERS_DECK_ID = 1820471102
MUHARNI_DECK_ID = 1820471103
CONJUNCTS_DECK_ID = 1820471104
SIGHT_DECK_ID = 1820471105

LETTERS_MODEL_ID = 1620471201
MUHARNI_MODEL_ID = 1620471202
CONJUNCTS_MODEL_ID = 1620471203
SIGHT_MODEL_ID = 1620471204


# ---------------------------------------------------------------------------
# Shared CSS — Noto Sans Gurmukhi with sans-serif fallback, large fronts.
# ---------------------------------------------------------------------------
CARD_CSS = """
.card {
  font-family: "Noto Sans Gurmukhi", "Gurmukhi MN", "Lohit Punjabi",
               "Raavi", "Nirmala UI", sans-serif;
  background-color: #fafaf7;
  color: #1f1f1f;
  text-align: center;
  padding: 32px 20px;
  line-height: 1.45;
}

.front-glyph {
  font-size: 140px;
  font-weight: 500;
  margin: 24px 0 32px 0;
  letter-spacing: 0.02em;
}

.back-glyph {
  font-size: 96px;
  font-weight: 500;
  margin: 8px 0 12px 0;
}

.back-glyph-medium {
  font-size: 64px;
  font-weight: 500;
  margin: 4px 0 10px 0;
}

.name {
  font-size: 30px;
  color: #444;
  margin: 14px 0 6px 0;
}

.roman {
  font-size: 28px;
  color: #444;
  margin: 8px 0 14px 0;
  font-style: italic;
}

.exemplar {
  font-size: 44px;
  margin: 18px 0 4px 0;
}

.exemplar-roman {
  font-size: 24px;
  color: #555;
  font-style: italic;
  margin: 0 0 18px 0;
}

.examples {
  margin: 14px auto;
  max-width: 520px;
  text-align: left;
}

.examples-row {
  font-size: 24px;
  margin: 6px 0;
}

.examples-row .pa {
  margin-right: 14px;
}

.examples-row .rom {
  color: #555;
  font-style: italic;
  font-size: 20px;
}

.pos {
  font-size: 22px;
  color: #6a4a00;
  background-color: #faf2dd;
  display: inline-block;
  padding: 4px 14px;
  border-radius: 12px;
  margin: 10px 0;
}

.note {
  font-size: 18px;
  color: #555;
  margin: 18px auto 0 auto;
  max-width: 560px;
  line-height: 1.55;
  text-align: left;
}

hr#answer {
  border: none;
  border-top: 1px solid #d8d8d2;
  margin: 18px auto;
  width: 80%;
}
"""


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
letters_model = genanki.Model(
    LETTERS_MODEL_ID,
    "Punjabi Letter",
    fields=[
        {"name": "Glyph"},
        {"name": "Name"},
        {"name": "Exemplar"},
        {"name": "ExemplarRoman"},
        {"name": "Note"},
        {"name": "Category"},
    ],
    templates=[
        {
            "name": "Glyph -> Info",
            "qfmt": '<div class="front-glyph">{{Glyph}}</div>',
            "afmt": (
                '<div class="back-glyph">{{Glyph}}</div>'
                '<div class="name">{{Name}}</div>'
                '<hr id="answer">'
                '<div class="exemplar">{{Exemplar}}</div>'
                '<div class="exemplar-roman">{{ExemplarRoman}}</div>'
                '<div class="note">{{Note}}</div>'
            ),
        }
    ],
    css=CARD_CSS,
)

muharni_model = genanki.Model(
    MUHARNI_MODEL_ID,
    "Punjabi Muharni",
    fields=[
        {"name": "Syllable"},
        {"name": "Roman"},
        {"name": "Pairing"},
        {"name": "Examples"},
    ],
    templates=[
        {
            "name": "Syllable -> Sound",
            "qfmt": '<div class="front-glyph">{{Syllable}}</div>',
            "afmt": (
                '<div class="back-glyph-medium">{{Syllable}}</div>'
                '<div class="roman">{{Roman}}</div>'
                '<hr id="answer">'
                '<div class="note">{{Pairing}}</div>'
                '<div class="examples">{{Examples}}</div>'
            ),
        }
    ],
    css=CARD_CSS,
)

conjuncts_model = genanki.Model(
    CONJUNCTS_MODEL_ID,
    "Punjabi Conjunct",
    fields=[
        {"name": "Front"},
        {"name": "Glyph"},
        {"name": "Roman"},
        {"name": "Note"},
    ],
    templates=[
        {
            "name": "Conjunct -> Info",
            "qfmt": '<div class="front-glyph">{{Front}}</div>',
            "afmt": (
                '<div class="back-glyph-medium">{{Glyph}}</div>'
                '<div class="roman">{{Roman}}</div>'
                '<hr id="answer">'
                '<div class="note">{{Note}}</div>'
            ),
        }
    ],
    css=CARD_CSS,
)

sight_model = genanki.Model(
    SIGHT_MODEL_ID,
    "Punjabi Sight Word",
    fields=[
        {"name": "Word"},
        {"name": "Roman"},
        {"name": "POS"},
        {"name": "Note"},
    ],
    templates=[
        {
            "name": "Word -> Read",
            "qfmt": '<div class="front-glyph">{{Word}}</div>',
            "afmt": (
                '<div class="back-glyph-medium">{{Word}}</div>'
                '<div class="roman">{{Roman}}</div>'
                '<hr id="answer">'
                '<div class="pos">{{POS}}</div>'
                '<div class="note">{{Note}}</div>'
            ),
        }
    ],
    css=CARD_CSS,
)


# ---------------------------------------------------------------------------
# Subdeck 1: Letters
# ---------------------------------------------------------------------------
# Format: (glyph, name, exemplar_gurmukhi, exemplar_roman, note, category)
LETTERS = [
    # ---- Vowel-bearers (matra vahak) ---------------------------------------
    ("ੳ", "ura",
     "ਉਹ", "uh",
     "Vowel-bearer for back, rounded vowels. Carries ੁ (aunkar), ੂ (dulainkar) "
     "and ੋ (hora). Never stands alone — without a matra it has no sound.",
     "vowel-bearer"),
    ("ਅ", "aira",
     "ਅੱਜ", "ajj",
     "Vowel-bearer for the central, open vowel /a/. Unique among the three: "
     "in isolation it carries the inherent vowel /a/ (the mukta). Also bears "
     "ਾ (kanna), ੈ (dulavan) and ੌ (kanaura).",
     "vowel-bearer"),
    ("ੲ", "iri",
     "ਇਹ", "ih",
     "Vowel-bearer for front vowels /i/, /iː/, /eː/. Carries ਿ (sihari), "
     "ੀ (bihari) and ੇ (lavan). Never stands alone.",
     "vowel-bearer"),

    # ---- Velars (back of the mouth; tongue against soft palate) ------------
    ("ਕ", "kakka",
     "ਕਰ", "kar",
     "Voiceless unaspirated velar stop /k/. Back of the tongue touches the "
     "soft palate. First letter of the painti and the most common Punjabi "
     "consonant.",
     "velar"),
    ("ਖ", "khakkha",
     "ਖਾਣਾ", "khaaNaa",
     "Voiceless aspirated velar stop /kʰ/ — like ਕ but with a strong puff of "
     "breath. Don't confuse with the dotted ਖ਼ (Persian /x/, often pronounced "
     "the same as ਖ in modern speech).",
     "velar"),
    ("ਗ", "gagga",
     "ਗੱਲ", "gall",
     "Voiced unaspirated velar stop /g/. Same place of articulation as ਕ but "
     "with vocal-cord vibration and no aspiration.",
     "velar"),
    ("ਘ", "ghaggha",
     "ਘਰ", "khàr (low-tone kar)",
     "Historically the voiced aspirated /gʱ/. Modern Punjabi has no voiced "
     "aspirates: instead, this letter marks LOW TONE on the syllable. So ਘਰ "
     "is read as low-tone /kàr/, not /ghar/.",
     "velar"),
    ("ਙ", "ngangna",
     "ਙਿਆਨ", "ngiaan (rare)",
     "Velar nasal /ŋ/, like the 'ng' in English 'sing'. Very rare as an "
     "independent letter in modern Punjabi; mostly appears in tatsama "
     "(Sanskritic) words.",
     "velar"),

    # ---- Palatals (tongue against the hard palate) -------------------------
    ("ਚ", "chachcha",
     "ਚਾਹ", "chaah",
     "Voiceless unaspirated palatal affricate /tʃ/, the 'ch' in English "
     "'church'. Tongue body presses against the hard palate.",
     "palatal"),
    ("ਛ", "chhachha",
     "ਛੇ", "chhe",
     "Voiceless aspirated palatal affricate /tʃʰ/ — ਚ with a strong puff. "
     "Romanized 'chh' to keep it distinct from plain 'ch'.",
     "palatal"),
    ("ਜ", "jajja",
     "ਜਾਣਾ", "jaaNaa",
     "Voiced unaspirated palatal affricate /dʒ/, the 'j' in English 'jam'.",
     "palatal"),
    ("ਝ", "jhajja",
     "ਝੱਲ", "chàll (low-tone)",
     "Historically /dʒʱ/. In modern Punjabi marks LOW TONE on the syllable, "
     "with the consonant itself realised as voiceless /tʃ/.",
     "palatal"),
    ("ਞ", "nyanya",
     "ਞਾਨ", "nyaan (rare)",
     "Palatal nasal /ɲ/, like Spanish 'ñ'. Very rare in modern Punjabi.",
     "palatal"),

    # ---- Retroflexes (tongue curled back to touch the palate) --------------
    ("ਟ", "Tainka",
     "ਟਮਾਟਰ", "TamaaTar",
     "Voiceless unaspirated retroflex stop /ʈ/. Tongue tip curls back and "
     "strikes the roof of the mouth. Romanized with capital T to distinguish "
     "from dental ਤ.",
     "retroflex"),
    ("ਠ", "Thaththa",
     "ਠੰਡ", "ThanD",
     "Voiceless aspirated retroflex stop /ʈʰ/. Retroflex ਟ + a puff of "
     "breath.",
     "retroflex"),
    ("ਡ", "Dadda",
     "ਡਰ", "Dar",
     "Voiced unaspirated retroflex stop /ɖ/. Capital D for retroflex; small "
     "d is reserved for the dental ਦ.",
     "retroflex"),
    ("ਢ", "Dhaddha",
     "ਢੋਲ", "Thòl (low-tone Dol)",
     "Historically voiced aspirated retroflex /ɖʱ/. In modern Punjabi marks "
     "LOW TONE on the syllable; the consonant surfaces as voiceless /ʈ/.",
     "retroflex"),
    ("ਣ", "Nana",
     "ਪਾਣੀ", "paaNee",
     "Retroflex nasal /ɳ/. Capital N to distinguish from dental ਨ. Never "
     "occurs word-initially.",
     "retroflex"),

    # ---- Dentals (tongue against the teeth) --------------------------------
    ("ਤ", "tatta",
     "ਤੇ", "te",
     "Voiceless unaspirated dental stop /t̪/. Tongue tip against the upper "
     "teeth (not the alveolar ridge — softer than English 't').",
     "dental"),
    ("ਥ", "thaththa",
     "ਥਾਂ", "thaa(n)",
     "Voiceless aspirated dental stop /t̪ʰ/. ਤ with a puff. Often confused "
     "by English speakers with the English 'th' sound — Punjabi has no "
     "/θ/.",
     "dental"),
    ("ਦ", "dadda",
     "ਦੇ", "de",
     "Voiced unaspirated dental stop /d̪/. Small d for dental; capital D is "
     "the retroflex ਡ.",
     "dental"),
    ("ਧ", "dhaddha",
     "ਧੋਣਾ", "thòNaa (low-tone)",
     "Historically voiced aspirated dental /d̪ʱ/. In modern Punjabi marks "
     "LOW TONE; the consonant is realised as voiceless /t̪/.",
     "dental"),
    ("ਨ", "nanna",
     "ਨਹੀਂ", "nahee(n)",
     "Dental nasal /n/. The default 'n' sound and one of the highest-"
     "frequency consonants in Punjabi.",
     "dental"),

    # ---- Labials (lips) ----------------------------------------------------
    ("ਪ", "pappa",
     "ਪਾਣੀ", "paaNee",
     "Voiceless unaspirated bilabial stop /p/. Both lips close, no puff of "
     "breath.",
     "labial"),
    ("ਫ", "phappha",
     "ਫੁੱਲ", "phull",
     "Voiceless aspirated bilabial stop /pʰ/. ਪ with a strong puff. The "
     "dotted ਫ਼ is the genuine /f/ sound borrowed from Persian; without the "
     "dot, this is just aspirated p.",
     "labial"),
    ("ਬ", "babba",
     "ਬੋਲ", "bol",
     "Voiced unaspirated bilabial stop /b/.",
     "labial"),
    ("ਭ", "bhabbha",
     "ਭਰ", "pàr (low-tone)",
     "Historically voiced aspirated bilabial /bʱ/. In modern Punjabi marks "
     "LOW TONE; the consonant surfaces as voiceless /p/.",
     "labial"),
    ("ਮ", "mamma",
     "ਮੈਂ", "mai(n)",
     "Bilabial nasal /m/. Both lips close while air exits through the nose.",
     "labial"),

    # ---- Semivowels --------------------------------------------------------
    ("ਯ", "yaiyya",
     "ਯਾਰ", "yaar",
     "Palatal approximant /j/, the 'y' in English 'yes'. Less common than "
     "in Hindi/Sanskrit — many tatsama y- words are pronounced with ਜ in "
     "Punjabi.",
     "semivowel"),
    ("ਰ", "rara",
     "ਰਾਤ", "raat",
     "Alveolar tap/trill /ɾ/. Single flap of the tongue tip against the "
     "alveolar ridge — softer than English r. Don't confuse with retroflex "
     "ੜ.",
     "semivowel"),
    ("ਲ", "lalla",
     "ਲੋਕ", "lok",
     "Dental/alveolar lateral approximant /l/.",
     "semivowel"),
    ("ਵ", "vavva",
     "ਵੀ", "vee",
     "Labiodental approximant /ʋ/, between English v and w. Realised closer "
     "to /v/ before front vowels and /w/ before back vowels.",
     "semivowel"),
    ("ੜ", "Rara",
     "ਘੋੜਾ", "khòRaa",
     "Retroflex flap /ɽ/. Tongue tip flicks back from the palate. Never "
     "occurs word-initially. Capital R distinguishes it from alveolar ਰ.",
     "semivowel"),

    # ---- Sibilants / fricatives -------------------------------------------
    ("ਸ", "sassa",
     "ਸੀ", "see",
     "Voiceless alveolar sibilant /s/. The original Gurmukhi 's'; the "
     "dotted ਸ਼ is the borrowed 'sh' sound.",
     "sibilant"),
    ("ਹ", "haha",
     "ਹੈ", "hai",
     "Voiced glottal fricative /ɦ/. Word-initially behaves like English h; "
     "elsewhere it often triggers HIGH tone on the preceding syllable and "
     "may be silent. The subjoined form ੍ਹ is central to Punjabi's tone "
     "system.",
     "sibilant"),

    # ---- Six dotted (Perso-Arabic) additions -------------------------------
    ("ਸ਼", "shashsha",
     "ਸ਼ਹਿਰ", "shahir",
     "ਸ + nukta dot → /ʃ/, the 'sh' sound. The most stable of the six "
     "dotted letters: pronounced distinctly from ਸ in all registers.",
     "dotted"),
    ("ਖ਼", "khakhkha (dotted)",
     "ਖ਼ਬਰ", "khabar",
     "ਖ + nukta → /x/, the voiceless velar fricative of Persian/Arabic "
     "loans (like the 'ch' in German 'Bach'). In colloquial Punjabi often "
     "merged with plain ਖ /kʰ/.",
     "dotted"),
    ("ਗ਼", "ghaghgha (dotted)",
     "ਗ਼ਜ਼ਲ", "ghazal",
     "ਗ + nukta → /ɣ/, the voiced velar fricative of Persian/Arabic loans. "
     "In colloquial Punjabi often merged with plain ਗ /g/.",
     "dotted"),
    ("ਜ਼", "zazza",
     "ਜ਼ਮੀਨ", "zameen",
     "ਜ + nukta → /z/, the voiced alveolar sibilant. Reliably distinct "
     "from ਜ in most speakers — borrowed mainly from Persian and English.",
     "dotted"),
    ("ਫ਼", "faffa",
     "ਫ਼ੌਜ", "fauj",
     "ਫ + nukta → /f/, the voiceless labiodental fricative. Often retained "
     "as /f/ in careful speech but merges with ਫ /pʰ/ in casual speech.",
     "dotted"),
    ("ਲ਼", "Lalla (dotted)",
     "ਆਲ਼ੂ", "aaLoo",
     "ਲ + nukta → /ɭ/, the retroflex lateral. The most recently added of "
     "the six (Unicode 1998). Native Punjabi sound, not a Persian "
     "borrowing — distinguishes pairs like ਪਲ /pal/ vs ਪਲ਼ /paɭ/.",
     "dotted"),

    # ---- 10 vowel matras (laga matra) --------------------------------------
    ("(mukta)", "mukta",
     "ਕਰ", "kar",
     "The 'unwritten' vowel: every base consonant with no matra carries an "
     "inherent /a/ (schwa-like). Inherent /a/ is often dropped at the end "
     "of a word (so ਕਰ is read 'kar', not 'kara').",
     "matra"),
    ("ਾ", "kanna",
     "ਕਾਰ", "kaar",
     "Long /aː/. Vertical line attached to the right of the consonant. "
     "Same character used independently in the vowel ਆ (ਅ + ਾ).",
     "matra"),
    ("ਿ", "sihari",
     "ਕਿਤਾਬ", "kitaab",
     "Short /i/. Written BEFORE the consonant in print but pronounced "
     "AFTER it. Independent form: ਇ (ੲ + ਿ).",
     "matra"),
    ("ੀ", "bihari",
     "ਕੀ", "kee",
     "Long /iː/. Written after the consonant. Independent form: ਈ.",
     "matra"),
    ("ੁ", "aunkar",
     "ਕੁਝ", "kujh",
     "Short /u/. Subscript hook attached below the consonant. Independent "
     "form: ਉ (ੳ + ੁ).",
     "matra"),
    ("ੂ", "dulainkar",
     "ਕੂੜਾ", "kooRaa",
     "Long /uː/. Subscript double-hook below the consonant. The 'du' in "
     "the name = 'double'. Independent form: ਊ.",
     "matra"),
    ("ੇ", "lavan",
     "ਕੇ", "ke",
     "Long /eː/ (close-mid front). Two short strokes above the consonant. "
     "Independent form: ਏ.",
     "matra"),
    ("ੈ", "dulavan",
     "ਕੈਸਾ", "kaisaa",
     "Diphthong/long /ɛː/, romanized 'ai'. Three strokes above the "
     "consonant. Independent form: ਐ.",
     "matra"),
    ("ੋ", "hora",
     "ਕੋਈ", "koee",
     "Long /oː/ (close-mid back). Diagonal stroke above + curve right of "
     "consonant. Independent form: ਓ.",
     "matra"),
    ("ੌ", "kanaura",
     "ਕੌਣ", "kau(n)",
     "Diphthong/long /ɔː/, romanized 'au'. Independent form: ਔ.",
     "matra"),

    # ---- 3 suprasegmental diacritics --------------------------------------
    ("ੰ", "tippi",
     "ਪੰਜ", "panj",
     "Nasalization mark used on short vowels (/a/, /i/, /u/ after a "
     "consonant). Realised as a homorganic nasal before a consonant. Also "
     "geminates the nasals ਙ, ਞ, ਨ, ਮ. Sits above the headline like a "
     "small loop.",
     "diacritic"),
    ("ਂ", "bindi",
     "ਨਹੀਂ", "nahee(n)",
     "Nasalization mark used on LONG vowels (ਾ, ੀ, ੂ, ੇ, ੈ, ੋ, ੌ) and on "
     "ਉ. Romanized as (n) after the vowel. Visually a single dot above.",
     "diacritic"),
    ("ੱ", "addak",
     "ਕੁੱਤਾ", "kuttaa",
     "Gemination mark: doubles (lengthens) the FOLLOWING consonant. ਕੁੱਤਾ "
     "is read 'kut-taa', not 'kutaa'. Visually like a small 'S' above the "
     "headline.",
     "diacritic"),
]


# ---------------------------------------------------------------------------
# Subdeck 2: Muharni (10 consonants × 10 matras = 100 cards)
# ---------------------------------------------------------------------------
# Matra info: (matra_char, matra_name, roman_suffix, mukta_flag)
MATRAS = [
    ("",  "mukta",     "",   True),   # inherent /a/
    ("ਾ", "kanna",     "aa", False),
    ("ਿ", "sihari",    "i",  False),
    ("ੀ", "bihari",    "ee", False),
    ("ੁ", "aunkar",    "u",  False),
    ("ੂ", "dulainkar", "oo", False),
    ("ੇ", "lavan",     "e",  False),
    ("ੈ", "dulavan",   "ai", False),
    ("ੋ", "hora",      "o",  False),
    ("ੌ", "kanaura",   "au", False),
]

# For each (consonant, matra-roman-suffix) we provide 2-3 real Punjabi words.
# Words are picked so the syllable itself appears prominently in the word.
MUHARNI_EXAMPLES = {
    # rara ਰ
    ("ਰ", ""):   [("ਰਮ", "ram"), ("ਰਖ", "rakh")],
    ("ਰ", "aa"): [("ਰਾਤ", "raat"), ("ਰਾਜ", "raaj"), ("ਰਾਮ", "raam")],
    ("ਰ", "i"):  [("ਰਿਹਾ", "rihaa"), ("ਰਿਸ਼ਤਾ", "rishtaa")],
    ("ਰ", "ee"): [("ਰੀਤ", "reet"), ("ਰੀਝ", "reejh")],
    ("ਰ", "u"):  [("ਰੁੱਖ", "rukkh"), ("ਰੁਪਿਆ", "rupiaa")],
    ("ਰ", "oo"): [("ਰੂਪ", "roop"), ("ਰੂਹ", "rooh")],
    ("ਰ", "e"):  [("ਰੇਤ", "ret"), ("ਰੇਲ", "rel")],
    ("ਰ", "ai"): [("ਰੈਣ", "raiN"), ("ਰੈਲੀ", "railee")],
    ("ਰ", "o"):  [("ਰੋਟੀ", "roTee"), ("ਰੋਜ਼", "roz")],
    ("ਰ", "au"): [("ਰੌਣਕ", "rauNak"), ("ਰੌਲਾ", "raulaa")],

    # dadda ਦ
    ("ਦ", ""):   [("ਦਮ", "dam"), ("ਦਰ", "dar")],
    ("ਦ", "aa"): [("ਦਾਦਾ", "daadaa"), ("ਦਾਲ", "daal"), ("ਦਾਣਾ", "daaNaa")],
    ("ਦ", "i"):  [("ਦਿਨ", "din"), ("ਦਿਲ", "dil")],
    ("ਦ", "ee"): [("ਦੀਵਾ", "deevaa"), ("ਦੀਦਾ", "deedaa")],
    ("ਦ", "u"):  [("ਦੁਖ", "dukh"), ("ਦੁਆ", "duaa")],
    ("ਦ", "oo"): [("ਦੂਰ", "door"), ("ਦੂਜਾ", "doojaa")],
    ("ਦ", "e"):  [("ਦੇਸ਼", "desh"), ("ਦੇਣਾ", "deNaa")],
    ("ਦ", "ai"): [("ਦੈਂਤ", "dai(n)t"), ("ਦੈਵੀ", "daivee")],
    ("ਦ", "o"):  [("ਦੋ", "do"), ("ਦੋਸਤ", "dost")],
    ("ਦ", "au"): [("ਦੌੜ", "dauR"), ("ਦੌਰ", "daur")],

    # haha ਹ
    ("ਹ", ""):   [("ਹਰ", "har"), ("ਹਨ", "han")],
    ("ਹ", "aa"): [("ਹਾਂ", "haa(n)"), ("ਹਾਥੀ", "haathee"), ("ਹਾਲ", "haal")],
    ("ਹ", "i"):  [("ਹਿੰਦੀ", "hindee"), ("ਹਿਸਾਬ", "hisaab")],
    ("ਹ", "ee"): [("ਹੀ", "hee"), ("ਹੀਰਾ", "heeraa")],
    ("ਹ", "u"):  [("ਹੁਣ", "huN"), ("ਹੁਕਮ", "hukam")],
    ("ਹ", "oo"): [("ਹੂਣ", "hooN"), ("ਹੂਕ", "hook")],
    ("ਹ", "e"):  [("ਹੇਠ", "heTh"), ("ਹੇਰਾ", "heraa")],
    ("ਹ", "ai"): [("ਹੈ", "hai"), ("ਹੈਰਾਨ", "hairaan")],
    ("ਹ", "o"):  [("ਹੋ", "ho"), ("ਹੋਣਾ", "hoNaa"), ("ਹੋਰ", "hor")],
    ("ਹ", "au"): [("ਹੌਲੀ", "haulee"), ("ਹੌਸਲਾ", "hauslaa")],

    # kakka ਕ
    ("ਕ", ""):   [("ਕਰ", "kar"), ("ਕਰਨਾ", "karnaa")],
    ("ਕ", "aa"): [("ਕਾਰ", "kaar"), ("ਕਾਲਾ", "kaalaa"), ("ਕਾਮ", "kaam")],
    ("ਕ", "i"):  [("ਕਿਤਾਬ", "kitaab"), ("ਕਿਸਾਨ", "kisaan")],
    ("ਕ", "ee"): [("ਕੀ", "kee"), ("ਕੀੜਾ", "keeRaa")],
    ("ਕ", "u"):  [("ਕੁਝ", "kujh"), ("ਕੁੜੀ", "kuRee")],
    ("ਕ", "oo"): [("ਕੂੜਾ", "kooRaa"), ("ਕੂਚ", "kooch")],
    ("ਕ", "e"):  [("ਕੇ", "ke"), ("ਕੇਲਾ", "kelaa")],
    ("ਕ", "ai"): [("ਕੈਸਾ", "kaisaa"), ("ਕੈਦ", "kaid")],
    ("ਕ", "o"):  [("ਕੋਈ", "koee"), ("ਕੋਲ", "kol")],
    ("ਕ", "au"): [("ਕੌਣ", "kau(n)"), ("ਕੌਮ", "kaum")],

    # nanna ਨ
    ("ਨ", ""):   [("ਨਹੀਂ", "nahee(n)"), ("ਨਮਕ", "namak")],
    ("ਨ", "aa"): [("ਨਾਮ", "naam"), ("ਨਾਲ", "naal"), ("ਨਾਨੀ", "naanee")],
    ("ਨ", "i"):  [("ਨਿੱਕਾ", "nikkaa"), ("ਨਿਸ਼ਾਨ", "nishaan")],
    ("ਨ", "ee"): [("ਨੀਲਾ", "neelaa"), ("ਨੀਂਦ", "nee(n)d")],
    ("ਨ", "u"):  [("ਨੁਕਸਾਨ", "nuksaan"), ("ਨੁਕਤਾ", "nuktaa")],
    ("ਨ", "oo"): [("ਨੂੰ", "noo(n)"), ("ਨੂਰ", "noor")],
    ("ਨ", "e"):  [("ਨੇ", "ne"), ("ਨੇਕ", "nek")],
    ("ਨ", "ai"): [("ਨੈਣ", "naiN"), ("ਨੈਤਿਕ", "naitik")],
    ("ਨ", "o"):  [("ਨੋਟ", "noT"), ("ਨੋਕ", "nok")],
    ("ਨ", "au"): [("ਨੌਕਰ", "naukar"), ("ਨੌਜਵਾਨ", "naujavaan")],

    # sassa ਸ
    ("ਸ", ""):   [("ਸਭ", "sabh"), ("ਸਰਕਾਰ", "sarkaar")],
    ("ਸ", "aa"): [("ਸਾਲ", "saal"), ("ਸਾਰਾ", "saaraa"), ("ਸਾਫ਼", "saaf")],
    ("ਸ", "i"):  [("ਸਿਰ", "sir"), ("ਸਿੱਖ", "sikkh")],
    ("ਸ", "ee"): [("ਸੀ", "see"), ("ਸੀਮਾ", "seemaa")],
    ("ਸ", "u"):  [("ਸੁੱਖ", "sukkh"), ("ਸੁਣਨਾ", "suNnaa")],
    ("ਸ", "oo"): [("ਸੂਰਜ", "sooraj"), ("ਸੂਚਨਾ", "soochnaa")],
    ("ਸ", "e"):  [("ਸੇਬ", "seb"), ("ਸੇਵਾ", "sevaa")],
    ("ਸ", "ai"): [("ਸੈਨਾ", "sainaa"), ("ਸੈਰ", "sair")],
    ("ਸ", "o"):  [("ਸੋਚ", "soch"), ("ਸੋਨਾ", "sonaa")],
    ("ਸ", "au"): [("ਸੌ", "sau"), ("ਸੌਖਾ", "saukhaa")],

    # mamma ਮ
    ("ਮ", ""):   [("ਮਨ", "man"), ("ਮਰ", "mar")],
    ("ਮ", "aa"): [("ਮਾਂ", "maa(n)"), ("ਮਾਰ", "maar"), ("ਮਾਲਕ", "maalak")],
    ("ਮ", "i"):  [("ਮਿਲ", "mil"), ("ਮਿੱਠਾ", "miThThaa")],
    ("ਮ", "ee"): [("ਮੀਟਰ", "meeTar"), ("ਮੀਂਹ", "mee(n)h")],
    ("ਮ", "u"):  [("ਮੁੰਡਾ", "munDaa"), ("ਮੁਲਕ", "mulak")],
    ("ਮ", "oo"): [("ਮੂੰਹ", "moo(n)h"), ("ਮੂਰਖ", "moorakh")],
    ("ਮ", "e"):  [("ਮੇਰਾ", "meraa"), ("ਮੇਜ਼", "mez")],
    ("ਮ", "ai"): [("ਮੈਂ", "mai(n)"), ("ਮੈਦਾਨ", "maidaan")],
    ("ਮ", "o"):  [("ਮੋਟਾ", "moTaa"), ("ਮੋੜ", "moR")],
    ("ਮ", "au"): [("ਮੌਤ", "maut"), ("ਮੌਸਮ", "mausam")],

    # tatta ਤ
    ("ਤ", ""):   [("ਤੇ", "te"), ("ਤਨ", "tan")],
    ("ਤ", "aa"): [("ਤਾਜ", "taaj"), ("ਤਾਕਤ", "taakat"), ("ਤਾਰਾ", "taaraa")],
    ("ਤ", "i"):  [("ਤਿੰਨ", "tinn"), ("ਤਿੱਖਾ", "tikkhaa")],
    ("ਤ", "ee"): [("ਤੀਰ", "teer"), ("ਤੀਜਾ", "teejaa")],
    ("ਤ", "u"):  [("ਤੁਸੀਂ", "tusee(n)"), ("ਤੁਰਨਾ", "turnaa")],
    ("ਤ", "oo"): [("ਤੂੰ", "too(n)"), ("ਤੂਫ਼ਾਨ", "toofaan")],
    ("ਤ", "e"):  [("ਤੇਰਾ", "teraa"), ("ਤੇਜ਼", "tez")],
    ("ਤ", "ai"): [("ਤੈਨੂੰ", "tainoo(n)"), ("ਤੈਅ", "tai")],
    ("ਤ", "o"):  [("ਤੋਂ", "to(n)"), ("ਤੋਹਫ਼ਾ", "tohfaa")],
    ("ਤ", "au"): [("ਤੌਰ", "taur"), ("ਤੌਬਾ", "taubaa")],

    # pappa ਪ
    ("ਪ", ""):   [("ਪਰ", "par"), ("ਪਰਖ", "parakh")],
    ("ਪ", "aa"): [("ਪਾਣੀ", "paaNee"), ("ਪਾਸੇ", "paase"), ("ਪਾਰ", "paar")],
    ("ਪ", "i"):  [("ਪਿਆਰ", "piaar"), ("ਪਿਤਾ", "pitaa")],
    ("ਪ", "ee"): [("ਪੀਣਾ", "peeNaa"), ("ਪੀਲਾ", "peelaa")],
    ("ਪ", "u"):  [("ਪੁਲਿਸ", "pulis"), ("ਪੁੱਤਰ", "puttar")],
    ("ਪ", "oo"): [("ਪੂਰਾ", "pooraa"), ("ਪੂਜਾ", "poojaa")],
    ("ਪ", "e"):  [("ਪੇਟ", "peT"), ("ਪੇਸ਼", "pesh")],
    ("ਪ", "ai"): [("ਪੈਸਾ", "paisaa"), ("ਪੈਰ", "pair")],
    ("ਪ", "o"):  [("ਪੋਤਾ", "potaa"), ("ਪੋਸਟ", "posT")],
    ("ਪ", "au"): [("ਪੌਣ", "pauN"), ("ਪੌੜੀ", "pauRee")],

    # lalla ਲ
    ("ਲ", ""):   [("ਲਗ", "lag"), ("ਲਖ", "lakh")],
    ("ਲ", "aa"): [("ਲਾਲ", "laal"), ("ਲਾਭ", "laabh"), ("ਲਾਜ਼ਮੀ", "laazmee")],
    ("ਲ", "i"):  [("ਲਿਖਣਾ", "likhNaa"), ("ਲਿਆਉਣਾ", "liaauNaa")],
    ("ਲ", "ee"): [("ਲੀਡਰ", "leeDar"), ("ਲੀਹ", "leeh")],
    ("ਲ", "u"):  [("ਲੁਟ", "luT"), ("ਲੁਕਾਉਣਾ", "lukaauNaa")],
    ("ਲ", "oo"): [("ਲੂਣ", "looN"), ("ਲੂਟ", "looT")],
    ("ਲ", "e"):  [("ਲੇਖ", "lekh"), ("ਲੇਟਣਾ", "leTNaa")],
    ("ਲ", "ai"): [("ਲੈਣਾ", "laiNaa"), ("ਲੈਅ", "lai")],
    ("ਲ", "o"):  [("ਲੋਕ", "lok"), ("ਲੋੜ", "loR")],
    ("ਲ", "au"): [("ਲੌਟਣਾ", "lauTNaa"), ("ਲੌਣ", "lauN")],
}

MUHARNI_CONSONANTS = [
    ("ਰ", "rara"),
    ("ਦ", "dadda"),
    ("ਹ", "haha"),
    ("ਕ", "kakka"),
    ("ਨ", "nanna"),
    ("ਸ", "sassa"),
    ("ਮ", "mamma"),
    ("ਤ", "tatta"),
    ("ਪ", "pappa"),
    ("ਲ", "lalla"),
]


# ---------------------------------------------------------------------------
# Subdeck 3: Conjuncts and tone
# ---------------------------------------------------------------------------
# (front, glyph, roman, note)
CONJUNCTS = [
    # 3 form cards
    ("੍ਰ",
     "੍ਰ",
     "pair rara",
     "Subjoined ਰ. Attaches under a base consonant to form a cluster like "
     "/Cr/. Example: ਪ੍ਰ = /pr/. Common in Sanskritic/tatsama vocabulary "
     "(ਪ੍ਰਧਾਨ, ਪ੍ਰੋਗਰਾਮ). In colloquial pronunciation often realised as "
     "/Cər/ with a faint schwa."),

    ("੍ਹ",
     "੍ਹ",
     "pair haha",
     "Subjoined ਹ. Critically, this is the tone marker of modern Punjabi: "
     "it does NOT add an /h/ sound to the cluster. Instead, ੍ਹ AFTER a "
     "consonant marks LOW TONE on the syllable. Example: ਪੜ੍ਹਨਾ = paRhnaa "
     "(low tone) — the /h/ is silent. Word-initial ਹ-row consonants (ਘ ਝ "
     "ਢ ਧ ਭ) do the same job for plain syllables."),

    ("੍ਵ",
     "੍ਵ",
     "pair vavva",
     "Subjoined ਵ. Forms /Cv/ clusters in Sanskritic loans (ਸ੍ਵਰ, ਸ੍ਵਾਮੀ). "
     "Increasingly rare in modern written Punjabi — usually unwound to "
     "ਵ separately."),

    # Example word cards
    ("ਪ੍ਰਧਾਨ", "ਪ੍ਰਧਾਨ", "pardhaan",
     "Subjoined ੍ਰ on ਪ: /pr/ cluster. The ਧ in the second syllable is "
     "historically a voiced aspirate and triggers low tone in modern "
     "Punjabi, so the second syllable is /tàan/ — but in this learned "
     "Sanskritic word many speakers preserve a closer-to-standard "
     "pronunciation."),
    ("ਪ੍ਰਬੰਧ", "ਪ੍ਰਬੰਧ", "parbandh",
     "Subjoined ੍ਰ on ਪ. The final ਧ marks low tone on the last "
     "syllable; the tippi ੰ before it nasalizes."),
    ("ਪ੍ਰੋਗਰਾਮ", "ਪ੍ਰੋਗਰਾਮ", "program",
     "Subjoined ੍ਰ on ਪ, plus hora matra. English borrowing — read "
     "almost exactly as 'program'."),
    ("ਪ੍ਰੇਮ", "ਪ੍ਰੇਮ", "prem",
     "Subjoined ੍ਰ on ਪ + lavan ੇ. Common in proper names."),
    ("ਪ੍ਰਾਰਥਨਾ", "ਪ੍ਰਾਰਥਨਾ", "praarthnaa",
     "Subjoined ੍ਰ on ਪ + kanna ਾ. Tatsama Sanskritic word."),
    ("ਕ੍ਰਾਂਤੀ", "ਕ੍ਰਾਂਤੀ", "kraa(n)tee",
     "Subjoined ੍ਰ on ਕ + kanna + bindi. /kr/ cluster word-initially is "
     "characteristic of Sanskritic loans."),
    ("ਸ੍ਰੀ", "ਸ੍ਰੀ", "sree",
     "Subjoined ੍ਰ on ਸ + bihari. Honorific 'Sri', read as a /sr/ "
     "cluster."),

    ("ਪੜ੍ਹਨਾ", "ਪੜ੍ਹਨਾ", "paRhnaa",
     "Subjoined ੍ਹ after retroflex ੜ marks LOW TONE on the syllable. "
     "Critically, the /h/ is NOT pronounced as aspiration — it is the "
     "tone marker itself. So the word is /pə̀ɽ.naː/, not "
     "/paɽh.naː/."),
    ("ਚੜ੍ਹਨਾ", "ਚੜ੍ਹਨਾ", "chaRhnaa",
     "Subjoined ੍ਹ after ੜ marks low tone. /tʃə̀ɽ.naː/. The /h/ is "
     "silent but the tone is the give-away that you're saying 'chaRhnaa' "
     "and not 'chaRnaa'."),
    ("ਮਿਹਨਤ", "ਮਿਹਨਤ", "mihnat",
     "Plain ਹ between vowels — note: written separately, not subjoined. "
     "Marks high tone in colloquial speech for the preceding syllable."),
    ("ਨ੍ਹਾਉਣਾ", "ਨ੍ਹਾਉਣਾ", "nhaauNaa",
     "Subjoined ੍ਹ on ਨ at the start of a word marks low tone on the "
     "syllable. Word-initial behaviour of ੍ਹ."),
    ("ਮੀਂਹ", "ਮੀਂਹ", "mee(n)h",
     "Word-final ਹ after a long nasal vowel. The /h/ surfaces as high "
     "tone in modern Punjabi."),
    ("ਕੱਲ੍ਹ", "ਕੱਲ੍ਹ", "kallh (high-tone)",
     "Addak + subjoined haha together. The final ੍ਹ raises tone on the "
     "geminated /ll/. Common word for 'yesterday/tomorrow'."),
    ("ਸ੍ਵਾਮੀ", "ਸ੍ਵਾਮੀ", "svaamee",
     "Subjoined ੍ਵ on ਸ — /sv/ cluster. Sanskritic loan."),
    ("ਸ੍ਵੈ", "ਸ੍ਵੈ", "svai",
     "Subjoined ੍ਵ on ਸ + dulavan ੈ. Tatsama. 'Self-' in compounds."),
    ("ਪ੍ਰਸ਼ਨ", "ਪ੍ਰਸ਼ਨ", "prashan",
     "Subjoined ੍ਰ on ਪ, then dotted ਸ਼ /ʃ/. Note the cluster + dotted "
     "letter combination."),
    ("ਪ੍ਰੋਫ਼ੈਸਰ", "ਪ੍ਰੋਫ਼ੈਸਰ", "professar",
     "English borrowing with subjoined ੍ਰ on ਪ + dotted ਫ਼ /f/. Common "
     "news-register word."),
    ("ਸ੍ਰੋਤ", "ਸ੍ਰੋਤ", "srot",
     "Subjoined ੍ਰ on ਸ + hora. /sr/ cluster. 'Source' (Sanskritic)."),
]


# ---------------------------------------------------------------------------
# Subdeck 4: Top 100 sight words
# ---------------------------------------------------------------------------
# (word, roman, pos, note)
SIGHT_WORDS = [
    # ---- Postpositions (the densest class in any Punjabi text) -------------
    ("ਦੇ", "de", "postposition (genitive, masc. pl. / oblique)",
     "Marks possession when the possessed noun is masculine plural or in "
     "an oblique case. Always follows the possessor noun. Compare ਦਾ "
     "(masc. sg.) and ਦੀ (fem.)."),
    ("ਦੀ", "dee", "postposition (genitive, fem.)",
     "Marks possession when the possessed noun is feminine. Agrees with "
     "the possessed item, not the possessor."),
    ("ਦਾ", "daa", "postposition (genitive, masc. sg. nominative)",
     "Marks possession when the possessed noun is masculine singular and "
     "in the nominative. Follows the possessor."),
    ("ਨੂੰ", "noo(n)", "postposition (dative / accusative)",
     "Marks the indirect object, and the direct object of a transitive "
     "verb in the perfective aspect. Always follows the noun it governs. "
     "Often fuses with pronouns: ਮੈਨੂੰ, ਤੈਨੂੰ, ਉਹਨੂੰ."),
    ("ਨੇ", "ne", "postposition (ergative)",
     "Marks the subject of a transitive verb in the perfective aspect. "
     "Required for 'I read the book' constructions in past tense. "
     "Pronoun fusions: ਮੈਂ + ਨੇ ('I' as agent)."),
    ("ਤੋਂ", "to(n)", "postposition (ablative)",
     "Means 'from' — source, origin, point of departure. Also used in "
     "comparisons ('more than X') and with passive agents."),
    ("ਨਾਲ", "naal", "postposition (comitative / instrumental)",
     "Means 'with'. Marks accompaniment ('with friends') and instrument "
     "('with a knife'). Follows the noun."),
    ("ਵਿੱਚ", "vichch", "postposition (locative)",
     "Means 'in / inside'. Follows the noun. Often written ਵਿਚ without "
     "the addak — pronunciation is the same."),
    ("ਤੇ", "te", "postposition / conjunction",
     "Two distinct words spelled the same: (1) postposition 'on / at' "
     "after a noun, (2) conjunction 'and' between clauses or noun "
     "phrases. Context disambiguates."),
    ("ਕੋਲ", "kol", "postposition (proximative)",
     "Means 'near / with (in possession)'. Used for inalienable "
     "possession: 'X ਕੋਲ Y ਹੈ' = 'X has Y'."),
    ("ਲਈ", "laee", "postposition (benefactive)",
     "Means 'for'. Marks purpose, recipient, or benefactor."),
    ("ਵੱਲ", "vall", "postposition (directional)",
     "Means 'towards'. Marks direction of motion or attention."),
    ("ਬਾਰੇ", "baare", "postposition",
     "Means 'about / concerning', usually 'X ਦੇ ਬਾਰੇ'. Marks topic."),

    # ---- Copula and auxiliaries -------------------------------------------
    ("ਹੈ", "hai", "verb (be, 3rd sg. present)",
     "Present tense copula for 3rd person singular subjects: 'is'. "
     "Highest-frequency verb form in Punjabi."),
    ("ਹਨ", "han", "verb (be, 3rd pl. present)",
     "Present tense copula for 3rd person plural subjects: 'are'. "
     "Often also used as a polite singular."),
    ("ਹਾਂ", "haa(n)", "verb (be, 1st sg./pl. present)",
     "Present tense copula for 1st person ('I am', 'we are'). Also an "
     "independent word meaning 'yes' — context disambiguates."),
    ("ਹੋ", "ho", "verb (be, 2nd pl. present)",
     "Present tense copula for 2nd person plural/formal ('you are'). "
     "Also the root of the verb ਹੋਣਾ 'to be / to become'."),
    ("ਸੀ", "see", "verb (be, 3rd sg. past)",
     "Past tense copula for 3rd person singular: 'was'."),
    ("ਸਨ", "san", "verb (be, 3rd pl. past)",
     "Past tense copula for 3rd person plural: 'were'."),
    ("ਹੋਇਆ", "hoiaa", "verb (be, perfective)",
     "Perfective participle of ਹੋਣਾ ('happened / became'). Also forms "
     "compound past tenses."),
    ("ਗਿਆ", "giaa", "verb (go, perfective masc. sg.)",
     "Perfective of ਜਾਣਾ. Also the standard passive auxiliary ('was "
     "done') and the 'unintentional/completed' light verb."),
    ("ਗਏ", "gae", "verb (go, perfective masc. pl.)",
     "Plural perfective of ਜਾਣਾ. Used as auxiliary just like ਗਿਆ."),
    ("ਗਈ", "gaee", "verb (go, perfective fem. sg.)",
     "Feminine perfective of ਜਾਣਾ."),
    ("ਰਿਹਾ", "rihaa", "verb auxiliary (continuous, masc. sg.)",
     "Continuous-aspect auxiliary: 'X is doing'. Combines with verb stem "
     "+ ਹੈ (ਕਰ ਰਿਹਾ ਹੈ = 'is doing')."),
    ("ਰਹੀ", "rahee", "verb auxiliary (continuous, fem.)",
     "Feminine continuous auxiliary. ਕਰ ਰਹੀ ਹੈ = '(she) is doing'."),
    ("ਰਹੇ", "rahe", "verb auxiliary (continuous, masc. pl.)",
     "Plural masculine continuous auxiliary."),

    # ---- High-frequency verb roots / common verb forms --------------------
    ("ਕਰ", "kar", "verb (do, root)",
     "Root of the verb ਕਰਨਾ 'to do/make'. The most productive verb in "
     "Punjabi — used in hundreds of light-verb constructions (X ਕਰਨਾ)."),
    ("ਕੀਤਾ", "keetaa", "verb (do, perfective masc. sg.)",
     "Perfective of ਕਰਨਾ: 'did/made'. Suppletive — formed from a "
     "different root than ਕਰ."),
    ("ਕਰਦਾ", "kardaa", "verb (do, imperfective masc. sg.)",
     "Imperfective participle: 'does / is doing (habitually)'. Combines "
     "with ਹੈ for present habitual."),
    ("ਹੋਣਾ", "hoNaa", "verb (be, infinitive)",
     "Infinitive of 'to be / to become'. Also a noun: 'being'."),
    ("ਜਾਣਾ", "jaaNaa", "verb (go, infinitive)",
     "Infinitive of 'to go'. Also the passive auxiliary in compounds."),
    ("ਆਉਣਾ", "aauNaa", "verb (come, infinitive)",
     "Infinitive of 'to come'. Also used impersonally for 'to know how': "
     "ਮੈਨੂੰ ਆਉਂਦਾ ਹੈ = 'I know how to'."),
    ("ਦੇਣਾ", "deNaa", "verb (give, infinitive)",
     "Infinitive of 'to give'. Also a benefactive light verb (X ਦੇਣਾ = "
     "'do X for someone')."),
    ("ਲੈਣਾ", "laiNaa", "verb (take, infinitive)",
     "Infinitive of 'to take'. Also a self-benefactive light verb."),
    ("ਕਹਿਣਾ", "kahiNaa", "verb (say, infinitive)",
     "Infinitive of 'to say'. ਕਹਿ is the bare stem; the ਹਿ marks high "
     "tone on the syllable."),
    ("ਸਕਣਾ", "sakNaa", "verb (be able, modal)",
     "Modal verb 'to be able'. Follows the bare stem: ਕਰ ਸਕਣਾ = 'to be "
     "able to do'."),
    ("ਚਾਹੀਦਾ", "chaaheedaa", "verb (be needed/should)",
     "Impersonal verb 'should / ought'. Construction: 'X ਨੂੰ Y ਚਾਹੀਦਾ "
     "ਹੈ' = 'X needs Y'."),

    # ---- Pronouns ---------------------------------------------------------
    ("ਮੈਂ", "mai(n)", "pronoun (1st sg.)",
     "'I'. Nominative case. Note the bindi — the vowel is nasalized."),
    ("ਅਸੀਂ", "asee(n)", "pronoun (1st pl.)",
     "'We'. Nominative case."),
    ("ਤੂੰ", "too(n)", "pronoun (2nd sg., informal)",
     "'You' (informal singular). Used for children, close friends, and "
     "(carefully) intimates. Bindi-nasalized."),
    ("ਤੁਸੀਂ", "tusee(n)", "pronoun (2nd pl. / formal sg.)",
     "'You' (plural or polite singular). Default polite form."),
    ("ਉਹ", "uh", "pronoun (3rd / demonstrative, distal)",
     "'He / she / it / that / those'. Used for both 3rd person personal "
     "reference and distal demonstrative."),
    ("ਇਹ", "ih", "pronoun (3rd / demonstrative, proximal)",
     "'He / she / it / this / these'. Proximal counterpart to ਉਹ."),
    ("ਉਸ", "us", "pronoun (oblique of ਉਹ, sg.)",
     "Oblique form of ਉਹ: used before postpositions in the singular. "
     "ਉਹ + ਨੇ → ਉਸ ਨੇ; ਉਹ + ਨੂੰ → ਉਸ ਨੂੰ (often written ਉਸਨੂੰ)."),
    ("ਇਸ", "is", "pronoun (oblique of ਇਹ, sg.)",
     "Oblique form of ਇਹ. Used before postpositions in the singular."),
    ("ਉਨ੍ਹਾਂ", "unhaa(n)", "pronoun (oblique of ਉਹ, pl.)",
     "Oblique plural of ਉਹ. Note the subjoined ੍ਹ marking low tone."),
    ("ਇਨ੍ਹਾਂ", "inhaa(n)", "pronoun (oblique of ਇਹ, pl.)",
     "Oblique plural of ਇਹ."),
    ("ਮੇਰਾ", "meraa", "pronoun (possessive, 1st sg., masc. sg.)",
     "'My' agreeing with masculine singular possessed noun. Inflects: "
     "ਮੇਰੀ (fem.), ਮੇਰੇ (masc. pl./oblique)."),
    ("ਤੁਹਾਡਾ", "tuhaaDaa", "pronoun (possessive, 2nd pl.)",
     "'Your' (polite/plural). Inflects like ਮੇਰਾ."),
    ("ਆਪਣਾ", "aapNaa", "pronoun (reflexive possessive)",
     "Reflexive possessive: 'one's own'. Used when the possessor is the "
     "subject. ਮੈਂ ਆਪਣਾ ਕੰਮ ਕੀਤਾ = 'I did my (own) work'."),

    # ---- Interrogatives ---------------------------------------------------
    ("ਕੀ", "kee", "interrogative pronoun",
     "'What'. Also a yes/no question marker placed before a clause."),
    ("ਕੌਣ", "kauN", "interrogative pronoun",
     "'Who'. Used for human referents. Oblique form: ਕਿਸ."),
    ("ਕਿੱਥੇ", "kitthe", "interrogative adverb",
     "'Where'. Locative interrogative."),
    ("ਕਦੋਂ", "kado(n)", "interrogative adverb",
     "'When'. Temporal interrogative."),
    ("ਕਿਉਂ", "kio(n)", "interrogative adverb",
     "'Why'. Causal interrogative."),
    ("ਕਿਵੇਂ", "kive(n)", "interrogative adverb",
     "'How'. Manner interrogative."),
    ("ਕਿੰਨਾ", "kinnaa", "interrogative adjective",
     "'How much / how many'. Agrees with the noun: ਕਿੰਨੀ (fem.), ਕਿੰਨੇ "
     "(pl.)."),
    ("ਕਿਹੜਾ", "kihRaa", "interrogative adjective",
     "'Which'. Agrees with the noun. Note the retroflex ੜ."),

    # ---- Conjunctions and particles ---------------------------------------
    ("ਅਤੇ", "ate", "conjunction",
     "'And'. The formal/written 'and'. In casual writing ਤੇ often "
     "replaces it."),
    ("ਜਾਂ", "jaa(n)", "conjunction",
     "'Or'. Coordinator for alternatives. The bindi nasalizes."),
    ("ਪਰ", "par", "conjunction",
     "'But'. Adversative coordinator."),
    ("ਕਿਉਂਕਿ", "kio(n)ki", "conjunction",
     "'Because'. Causal subordinator. Compound of ਕਿਉਂ + ਕਿ."),
    ("ਜੇ", "je", "conjunction",
     "'If'. Conditional subordinator. Often paired with ਤਾਂ 'then'."),
    ("ਤਾਂ", "taa(n)", "conjunction / particle",
     "'Then' (in if-then), also a topic / emphasis particle. Highly "
     "polysemous — context decides."),
    ("ਜੋ", "jo", "relative pronoun",
     "'Who / which / that'. Introduces relative clauses. Usually paired "
     "with a correlative (ਉਹ, ਇਹ)."),
    ("ਕਿ", "ki", "complementizer / conjunction",
     "'That' — introduces complement clauses ('I said that...'). Also "
     "'or' in some questions."),
    ("ਹੀ", "hee", "particle (emphatic / restrictive)",
     "'Only / just / exactly'. Follows the word it emphasizes. ਉਹ ਹੀ "
     "= 'he himself / only he'."),
    ("ਵੀ", "vee", "particle (additive)",
     "'Also / too / even'. Follows the word it adds. ਉਹ ਵੀ ਆਇਆ = 'He "
     "too came'."),
    ("ਨਹੀਂ", "nahee(n)", "negative particle",
     "'No / not'. The standard sentence negator. Note the bindi "
     "nasalization."),
    ("ਨਾ", "naa", "negative particle (subjunctive/imperative)",
     "'Not' — used with imperatives and subjunctives, where ਨਹੀਂ would "
     "be ungrammatical. Also 'isn't it?' as a tag question."),
    ("ਫਿਰ", "phir", "adverb",
     "'Then / again'. Both sequential ('then X happened') and "
     "repetitive ('once again')."),
    ("ਹੁਣ", "huN", "adverb",
     "'Now'. Temporal. Note the retroflex ਣ."),
    ("ਅੱਜ", "ajj", "adverb",
     "'Today'. Note the addak: read with a geminated /jj/."),
    ("ਕੱਲ੍ਹ", "kallh", "adverb",
     "'Yesterday' or 'tomorrow' — Punjabi uses one word for both; tense "
     "disambiguates. Note the addak (gemination) and subjoined ੍ਹ (high "
     "tone)."),
    ("ਇੱਥੇ", "itthe", "adverb",
     "'Here'. Proximal locative. Addak geminates the /tt/."),
    ("ਉੱਥੇ", "utthe", "adverb",
     "'There'. Distal locative."),
    ("ਬਹੁਤ", "bahut", "adverb / quantifier",
     "'Very / much / many'. Intensifier before adjectives, quantifier "
     "before nouns."),

    # ---- Numerals & quantifiers -------------------------------------------
    ("ਇੱਕ", "ikk", "numeral / indefinite article",
     "'One' — and also the closest Punjabi gets to an indefinite "
     "article ('a/an'). Addak geminates /kk/."),
    ("ਦੋ", "do", "numeral",
     "'Two'."),
    ("ਸਭ", "sabh", "quantifier",
     "'All / every'. Universal quantifier."),
    ("ਸਾਰਾ", "saaraa", "quantifier",
     "'Whole / entire'. Agrees with the noun: ਸਾਰੀ (fem.), ਸਾਰੇ (pl.)."),
    ("ਕੁਝ", "kujh", "quantifier",
     "'Some / something'. Indefinite. Note: not nasalized in Punjabi "
     "(unlike Hindi कुछ)."),
    ("ਕੋਈ", "koee", "indefinite pronoun",
     "'Someone / any'. Animate-leaning indefinite."),
    ("ਹਰ", "har", "quantifier",
     "'Every'. Pre-nominal. ਹਰ ਆਦਮੀ = 'every man'."),
    ("ਹੋਰ", "hor", "quantifier / adjective",
     "'More / other / another'."),

    # ---- High-frequency content words for news -----------------------------
    ("ਆਦਮੀ", "aadmee", "noun (masc.)",
     "Common content word; appears across registers."),
    ("ਔਰਤ", "aurat", "noun (fem.)",
     "Common content word. Begins with kanaura ੌ."),
    ("ਲੋਕ", "lok", "noun (masc., usually pl.)",
     "Mass plural 'people'. Takes plural agreement."),
    ("ਦੇਸ਼", "desh", "noun (masc.)",
     "High-frequency in news: 'country'. Note dotted ਸ਼."),
    ("ਸਰਕਾਰ", "sarkaar", "noun (fem.)",
     "High-frequency in news: 'government'."),
    ("ਸਾਲ", "saal", "noun (masc.)",
     "'Year' — temporal unit."),
    ("ਦਿਨ", "din", "noun (masc.)",
     "'Day'."),
    ("ਸਮਾਂ", "samaa(n)", "noun (masc.)",
     "'Time'. The bindi nasalizes the final long /aa/."),
    ("ਘਰ", "ghar", "noun (masc.)",
     "'House / home'. Note: ਘ marks low tone in modern Punjabi, so this "
     "is read with low tone on the syllable."),
    ("ਕੰਮ", "kamm", "noun (masc.)",
     "'Work / task'. Tippi + geminated /mm/."),
    ("ਗੱਲ", "gall", "noun (fem.)",
     "'Talk / matter / thing-said'. Extremely common in news quotes and "
     "narration."),
    ("ਨਾਮ", "naam", "noun (masc.)",
     "'Name'."),
    ("ਪਾਣੀ", "paaNee", "noun (masc.)",
     "'Water'. Retroflex ਣ."),
    ("ਭਾਰਤ", "bhaarat", "proper noun",
     "'India'. Note ਭ — historical voiced aspirate, marks low tone on "
     "the first syllable."),
    ("ਪੰਜਾਬ", "panjaab", "proper noun",
     "'Punjab'. Tippi nasalizes the first vowel."),
]


# ---------------------------------------------------------------------------
# Build the decks
# ---------------------------------------------------------------------------
def build():
    # Parent deck (Anki creates subdecks from "Parent::Child" names).
    parent = genanki.Deck(TOP_DECK_ID, "Punjabi")

    letters_deck = genanki.Deck(LETTERS_DECK_ID, "Punjabi::1-Letters")
    muharni_deck = genanki.Deck(MUHARNI_DECK_ID, "Punjabi::2-Muharni")
    conjuncts_deck = genanki.Deck(CONJUNCTS_DECK_ID, "Punjabi::3-Conjuncts")
    sight_deck = genanki.Deck(SIGHT_DECK_ID, "Punjabi::4-Sight-Words")

    # ----- Letters ---------------------------------------------------------
    for glyph, name, exemplar, exemplar_rom, note, category in LETTERS:
        note_obj = genanki.Note(
            model=letters_model,
            fields=[glyph, name, exemplar, exemplar_rom, note, category],
            tags=[f"category::{category}"],
        )
        letters_deck.add_note(note_obj)

    # ----- Muharni ---------------------------------------------------------
    for cons, cons_name in MUHARNI_CONSONANTS:
        for matra_char, matra_name, roman_suffix, is_mukta in MATRAS:
            syllable = cons if is_mukta else cons + matra_char

            # Romanization: consonant base (drop the "a" from cons_name like
            # "kakka" → "k") + roman suffix; mukta = base + "a".
            cons_base = {
                "ਰ": "r", "ਦ": "d", "ਹ": "h", "ਕ": "k", "ਨ": "n",
                "ਸ": "s", "ਮ": "m", "ਤ": "t", "ਪ": "p", "ਲ": "l",
            }[cons]
            if is_mukta:
                roman = cons_base + "a"
                pairing = (
                    f"{cons_name} alone (mukta). Every base consonant "
                    f"carries an inherent /a/ when written without a "
                    f"matra. Word-finally this /a/ is usually dropped."
                )
            else:
                roman = cons_base + roman_suffix
                pairing = (
                    f"{cons_name} + {matra_name} ({matra_char}). "
                    f"Reads /{roman}/."
                )

            examples = MUHARNI_EXAMPLES[(cons, roman_suffix if not is_mukta else "")]
            examples_html = "".join(
                f'<div class="examples-row">'
                f'<span class="pa">{pa}</span>'
                f'<span class="rom">{rom}</span>'
                f'</div>'
                for pa, rom in examples
            )

            note_obj = genanki.Note(
                model=muharni_model,
                fields=[syllable, roman, pairing, examples_html],
                tags=[f"consonant::{cons_name}", f"matra::{matra_name}"],
            )
            muharni_deck.add_note(note_obj)

    # ----- Conjuncts -------------------------------------------------------
    for front, glyph, roman, note in CONJUNCTS:
        # Tag forms differently from example words.
        is_form = roman.startswith("pair ")
        tag = "conjunct::form" if is_form else "conjunct::example"
        note_obj = genanki.Note(
            model=conjuncts_model,
            fields=[front, glyph, roman, note],
            tags=[tag],
        )
        conjuncts_deck.add_note(note_obj)

    # ----- Sight words -----------------------------------------------------
    for word, roman, pos, note in SIGHT_WORDS:
        note_obj = genanki.Note(
            model=sight_model,
            fields=[word, roman, pos, note],
            tags=[f"pos::{pos.split(' ')[0].lower()}"],
        )
        sight_deck.add_note(note_obj)

    # Package all four subdecks together.
    package = genanki.Package([
        letters_deck,
        muharni_deck,
        conjuncts_deck,
        sight_deck,
    ])
    out_path = "Punjabi_Reading.apkg"
    package.write_to_file(out_path)

    # ----- Report ----------------------------------------------------------
    decks_report = [
        ("Punjabi::1-Letters", len(letters_deck.notes)),
        ("Punjabi::2-Muharni", len(muharni_deck.notes)),
        ("Punjabi::3-Conjuncts", len(conjuncts_deck.notes)),
        ("Punjabi::4-Sight-Words", len(sight_deck.notes)),
    ]
    file_size = os.path.getsize(out_path)

    print("=" * 60)
    print("Punjabi_Reading.apkg built")
    print("=" * 60)
    for name, count in decks_report:
        print(f"  {name:30s} {count:4d} cards")
    print(f"  {'TOTAL':30s} {sum(c for _, c in decks_report):4d} cards")
    print(f"  File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print()

    # Three sample cards.
    print("=" * 60)
    print("SAMPLE CARDS (plain-text preview)")
    print("=" * 60)

    samples = [
        ("Letters",
         f"FRONT: {LETTERS[3][0]}\n"
         f"BACK:\n"
         f"  Glyph: {LETTERS[3][0]}\n"
         f"  Name:  {LETTERS[3][1]}\n"
         f"  Exemplar: {LETTERS[3][2]}  ({LETTERS[3][3]})\n"
         f"  Note:  {LETTERS[3][4]}\n"
         f"  Tag:   category::{LETTERS[3][5]}"),

        ("Muharni",
         f"FRONT: ਕਾ\n"
         f"BACK:\n"
         f"  Syllable: ਕਾ\n"
         f"  Roman:    kaa\n"
         f"  Pairing:  kakka + kanna (ਾ). Reads /kaa/.\n"
         f"  Examples: " + ", ".join(
             f"{w} ({r})" for w, r in MUHARNI_EXAMPLES[("ਕ", "aa")])),

        ("Conjuncts (pair haha)",
         f"FRONT: {CONJUNCTS[1][0]}\n"
         f"BACK:\n"
         f"  Glyph: {CONJUNCTS[1][1]}\n"
         f"  Roman: {CONJUNCTS[1][2]}\n"
         f"  Note:  {CONJUNCTS[1][3]}"),
    ]
    for label, body in samples:
        print(f"\n--- {label} ---")
        print(body)

    # Import instructions.
    print()
    print("=" * 60)
    print("IMPORT INSTRUCTIONS")
    print("=" * 60)
    print(textwrap.dedent("""\
        AnkiMobile (iOS):
          1. Email or AirDrop Punjabi_Reading.apkg to your iPhone/iPad.
          2. Tap the attachment and choose "Copy to AnkiMobile".
          3. Anki opens and imports automatically. The four subdecks
             appear under "Punjabi" in the deck list.
          4. To verify Gurmukhi rendering, open any card. If glyphs show
             as boxes, install the "Noto Sans Gurmukhi" font system-wide
             (Settings -> General -> Fonts) and restart AnkiMobile.

        AnkiDroid (Android):
          1. Transfer Punjabi_Reading.apkg to your device (USB, email,
             Drive, etc.).
          2. In AnkiDroid, tap the menu (three dots) -> Import -> select
             the .apkg file.
          3. AnkiDroid imports all four subdecks under "Punjabi".
          4. For best Gurmukhi rendering, install Google's Noto Sans
             Gurmukhi font via the Play Store font manager, or use a ROM
             font that includes Gurmukhi (most modern Androids ship one).

        Anki Desktop (for review/edit):
          1. File -> Import -> select Punjabi_Reading.apkg.
          2. Edit notes freely; re-imports of the same .apkg update
             existing notes thanks to fixed deck and model IDs.
    """))


if __name__ == "__main__":
    build()
