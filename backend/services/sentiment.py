"""
Lightweight, explainable text analysis for the class chat.

This is deliberately NOT emotion detection and NOT a judgement of a child.
It only detects a few word patterns so the teacher dashboard can spot a
student who is asking for help.

The result is an optional supporting signal for the feedback engine. Quiz
scores always remain the main evidence.
"""
from __future__ import annotations

import re

from curriculum import TOPIC_BY_SLUG, TOPICS, level_for_class

# Words that suggest a student is finding something difficult.
DIFFICULTY_PHRASES = [
    "not understanding",
    "don't understand",
    "do not understand",
    "didn't understand",
    "cannot understand",
    "can't understand",
    "not able to",
    "unable to",
    "struggling",
    "stuck",
    "confused",
    "confusing",
    "difficult",
    "hard to",
    "too hard",
    "not clear",
    "unclear",
    "need help",
    "help me",
    "explain again",
    "doubt",
]

POSITIVE_PHRASES = [
    "easy",
    "understood",
    "i understand",
    "got it",
    "enjoyed",
    "fun",
    "interesting",
    "helpful",
    "thank",
    "thanks",
    "improved",
    "scored",
    "correct",
    "better",
]

NEGATIVE_PHRASES = [
    "hate",
    "boring",
    "worst",
    "useless",
    "too much",
    "tired",
    "scared",
    "worried",
    "sad",
]

# Topic detection: reuse the curriculum vocabulary.
KEYWORDS = [
    ("active-passive-voice", ["passive voice", "active voice", "passive", "active"]),
    ("direct-indirect-speech", ["indirect speech", "direct speech", "reported speech"]),
    ("reading-comprehension-secondary", ["main idea", "inference", "comprehension", "passage"]),
    ("reading-comprehension", ["story", "read and answer"]),
    ("basic-writing-skills", ["paragraph", "essay", "letter writing", "topic sentence"]),
    ("sentence-correction", ["correct the sentence", "sentence correction", "double negative"]),
    ("parts-of-speech", ["parts of speech", "noun", "pronoun", "adjective", "adverb", "verb"]),
    ("tenses", ["tense", "past tense", "present tense", "future tense"]),
    ("vocabulary-building", ["synonym", "antonym", "vocabulary", "word meaning"]),
    ("linear-equations", ["linear equation", "solve for x", "equation"]),
    ("ratio-proportion", ["ratio", "proportion"]),
    ("fractions-decimals", ["decimal", "fraction and decimal"]),
    ("basic-statistics", ["mean", "median", "mode", "statistics", "average"]),
    ("percentages", ["percentage", "percent", "discount", "interest"]),
    ("algebra", ["algebra", "expression", "like terms", "expand"]),
    ("geometry", ["geometry", "angle", "triangle", "area", "perimeter", "circle"]),
    ("integers", ["integer", "negative number", "number line"]),
    ("fractions", ["fraction", "numerator", "denominator"]),
    ("multiplication", ["multiplication", "multiply", "times table"]),
    ("division", ["division", "divide", "quotient"]),
    ("addition", ["addition", "add", "sum", "plus"]),
    ("subtraction", ["subtraction", "subtract", "minus", "take away"]),
    ("counting", ["counting", "count", "how many"]),
    ("number-patterns", ["number pattern", "sequence", "missing number"]),
    ("basic-shapes", ["shape", "square", "rectangle", "sides"]),
    ("spelling-practice", ["spelling", "spell", "misspell"]),
    ("articles", ["article", "a or an"]),
    ("alphabet-recognition", ["alphabet", "vowel", "consonant", "letter"]),
    ("basic-vocabulary", ["vocabulary word", "word for", "means"]),
    ("naming-words", ["naming word", "noun"]),
    ("simple-sentences", ["sentence", "capital letter", "full stop", "punctuation"]),
    ("basic-grammar", ["plural", "singular", "grammar"]),
]

# Whole-word matches that are safe to use.
DIFFICULTY_WORDS = {"stuck", "confused", "confusing", "difficult", "struggling", "doubt"}
POSITIVE_WORDS = {"easy", "understood", "enjoyed", "fun", "interesting", "helpful"}
NEGATIVE_WORDS = {"hate", "boring", "useless", "tired", "scared", "worried", "sad"}


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def detect_topic(text: str, class_level: int | None = None):
    """Return (topic slug, readable title) for a chat message, or (None, None)."""
    normalised = _normalise(text)
    if not normalised:
        return None, None

    for topic in TOPICS:
        if topic["title"].lower() in normalised or topic["slug"] in normalised:
            return topic["slug"], topic["title"]

    for slug, words in KEYWORDS:
        for word in words:
            if re.search(rf"\b{re.escape(word)}\b", normalised):
                topic = TOPIC_BY_SLUG.get(slug)
                if topic:
                    return slug, topic["title"]

    if re.search(r"\d+\s*[/+×x*÷-]\s*\d+", normalised):
        return None, "Arithmetic"
    return None, None


def analyze_message(text: str, class_level: int | None = None):
    """
    Return a small, transparent analysis dictionary.

    Keys used elsewhere:
      sentiment             Positive / Neutral / Negative
      learning_difficulty   Possible / Low
      topic                 readable topic or subject title
      subtopic              readable topic title
    """
    normalised = _normalise(text)
    if not normalised:
        return {
            "sentiment": "Neutral",
            "learning_difficulty": "Low",
            "topic": None,
            "subtopic": None,
            "keywords": [],
            "note": "Empty message.",
        }

    words = set(re.findall(r"[a-z']+", normalised))
    difficulty_hits = [
        phrase for phrase in DIFFICULTY_PHRASES if phrase in normalised
    ]
    difficulty_hits += sorted(words & DIFFICULTY_WORDS)
    positive_hits = [
        phrase for phrase in POSITIVE_PHRASES if phrase in normalised
    ] + sorted(words & POSITIVE_WORDS)
    negative_hits = [
        phrase for phrase in NEGATIVE_PHRASES if phrase in normalised
    ] + sorted(words & NEGATIVE_WORDS)

    # A help request should not be read as a negative feeling.
    if difficulty_hits:
        sentiment = "Negative" if negative_hits else "Neutral"
    elif len(positive_hits) > len(negative_hits):
        sentiment = "Positive"
    elif negative_hits and not positive_hits:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    slug, title = detect_topic(normalised, class_level)
    topic = TOPIC_BY_SLUG.get(slug) if slug else None

    keywords = sorted(set(difficulty_hits + positive_hits + negative_hits))
    return {
        "sentiment": sentiment,
        "learning_difficulty": "Possible" if difficulty_hits else "Low",
        "topic_slug": slug,
        "topic": (topic or {}).get("subject") or title,
        "subtopic": (topic or {}).get("title") or title,
        "keywords": keywords[:8],
        "note": (
            "This is a rough text signal from a few word patterns. It is not "
            "emotion detection and it never changes a learner's quiz grade."
        ),
    }
