"""
Rule-based learning assistant for IAFS.

The assistant is intentionally simple and explainable:
  * It never calls a paid AI API, so the demo works offline.
  * It never reveals a quiz answer. It explains the method and gives a
    similar worked example instead.
  * Every explanation is rewritten for Primary (Classes 1-5) or
    Secondary (Classes 6-10) learners.

The route layer only needs `build_reply(message, class_level, topic_slug)`.
"""
from __future__ import annotations

import re

from curriculum import TOPIC_BY_SLUG, TOPICS, level_for_class

# ---------------------------------------------------------------------------
# Friendly per-topic coaching notes
# ---------------------------------------------------------------------------
# `remember` is the one line we want a child to walk away with.
# `steps` are the method, in order, never the answer to a live quiz question.
# `example` is always a *different* worked example from the quiz generator.
TOPIC_HINTS = {
    # Primary English
    "alphabet-recognition": {
        "remember": "The English alphabet has 26 letters, and A, E, I, O, U are vowels.",
        "steps": [
            "Say the alphabet slowly and point to each letter.",
            "For 'before' or 'after', find the letter in the alphabet first.",
            "Then step one place left for before, or one place right for after.",
        ],
        "example": "N comes after M and before O.",
    },
    "basic-vocabulary": {
        "remember": "Vocabulary means the words you know and can use.",
        "steps": [
            "Read the whole sentence, not just the blank.",
            "Picture the meaning in your head.",
            "Choose the word that fits the meaning.",
        ],
        "example": "'Enormous' means very big, so 'tiny' is its opposite.",
    },
    "naming-words": {
        "remember": "A naming word (noun) names a person, place, animal or thing.",
        "steps": [
            "Ask: who or what is this word talking about?",
            "Check if it is a person, place, animal or thing.",
            "Action words like run or sing are verbs, not nouns.",
        ],
        "example": "In 'The girl feeds the cat', 'girl' and 'cat' are naming words.",
    },
    "articles": {
        "remember": "Use 'a' before a consonant sound, 'an' before a vowel sound and 'the' for one specific thing.",
        "steps": [
            "Say the word after the blank out loud.",
            "If it starts with a vowel sound (a, e, i, o, u), use 'an'.",
            "If it starts with any other sound, use 'a'.",
            "Use 'the' when everyone knows exactly which one you mean.",
        ],
        "example": "an orange, a pencil, the moon.",
    },
    "simple-sentences": {
        "remember": "A sentence needs a subject, a verb and a capital letter plus an end mark.",
        "steps": [
            "Find who or what the sentence is about.",
            "Find the action word.",
            "Check the capital letter at the start.",
            "Check the full stop, question mark or exclamation mark at the end.",
        ],
        "example": "'The dog runs.' is a sentence because it has a subject (dog) and a verb (runs).",
    },
    "basic-grammar": {
        "remember": "Plurals often add -s or -es, and the verb must match the noun.",
        "steps": [
            "Decide if the noun is singular (one) or plural (more than one).",
            "For plurals, add -s, or -es after sh, ch, s, x or z.",
            "Use 'is' with one thing and 'are' with many things.",
        ],
        "example": "one box → two boxes; the box is heavy → the boxes are heavy.",
    },
    "reading-comprehension": {
        "remember": "Read the question first, then look back in the story for the answer.",
        "steps": [
            "Read the passage once to understand the story.",
            "Read the question and find its key words.",
            "Look for the sentence in the passage that matches.",
            "Say your answer in a full sentence.",
        ],
        "example": "If the question asks 'Where?', look for a place word such as park, school or home.",
    },
    "spelling-practice": {
        "remember": "Say the word slowly, listen to each sound and look for a pattern.",
        "steps": [
            "Break the word into small parts.",
            "Say each part aloud.",
            "Look for a word family, such as light, night and bright.",
            "Write it three times, then cover it and try from memory.",
        ],
        "example": "'Because' is easier as be-cause, and 'beautiful' as beau-ti-ful.",
    },
    # Primary Mathematics
    "counting": {
        "remember": "Say one number for each object, and the last number is the total.",
        "steps": [
            "Point to one object at a time.",
            "Say a number for each object.",
            "The last number you say is how many there are.",
            "For patterns, find how much you add or subtract each time.",
        ],
        "example": "⭐ ⭐ ⭐ ⭐ → 1, 2, 3, 4, so there are 4 stars.",
    },
    "addition": {
        "remember": "Addition finds the total. The answer is called the sum.",
        "steps": [
            "Start with the larger number.",
            "Count on the smaller number.",
            "Add the ones first, then the tens.",
            "Check your answer by adding in the opposite order.",
        ],
        "example": "8 + 5: start at 8 and count on 5 → 9, 10, 11, 12, 13.",
    },
    "subtraction": {
        "remember": "Subtraction finds what is left or the difference.",
        "steps": [
            "Start with the bigger number.",
            "Count back the smaller number.",
            "For big numbers, subtract the ones and then the tens.",
            "Check with addition: add your answer back to the number you took away.",
        ],
        "example": "12 - 4: start at 12 and count back 4 → 11, 10, 9, 8.",
    },
    "multiplication": {
        "remember": "Multiplication is repeated addition of equal groups.",
        "steps": [
            "Read it as 'groups of'.",
            "Count the total in the equal groups.",
            "Practise the times table for the number.",
            "Remember that the order does not change the answer.",
        ],
        "example": "3 × 4 means 3 groups of 4: 4 + 4 + 4 = 12.",
    },
    "division": {
        "remember": "Division shares an amount into equal groups.",
        "steps": [
            "Read it as 'share into equal groups'.",
            "Ask how many are in each group.",
            "Use the matching times table.",
            "Check by multiplying your answer by the divisor.",
        ],
        "example": "15 ÷ 5: which number times 5 makes 15? → 3.",
    },
    "number-patterns": {
        "remember": "Find the difference between two numbers next to each other.",
        "steps": [
            "Look at two numbers side by side.",
            "Subtract the smaller from the larger.",
            "Check that the same step works for the next pair.",
            "Continue the pattern using that step.",
        ],
        "example": "5, 10, 15, 20 grows by 5 each time.",
    },
    "basic-shapes": {
        "remember": "Name a shape by counting its sides and corners.",
        "steps": [
            "Count the straight sides.",
            "Count the corners.",
            "Check if all sides are the same length.",
            "Use the side count to name the shape.",
        ],
        "example": "A triangle has 3 sides and 3 corners; a square has 4 equal sides.",
    },
    "fractions": {
        "remember": "The bottom number tells the equal parts, and the top number tells how many you have.",
        "steps": [
            "Check that the whole is cut into equal parts.",
            "Write the total number of parts as the bottom number.",
            "Write the parts you have as the top number.",
            "For adding with the same bottom number, add only the top numbers.",
        ],
        "example": "A pizza in 4 equal slices with 1 slice eaten → 1/4 eaten.",
    },
    "measurement": {
        "remember": "Use the right unit: cm and m for length, g and kg for weight, mL and L for capacity.",
        "steps": [
            "Decide what you are measuring: length, weight or capacity.",
            "Choose a unit that fits the object's size.",
            "Remember 100 cm = 1 m, 1000 g = 1 kg and 1000 mL = 1 L.",
            "To change a bigger unit to a smaller unit, multiply.",
        ],
        "example": "2 m = 2 × 100 = 200 cm, and 3 kg = 3 × 1000 = 3000 g.",
    },
    "time-and-money": {
        "remember": "The short hand shows hours and the long hand shows minutes. Add money to find a total and subtract to find change.",
        "steps": [
            "Read the hour from the short hand.",
            "Each number on the clock is 5 minutes for the long hand.",
            "For elapsed time, count whole hours (60 minutes) then add the extra minutes.",
            "For change, subtract the cost from the amount paid.",
        ],
        "example": "From 4:00 to 4:30 is 30 minutes. Change from ₹100 after spending ₹65 is ₹35.",
    },
    # Secondary English
    "parts-of-speech": {
        "remember": "Ask what job the word is doing in the sentence.",
        "steps": [
            "Noun: names a person, place, thing or idea.",
            "Verb: shows an action or a state.",
            "Adjective: describes a noun.",
            "Adverb: describes a verb, adjective or another adverb.",
        ],
        "example": "In 'She spoke softly', 'softly' describes how she spoke, so it is an adverb.",
    },
    "tenses": {
        "remember": "Tense tells us when the action happens.",
        "steps": [
            "Look for a time clue: every day, yesterday or tomorrow.",
            "Simple present: habits and facts.",
            "Simple past: completed actions.",
            "Simple future: use 'will' plus the base verb.",
        ],
        "example": "She studies (present), she studied (past), she will study (future).",
    },
    "active-passive-voice": {
        "remember": "Active voice: the subject does the action. Passive voice: the action is done to the subject.",
        "steps": [
            "Find the subject, the verb and the object.",
            "Move the object to the front.",
            "Use the correct form of 'be' plus the past participle.",
            "Add 'by' and the original subject if it matters.",
        ],
        "example": "Active: The chef cooked the meal. Passive: The meal was cooked by the chef.",
    },
    "direct-indirect-speech": {
        "remember": "Direct speech repeats exact words. Indirect speech reports them without quotation marks.",
        "steps": [
            "Remove the quotation marks.",
            "Change the reporting verb if needed: said → told.",
            "Move the tense one step back.",
            "Change pronouns and time words such as tomorrow → the next day.",
        ],
        "example": "Direct: 'I am tired.' Indirect: She said that she was tired.",
    },
    "vocabulary-building": {
        "remember": "A synonym means almost the same; an antonym means the opposite.",
        "steps": [
            "Read the word in a sentence.",
            "Use context clues around it.",
            "Think of a word with a similar meaning.",
            "Check that the word fits the sentence grammatically too.",
        ],
        "example": "'Rapid' and 'quick' are synonyms; 'expand' and 'shrink' are antonyms.",
    },
    "sentence-correction": {
        "remember": "Check the verb, the capital letters and the punctuation.",
        "steps": [
            "Find the subject and make sure the verb agrees with it.",
            "Use only one negative word in a negative sentence.",
            "Start with a capital letter and end with the right mark.",
            "Read it aloud to catch anything that sounds wrong.",
        ],
        "example": "Wrong: She go to school. Right: She goes to school.",
    },
    "reading-comprehension-secondary": {
        "remember": "The main idea is what the passage is mostly about; details support it.",
        "steps": [
            "Read the passage twice.",
            "Find the topic sentence of each paragraph.",
            "Underline the words that answer the question.",
            "For an inference, combine a clue from the text with your own reasoning.",
        ],
        "example": "If the passage says forests are cut down and asks what can be inferred, the answer is that protecting forests helps the environment.",
    },
    "basic-writing-skills": {
        "remember": "A paragraph needs a topic sentence, supporting sentences and a closing sentence.",
        "steps": [
            "Plan your main idea in one sentence.",
            "List three supporting points.",
            "Write the paragraph in a clear order.",
            "Proofread spelling, grammar and punctuation.",
        ],
        "example": "Topic sentence: Trees are important for every living thing. Then give oxygen, shade and soil as support.",
    },
    # Secondary Mathematics
    "integers": {
        "remember": "Integers are positive and negative whole numbers, including zero.",
        "steps": [
            "Draw or imagine a number line.",
            "Adding a negative moves left; adding a positive moves right.",
            "For multiplication, multiply the numbers then decide the sign.",
            "Two negatives give a positive; one negative gives a negative.",
        ],
        "example": "-7 + 3 = -4, and -4 × -3 = 12.",
    },
    "fractions-decimals": {
        "remember": "A fraction is a division: top ÷ bottom.",
        "steps": [
            "To convert a fraction to a decimal, divide the numerator by the denominator.",
            "To add fractions, make the denominators the same.",
            "Line up decimal points when adding decimals.",
            "Compare by converting both to the same form.",
        ],
        "example": "3/4 = 3 ÷ 4 = 0.75.",
    },
    "percentages": {
        "remember": "Percent means 'per hundred', so divide by 100.",
        "steps": [
            "Change the percentage to a decimal.",
            "Multiply by the number.",
            "For a discount, subtract the result from the original price.",
            "Check that the answer is sensible for the size of the number.",
        ],
        "example": "20% of 50 = 0.20 × 50 = 10.",
    },
    "ratio-proportion": {
        "remember": "A ratio compares two quantities; a proportion says two ratios are equal.",
        "steps": [
            "Write the ratio in the order the question gives.",
            "Simplify by dividing both parts by the same number.",
            "To share an amount, add the ratio parts first.",
            "Divide the total by the number of parts, then multiply each part.",
        ],
        "example": "Share 100 in 2:3 → 5 parts, one part is 20, shares are 40 and 60.",
    },
    "algebra": {
        "remember": "A letter stands for an unknown number, and only like terms can be combined.",
        "steps": [
            "Identify the like terms.",
            "Add or subtract their coefficients.",
            "To evaluate, replace the letter with the given number.",
            "To expand, multiply the outside number by every term inside the brackets.",
        ],
        "example": "3x + 2x = 5x; if x = 4 then 2x + 3 = 11.",
    },
    "geometry": {
        "remember": "Angles in a triangle add to 180°, and area is the space inside a shape.",
        "steps": [
            "Write down the facts you know about the shape.",
            "For a triangle, subtract the known angles from 180°.",
            "Area of a rectangle = length × width.",
            "Perimeter is the total distance around the outside.",
        ],
        "example": "A triangle with 60° and 60° has a third angle of 60°.",
    },
    "linear-equations": {
        "remember": "Keep the equation balanced: whatever you do to one side, do to the other.",
        "steps": [
            "Undo addition or subtraction first.",
            "Then undo multiplication or division.",
            "Keep the letter on one side and numbers on the other.",
            "Substitute your answer back to check it.",
        ],
        "example": "2x + 4 = 10 → 2x = 6 → x = 3.",
    },
    "basic-statistics": {
        "remember": "Mean is the average, median is the middle, mode is the most common and range is largest minus smallest.",
        "steps": [
            "For the mean, add all values and divide by how many there are.",
            "For the median, sort the values and find the middle.",
            "For the mode, look for the value that repeats most.",
            "For the range, subtract the smallest from the largest.",
        ],
        "example": "For 2, 4, 6: mean = 12 ÷ 3 = 4, median = 4, range = 4.",
    },
    "mensuration": {
        "remember": "Perimeter is the distance around, area is the surface inside and volume is the space inside a solid.",
        "steps": [
            "Identify the shape and the measurement the question asks for.",
            "Use perimeter = 2(l + w) for a rectangle.",
            "Use area = l × w for a rectangle and ½ × base × height for a triangle.",
            "Use volume = l × w × h for a cuboid.",
            "Write the correct unit: cm, cm² or cm³.",
        ],
        "example": "A 6 cm by 4 cm rectangle has perimeter 20 cm and area 24 cm².",
    },
}

# ---------------------------------------------------------------------------
# Keyword detection
# ---------------------------------------------------------------------------
# Order matters: more specific phrases come first.
KEYWORDS = [
    ("active-passive-voice", ["passive voice", "active voice", "passive", "active"]),
    ("direct-indirect-speech", ["indirect speech", "direct speech", "reported speech", "quotation"]),
    ("reading-comprehension-secondary", ["main idea", "inference", "comprehension", "passage", "summary"]),
    ("reading-comprehension", ["story", "read and answer", "comprehension"]),
    ("basic-writing-skills", ["paragraph", "letter writing", "essay", "topic sentence", "formal letter"]),
    ("mensuration", ["mensuration", "volume", "cuboid", "surface area", "three dimensional"]),
    ("measurement", ["measurement", "metre", "metres", "centimetre", "centimetres", "kilogram", "kilograms", "litre", "litres", "capacity"]),
    ("time-and-money", ["money", "rupee", "rupees", "clock", "elapsed time", "change from"]),
    ("sentence-correction", ["correct the sentence", "sentence correction", "double negative", "grammar mistake"]),
    ("parts-of-speech", ["parts of speech", "noun", "pronoun", "adjective", "adverb", "verb"]),
    ("tenses", ["tense", "present perfect", "past continuous", "future tense", "past tense", "present tense"]),
    ("vocabulary-building", ["synonym", "antonym", "vocabulary", "word meaning", "opposite word"]),
    ("linear-equations", ["linear equation", "solve for x", "equation", "balance the equation"]),
    ("ratio-proportion", ["ratio", "proportion", "share in the ratio"]),
    ("fractions-decimals", ["decimal", "fraction and decimal", "convert fraction"]),
    ("basic-statistics", ["mean", "median", "mode", "range", "statistics", "average"]),
    ("percentages", ["percentage", "percent", "discount", "interest"]),
    ("algebra", ["algebra", "expression", "expand", "simplify", "like terms"]),
    ("geometry", ["geometry", "angle", "triangle", "area", "perimeter", "circle", "pythagoras"]),
    ("integers", ["integer", "negative number", "number line", "positive and negative"]),
    ("fractions", ["fraction", "numerator", "denominator", "half", "quarter"]),
    ("multiplication", ["multiplication", "multiply", "times table", "product", "times"]),
    ("division", ["division", "divide", "quotient", "share equally"]),
    ("addition", ["addition", "add", "sum", "plus", "total"]),
    ("subtraction", ["subtraction", "subtract", "minus", "difference", "take away"]),
    ("counting", ["counting", "count", "how many", "number pattern"]),
    ("number-patterns", ["number pattern", "sequence", "missing number", "pattern"]),
    ("basic-shapes", ["shape", "triangle shape", "square", "rectangle", "circle shape", "sides"]),
    ("spelling-practice", ["spelling", "spell", "how do you spell", "misspell"]),
    ("articles", ["article", "a or an", "use a", "use an"]),
    ("alphabet-recognition", ["alphabet", "vowel", "consonant", "letter"]),
    ("basic-vocabulary", ["vocabulary word", "word for", "means", "opposite"]),
    ("naming-words", ["naming word", "noun"]),
    ("simple-sentences", ["sentence", "capital letter", "full stop", "punctuation"]),
    ("basic-grammar", ["plural", "singular", "grammar", "pronoun"]),
]

GREETING_WORDS = {"hi", "hello", "hey", "namaste", "good morning", "good afternoon", "good evening"}
THANKS_WORDS = {"thank", "thanks", "thank you", "shukriya"}

def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").lower()).strip()


def detect_topic(message: str, class_level: int, fallback: str | None = None) -> str | None:
    """Return the most likely topic slug for a message."""
    text = normalise(message)
    if not text:
        return fallback

    # Explicit topic title match first.
    for topic in TOPICS:
        if topic["title"].lower() in text or topic["slug"] in text:
            return topic["slug"]

    # An equation such as 2x + 4 = 10.
    if "=" in text and re.search(r"[a-z]", text):
        return "linear-equations" if class_level >= 6 else None

    # A percentage question.
    if re.search(r"\d+\s*%", text) or "percent" in text:
        return "percentages"

    # A fraction calculation such as 1/2 + 1/4.
    if re.search(r"\d+\s*/\s*\d+", text):
        return "fractions-decimals" if class_level >= 6 else "fractions"

    # A plain arithmetic question such as 12 + 7.
    if re.search(r"\d+\s*[+\-×x*÷/]\s*\d+", text):
        if class_level >= 6:
            return "integers"
        if re.search(r"[×x*]", text):
            return "multiplication"
        if re.search(r"[÷/]", text):
            return "division"
        if re.search(r"[+\-]", text):
            return "addition" if "+" in text else "subtraction"

    for slug, words in KEYWORDS:
        for word in words:
            if re.search(rf"\b{re.escape(word)}\b", text):
                topic = TOPIC_BY_SLUG.get(slug)
                if not topic:
                    continue
                # Prefer a topic that belongs to the student's level.
                if topic["level"] == level_for_class(class_level):
                    return slug
                # Otherwise keep looking for a level-appropriate match.
    return fallback


def _suggestions_for(topic, class_level):
    """Three class-appropriate follow-up prompts."""
    title = topic["title"]
    if class_level <= 5:
        return [
            f"Give me an easy example of {title}.",
            f"Can you ask me a practice question on {title}?",
            f"Explain {title} in an even simpler way.",
        ]
    return [
        f"Show me a worked example for {title}.",
        f"Give me a harder practice question on {title}.",
        f"What is a common mistake in {title}?",
    ]


def _primary_example(topic):
    examples = topic.get("examples") or []
    if not examples:
        return ""
    first = examples[0]
    return f"{first.get('emoji', '•')} {first.get('title', 'Example')}: {first.get('body', '')}"


def _secondary_example(topic):
    examples = topic.get("examples") or []
    if not examples:
        return ""
    return " ".join(
        f"{item.get('title', '')}: {item.get('body', '')}" for item in examples[:2]
    )


def topic_explanation(topic_slug: str, class_level: int, question: str = ""):
    """Return the assistant reply for a curriculum topic."""
    topic = TOPIC_BY_SLUG[topic_slug]
    hint = TOPIC_HINTS.get(topic_slug, {})
    level = level_for_class(class_level)
    title = topic["title"]
    text = normalise(question)

    asks_example = any(word in text for word in ["example", "show me", "demonstrate"])
    asks_answer = any(
        phrase in text
        for phrase in ["give me the answer", "what is the answer", "tell me the answer", "answer is"]
    )

    lines = []
    if level == "Primary":
        lines.append(f"Let's learn {title}! {topic['emoji']}")
        summary = hint.get("remember") or topic["description"]
        lines.append(summary)
        if asks_answer:
            lines.append(
                "I won't give the quiz answer, but I can help you find it yourself. "
                "Try these steps:"
            )
        else:
            lines.append("Here is how to do it:")
        steps = hint.get("steps", [])[:3]
        lines.extend(f"{index}. {step}" for index, step in enumerate(steps, start=1))
        example = _primary_example(topic)
        if example and (asks_example or level == "Primary"):
            lines.append(f"Example: {example}")
        lines.append("You can try it now, and I can explain any step again. 🌟")
    else:
        lines.append(f"{title} — a quick explanation.")
        lines.append(hint.get("remember") or topic["description"])
        if asks_answer:
            lines.append(
                "I won't hand over a quiz answer, but here is the method so you can solve it."
            )
        steps = hint.get("steps", [])[:4]
        if steps:
            lines.append("Method:")
            lines.extend(f"{index}. {step}" for index, step in enumerate(steps, start=1))
        example = _secondary_example(topic)
        if example:
            lines.append(f"Worked example — {example}")
        if asks_example:
            lines.append("Try changing the numbers in the example and solving it yourself.")
        lines.append("Ask me to check your reasoning at any step.")

    return {
        "answer": "\n".join(lines),
        "topic_slug": topic_slug,
        "topic_title": title,
        "subject": topic["subject"],
        "suggestions": _suggestions_for(topic, class_level),
        "kind": "topic",
    }


def build_reply(message: str, class_level: int = 1, topic_slug: str | None = None):
    """
    Build a safe, class-aware reply.

    The function always returns the same dictionary shape so the route and
    frontend stay simple.
    """
    text = normalise(message)
    level = level_for_class(class_level)

    if not text:
        return {
            "answer": (
                "Hi! Ask me about any English or Mathematics topic and I will "
                "explain it step by step."
            ),
            "topic_slug": None,
            "topic_title": None,
            "subject": None,
            "suggestions": [
                "Explain fractions in a simple way.",
                "How do I find the main idea of a passage?",
                "What is a synonym?",
            ],
            "kind": "greeting",
        }

    if any(word in text.split() for word in GREETING_WORDS) or text in GREETING_WORDS:
        return {
            "answer": (
                f"Hello! I'm your learning helper. 🌟 You are in Class {class_level}, "
                "so I'll keep my explanations at a level that fits you. "
                "What would you like to learn today?"
            ),
            "topic_slug": None,
            "topic_title": None,
            "subject": None,
            "suggestions": [
                "Help me with my Maths topic.",
                "Explain a grammar rule to me.",
                "How can I practise reading?",
            ],
            "kind": "greeting",
        }

    if any(word in text for word in THANKS_WORDS):
        return {
            "answer": (
                "You're welcome! Keep asking questions — that is how learning "
                "gets easier. 😊"
            ),
            "topic_slug": None,
            "topic_title": None,
            "subject": None,
            "suggestions": [
                "Give me a practice question.",
                "Explain another topic.",
                "How can I improve my score?",
            ],
            "kind": "thanks",
        }

    detected = detect_topic(text, class_level, fallback=topic_slug)
    # A primary-class student must never be shown secondary content (or the
    # reverse), even if the question itself names another class's topic.
    if detected:
        topic = TOPIC_BY_SLUG.get(detected)
        if not topic or topic["level"] != level_for_class(class_level):
            detected = None
    if detected and detected in TOPIC_HINTS:
        return topic_explanation(detected, class_level, message)

    # Subject-level fallback: talk about how to study that subject.
    math_signal = any(word in text for word in ["math", "maths", "number", "calculate", "equation", "solve"])
    math_signal = math_signal or bool(re.search(r"\d", text))
    subject = "Mathematics" if math_signal else "English"
    if subject == "Mathematics":
        answer = (
            f"Maths is easier when you take it one small step at a time. "
            f"For Class {class_level}, try this routine:\n"
            "1. Read the question twice and underline the numbers.\n"
            "2. Write down what you already know.\n"
            "3. Choose an operation: add, subtract, multiply or divide.\n"
            "4. Check your answer with a different method."
        )
        suggestions = [
            "Explain addition step by step.",
            "How do fractions work?",
            "Give me a practice question on percentages.",
        ]
        subject_name = "Mathematics"
    else:
        answer = (
            f"English gets easier with a little practice every day. "
            f"For Class {class_level}, try this routine:\n"
            "1. Read a short passage aloud.\n"
            "2. Write down two new words and their meanings.\n"
            "3. Write one sentence using each new word.\n"
            "4. Check capital letters, verbs and full stops."
        )
        suggestions = [
            "Explain nouns in a simple way.",
            "How do I use a and an?",
            "How can I find the main idea?",
        ]
        subject_name = "English"

    return {
        "answer": answer,
        "topic_slug": None,
        "topic_title": None,
        "subject": subject_name,
        "suggestions": suggestions,
        "kind": "subject",
    }
