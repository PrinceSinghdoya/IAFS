"""
School curriculum for IAFS.

This module is the single source of truth for:
  * Classes 1-10 and the Primary / Secondary split
  * The English and Mathematics topic catalogue
  * Class-aware explanations, examples and practice questions
  * The adaptive question generator used by the quiz API

The content is deliberately simple, friendly and explainable. Nothing here
calls an external AI service, so the project works completely offline after
the Python dependencies are installed.
"""
from __future__ import annotations

import random

# ---------------------------------------------------------------------------
# Classes and subjects
# ---------------------------------------------------------------------------
CLASS_LEVELS = list(range(1, 11))
PRIMARY_CLASSES = [1, 2, 3, 4, 5]
SECONDARY_CLASSES = [6, 7, 8, 9, 10]

SUBJECT_ENGLISH = "English"
SUBJECT_MATHS = "Mathematics"
SUBJECTS = [SUBJECT_ENGLISH, SUBJECT_MATHS]

SUBJECT_INFO = {
    SUBJECT_ENGLISH: {
        "name": SUBJECT_ENGLISH,
        "icon": "BookOpenText",
        "emoji": "📖",
        "colour": "violet",
        "tagline": "Reading, writing, words and confident speaking.",
        "description": (
            "Build strong reading and writing habits with stories, vocabulary, "
            "grammar and sentence practice."
        ),
    },
    SUBJECT_MATHS: {
        "name": SUBJECT_MATHS,
        "icon": "Calculator",
        "emoji": "🔢",
        "colour": "blue",
        "tagline": "Numbers, patterns, shapes and problem solving.",
        "description": (
            "Learn numbers step by step with counting, arithmetic, fractions, "
            "algebra, geometry and everyday maths."
        ),
    },
}


def level_for_class(class_level: int) -> str:
    """Return 'Primary' or 'Secondary' for a class number."""
    return "Primary" if int(class_level) <= 5 else "Secondary"


def classes_for_level(level: str):
    return PRIMARY_CLASSES if level == "Primary" else SECONDARY_CLASSES


# ---------------------------------------------------------------------------
# Topic catalogue
# ---------------------------------------------------------------------------
# Each topic is intentionally short enough to read in 5-8 minutes. The
# `class_tips` entry lets the lesson page speak directly to the student's class.
TOPICS = [
    # ------------------------------------------------------------------ Primary English
    {
        "slug": "alphabet-recognition",
        "title": "Alphabet Recognition",
        "subject": SUBJECT_ENGLISH,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "SpellCheck",
        "emoji": "🔤",
        "order": 1,
        "description": "Meet the 26 letters and learn their capital and small forms.",
        "explanation": (
            "The English alphabet has 26 letters. We use capital letters at the "
            "start of a name, at the start of a sentence and for the word 'I'. "
            "All other letters are usually small letters.\n\n"
            "The five vowels are A, E, I, O and U. The other 21 letters are "
            "consonants. Learning the order of the alphabet helps you use a "
            "dictionary and read new words."
        ),
        "examples": [
            {"title": "Capital and small", "body": "A → a, B → b, C → c", "emoji": "🅰️"},
            {"title": "Vowels", "body": "A, E, I, O, U are vowels.", "emoji": "🎵"},
            {"title": "Alphabet order", "body": "A, B, C, D, E, F, G ...", "emoji": "🔤"},
        ],
        "key_points": [
            "There are 26 letters in English.",
            "A, E, I, O and U are vowels.",
            "Names and sentences begin with a capital letter.",
        ],
        "class_tips": {
            "1": "Sing the alphabet song and point to each letter as you say it.",
            "2": "Practise writing both the capital and small form of five letters.",
            "3": "Put five words in alphabetical order using their first letters.",
            "4": "Find the vowels and consonants in your own name.",
            "5": "Use a dictionary to find two words that start with the same letter.",
        },
    },
    {
        "slug": "basic-vocabulary",
        "title": "Basic Vocabulary",
        "subject": SUBJECT_ENGLISH,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "BookMarked",
        "emoji": "🗂️",
        "order": 2,
        "description": "Learn useful words for people, places, animals and everyday things.",
        "explanation": (
            "Vocabulary means the words we know and use. A good vocabulary helps "
            "you read, write and speak clearly.\n\n"
            "You can grow your vocabulary by learning one new word each day, "
            "using it in a sentence and looking for it in your reading book."
        ),
        "examples": [
            {"title": "People", "body": "teacher, friend, doctor, farmer", "emoji": "👩‍🏫"},
            {"title": "Places", "body": "school, market, park, hospital", "emoji": "🏫"},
            {"title": "Describing words", "body": "happy, bright, quiet, brave", "emoji": "🌈"},
        ],
        "key_points": [
            "Vocabulary is the set of words you understand.",
            "Learn words in groups such as animals or places.",
            "Use a new word in your own sentence to remember it.",
        ],
        "class_tips": {
            "1": "Name five things you can see in your classroom.",
            "2": "Write the names of five animals and their sounds.",
            "3": "Make a word map for the word 'school'.",
            "4": "Write a sentence using the word 'curious'.",
            "5": "Find three new words in a story and write their meanings.",
        },
    },
    {
        "slug": "naming-words",
        "title": "Naming Words",
        "subject": SUBJECT_ENGLISH,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "Users",
        "emoji": "👧",
        "order": 3,
        "description": "Find the words that name a person, place, animal or thing.",
        "explanation": (
            "A naming word is also called a noun. It names a person, place, "
            "animal or thing.\n\n"
            "In the sentence 'Riya reads a book in the library', Riya is a "
            "person, book is a thing and library is a place. All three are "
            "naming words."
        ),
        "examples": [
            {"title": "Person", "body": "Rahul, teacher, mother", "emoji": "🧑"},
            {"title": "Place", "body": "Delhi, school, garden", "emoji": "🏙️"},
            {"title": "Animal or thing", "body": "dog, pencil, bicycle", "emoji": "🐕"},
        ],
        "key_points": [
            "Naming words are also called nouns.",
            "They name people, places, animals and things.",
            "A sentence usually has at least one naming word.",
        ],
        "class_tips": {
            "1": "Point to three things and say their names.",
            "2": "Circle the naming words in 'The cat sleeps on the bed'.",
            "3": "Write two names of people and two names of places.",
            "4": "Sort ten nouns into person, place, animal and thing.",
            "5": "Rewrite a short paragraph and underline every noun.",
        },
    },
    {
        "slug": "articles",
        "title": "Articles",
        "subject": SUBJECT_ENGLISH,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "Type",
        "emoji": "🅰️",
        "order": 4,
        "description": "Use a, an and the correctly in simple sentences.",
        "explanation": (
            "Articles are small words that come before naming words. We use 'a' "
            "before a word that starts with a consonant sound and 'an' before a "
            "word that starts with a vowel sound.\n\n"
            "We use 'the' when we talk about one particular person or thing. "
            "For example: 'I saw a dog. The dog was friendly.'"
        ),
        "examples": [
            {"title": "A", "body": "a cat, a school, a red ball", "emoji": "🐱"},
            {"title": "An", "body": "an apple, an elephant, an orange", "emoji": "🍎"},
            {"title": "The", "body": "the sun, the moon, the tallest tree", "emoji": "☀️"},
        ],
        "key_points": [
            "Use 'a' before consonant sounds.",
            "Use 'an' before vowel sounds.",
            "Use 'the' for a specific person or thing.",
        ],
        "class_tips": {
            "1": "Say 'a cat' and 'an apple' aloud.",
            "2": "Write five words with 'a' and five with 'an'.",
            "3": "Complete: ___ owl, ___ pencil, ___ moon.",
            "4": "Write three sentences using a, an and the.",
            "5": "Explain why we say 'an hour' but 'a house'.",
        },
    },
    {
        "slug": "simple-sentences",
        "title": "Simple Sentences",
        "subject": SUBJECT_ENGLISH,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "AlignLeft",
        "emoji": "✏️",
        "order": 5,
        "description": "Build clear sentences with a capital letter and full stop.",
        "explanation": (
            "A sentence is a group of words that makes complete sense. It begins "
            "with a capital letter and ends with a full stop, question mark or "
            "exclamation mark.\n\n"
            "A simple sentence needs a subject and a verb. In 'Birds fly', "
            "'birds' is the subject and 'fly' is the verb."
        ),
        "examples": [
            {"title": "Statement", "body": "The boy is reading a book.", "emoji": "📘"},
            {"title": "Question", "body": "Where is my pencil?", "emoji": "❓"},
            {"title": "Exclamation", "body": "What a beautiful rainbow!", "emoji": "🌈"},
        ],
        "key_points": [
            "Every sentence needs a subject and a verb.",
            "Start a sentence with a capital letter.",
            "End with the correct punctuation mark.",
        ],
        "class_tips": {
            "1": "Make a sentence using the words 'I' and 'like'.",
            "2": "Add a full stop to five sentences.",
            "3": "Write one statement and one question.",
            "4": "Underline the subject in three sentences.",
            "5": "Rewrite a paragraph with correct capital letters and full stops.",
        },
    },
    {
        "slug": "basic-grammar",
        "title": "Basic Grammar",
        "subject": SUBJECT_ENGLISH,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "PenTool",
        "emoji": "🧩",
        "order": 6,
        "description": "Learn plurals, verbs, pronouns and the rules that join words.",
        "explanation": (
            "Grammar is the set of rules that helps us put words together "
            "correctly. We add -s or -es to many naming words to show more than "
            "one: one cat, two cats; one box, two boxes.\n\n"
            "We also choose the right verb. A singular naming word takes 'is' or "
            "'has', while a plural naming word takes 'are' or 'have'."
        ),
        "examples": [
            {"title": "Plurals", "body": "cat → cats, bus → buses, baby → babies", "emoji": "➕"},
            {"title": "Verbs", "body": "She is happy. They are happy.", "emoji": "🏃"},
            {"title": "Pronouns", "body": "I, you, he, she, it, we, they", "emoji": "👥"},
        ],
        "key_points": [
            "Plurals often end in -s or -es.",
            "The verb must agree with the naming word.",
            "Pronouns replace nouns to avoid repetition.",
        ],
        "class_tips": {
            "1": "Say the plural of cat, dog and book.",
            "2": "Write the plural of bus, box and baby.",
            "3": "Choose is or are for five sentences.",
            "4": "Replace a repeated name with a pronoun.",
            "5": "Write a short paragraph using correct plurals and verbs.",
        },
    },
    {
        "slug": "reading-comprehension",
        "title": "Reading Comprehension",
        "subject": SUBJECT_ENGLISH,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "BookOpen",
        "emoji": "📚",
        "order": 7,
        "description": "Read a short story and answer questions about it.",
        "explanation": (
            "Reading comprehension means understanding what you read. Good "
            "readers read slowly, picture the story and look back at the text "
            "when they answer a question.\n\n"
            "Ask yourself: Who is in the story? Where are they? What happened? "
            "How did the story end?"
        ),
        "examples": [
            {"title": "Who?", "body": "Find the person or animal in the story.", "emoji": "🧐"},
            {"title": "Where?", "body": "Look for a place word such as park or school.", "emoji": "📍"},
            {"title": "What happened?", "body": "Find the action or the problem.", "emoji": "⚡"},
        ],
        "key_points": [
            "Read the question before looking back at the text.",
            "Find the exact sentence that supports your answer.",
            "A story has characters, a place and events.",
        ],
        "class_tips": {
            "1": "Read a picture book and name the main character.",
            "2": "Read two sentences and say where the story happens.",
            "3": "Write one question about a story you read.",
            "4": "Find the beginning, middle and end of a story.",
            "5": "Read a short passage and explain the lesson it teaches.",
        },
    },
    {
        "slug": "spelling-practice",
        "title": "Spelling Practice",
        "subject": SUBJECT_ENGLISH,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "SpellCheck2",
        "emoji": "🔡",
        "order": 8,
        "description": "Learn to spell common words correctly and spot mistakes.",
        "explanation": (
            "Spelling is how we write the sounds of a word using letters. Some "
            "words sound the way they are written, but many English words have "
            "a special pattern.\n\n"
            "Break a long word into small parts, say it aloud and write it three "
            "times. Then cover it and try again from memory."
        ),
        "examples": [
            {"title": "Sound it out", "body": "c-a-t → cat", "emoji": "🐱"},
            {"title": "Word families", "body": "light, night, bright", "emoji": "💡"},
            {"title": "Tricky words", "body": "because, friend, beautiful", "emoji": "🌟"},
        ],
        "key_points": [
            "Say the word slowly and listen to each sound.",
            "Look for a spelling pattern or word family.",
            "Practice a tricky word three times.",
        ],
        "class_tips": {
            "1": "Spell your name and three colour words.",
            "2": "Write cat, dog, sun and book three times.",
            "3": "Find the correctly spelled word in a list.",
            "4": "Practice five words with 'ea' or 'ee'.",
            "5": "Write a sentence with a tricky word such as 'beautiful'.",
        },
    },
    # ------------------------------------------------------------------ Primary Mathematics
    {
        "slug": "counting",
        "title": "Counting",
        "subject": SUBJECT_MATHS,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "Hash",
        "emoji": "🔢",
        "order": 1,
        "description": "Count objects, read numbers and continue number patterns.",
        "explanation": (
            "Counting tells us how many things there are. We say one number for "
            "each object and stop when every object has been counted.\n\n"
            "When we count in order, each number is one more than the number "
            "before it: 1, 2, 3, 4, 5. We can also skip count: 2, 4, 6, 8 or "
            "5, 10, 15, 20."
        ),
        "examples": [
            {"title": "Count the stars", "body": "⭐ ⭐ ⭐ ⭐ ⭐ = 5 stars", "emoji": "⭐"},
            {"title": "One more", "body": "8 + 1 = 9", "emoji": "➕"},
            {"title": "Skip counting", "body": "5, 10, 15, 20, 25 ...", "emoji": "🦘"},
        ],
        "key_points": [
            "Say one number for each object.",
            "The last number you say is the total.",
            "Counting patterns can go up by 2, 5 or 10.",
        ],
        "class_tips": {
            "1": "Count ten toys in your room.",
            "2": "Count to 50 in steps of 2.",
            "3": "Write the missing numbers from 1 to 100.",
            "4": "Count backwards from 50 to 1.",
            "5": "Make a skip-counting pattern with 7s.",
        },
    },
    {
        "slug": "addition",
        "title": "Addition",
        "subject": SUBJECT_MATHS,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "Plus",
        "emoji": "➕",
        "order": 2,
        "description": "Put numbers together to find the total.",
        "explanation": (
            "Addition means putting two or more amounts together. The plus sign "
            "(+) tells us to add, and the equals sign (=) shows the answer.\n\n"
            "We can add by counting on, using fingers, drawing groups or making a "
            "number line. The order of the numbers does not change the total: "
            "3 + 4 is the same as 4 + 3."
        ),
        "examples": [
            {"title": "Small numbers", "body": "3 + 4 = 7", "emoji": "🍎"},
            {"title": "Counting on", "body": "Start at 8 and count 3 more: 9, 10, 11", "emoji": "👣"},
            {"title": "Add three numbers", "body": "2 + 3 + 4 = 9", "emoji": "🧮"},
        ],
        "key_points": [
            "Addition finds the total.",
            "The answer is called the sum.",
            "Changing the order does not change the sum.",
        ],
        "class_tips": {
            "1": "Add using objects: 2 + 3.",
            "2": "Add numbers up to 20 using a number line.",
            "3": "Add two-digit numbers without carrying.",
            "4": "Add three-digit numbers with carrying.",
            "5": "Solve a shopping word problem with addition.",
        },
    },
    {
        "slug": "subtraction",
        "title": "Subtraction",
        "subject": SUBJECT_MATHS,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "Minus",
        "emoji": "➖",
        "order": 3,
        "description": "Take away numbers and find the difference.",
        "explanation": (
            "Subtraction means taking one amount away from another. The minus "
            "sign (-) shows subtraction. The answer is called the difference.\n\n"
            "If you have 8 apples and eat 3, you can subtract to find how many "
            "are left: 8 - 3 = 5. Subtraction is the opposite of addition."
        ),
        "examples": [
            {"title": "Take away", "body": "9 - 4 = 5", "emoji": "🍪"},
            {"title": "Count back", "body": "Start at 10 and count back 3: 9, 8, 7", "emoji": "👣"},
            {"title": "Difference", "body": "12 - 7 = 5", "emoji": "🧮"},
        ],
        "key_points": [
            "Subtraction finds what is left or the difference.",
            "The answer is called the difference.",
            "Addition can check subtraction: 5 + 3 = 8.",
        ],
        "class_tips": {
            "1": "Take away 2 from 5 using objects.",
            "2": "Subtract numbers up to 20.",
            "3": "Subtract two-digit numbers.",
            "4": "Subtract three-digit numbers with borrowing.",
            "5": "Solve a word problem about money and change.",
        },
    },
    {
        "slug": "multiplication",
        "title": "Multiplication",
        "subject": SUBJECT_MATHS,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "X",
        "emoji": "✖️",
        "order": 4,
        "description": "Use equal groups and times tables to multiply.",
        "explanation": (
            "Multiplication is repeated addition of equal groups. 3 × 4 means "
            "3 groups of 4, or 4 + 4 + 4, which equals 12.\n\n"
            "The times sign (×) is used for multiplication. Learning tables from "
            "2 to 10 makes multiplication much faster."
        ),
        "examples": [
            {"title": "Equal groups", "body": "2 groups of 5 = 2 × 5 = 10", "emoji": "🍬"},
            {"title": "Times table", "body": "3 × 4 = 12", "emoji": "🧮"},
            {"title": "Real life", "body": "4 bags with 5 marbles each = 20 marbles", "emoji": "🔮"},
        ],
        "key_points": [
            "Multiplication is repeated addition.",
            "The answer is called the product.",
            "The order of the numbers does not change the product.",
        ],
        "class_tips": {
            "1": "Make two groups of three blocks.",
            "2": "Learn the 2 and 5 times tables.",
            "3": "Learn tables up to 10.",
            "4": "Multiply a two-digit number by one digit.",
            "5": "Solve a word problem with equal groups.",
        },
    },
    {
        "slug": "division",
        "title": "Division",
        "subject": SUBJECT_MATHS,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "Divide",
        "emoji": "➗",
        "order": 5,
        "description": "Share amounts equally and use division facts.",
        "explanation": (
            "Division means sharing an amount into equal groups. 12 ÷ 3 = 4 "
            "means 12 objects shared into 3 equal groups, with 4 objects in each "
            "group.\n\n"
            "Division is the opposite of multiplication. If 3 × 4 = 12, then "
            "12 ÷ 3 = 4."
        ),
        "examples": [
            {"title": "Share equally", "body": "6 sweets shared by 2 children = 3 each", "emoji": "🍬"},
            {"title": "Division fact", "body": "15 ÷ 5 = 3", "emoji": "🧮"},
            {"title": "Check with multiplication", "body": "3 × 5 = 15, so 15 ÷ 5 = 3", "emoji": "✅"},
        ],
        "key_points": [
            "Division shares an amount into equal groups.",
            "The answer is called the quotient.",
            "Multiplication can check a division answer.",
        ],
        "class_tips": {
            "1": "Share six pencils between two friends.",
            "2": "Divide numbers up to 20 by 2 and 5.",
            "3": "Use times tables to divide.",
            "4": "Divide a two-digit number by one digit.",
            "5": "Solve a sharing word problem.",
        },
    },
    {
        "slug": "number-patterns",
        "title": "Number Patterns",
        "subject": SUBJECT_MATHS,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "Waves",
        "emoji": "🌀",
        "order": 6,
        "description": "Spot the rule and continue a number sequence.",
        "explanation": (
            "A number pattern is a list of numbers that follows a rule. The rule "
            "tells us how to get from one number to the next.\n\n"
            "In 2, 4, 6, 8 the rule is 'add 2'. In 20, 17, 14, 11 the rule is "
            "'subtract 3'. Once you find the rule, you can continue the pattern."
        ),
        "examples": [
            {"title": "Add 2", "body": "2, 4, 6, 8, 10", "emoji": "➕"},
            {"title": "Add 5", "body": "5, 10, 15, 20", "emoji": "🖐️"},
            {"title": "Subtract 3", "body": "20, 17, 14, 11", "emoji": "➖"},
        ],
        "key_points": [
            "Find the difference between two neighbouring numbers.",
            "Check that the same rule works for the whole pattern.",
            "Patterns can go up or down.",
        ],
        "class_tips": {
            "1": "Continue 1, 2, 3, 4, ...",
            "2": "Continue 2, 4, 6, 8, ...",
            "3": "Continue 5, 10, 15, ...",
            "4": "Find the rule in 100, 90, 80, ...",
            "5": "Make your own pattern and explain the rule.",
        },
    },
    {
        "slug": "basic-shapes",
        "title": "Basic Shapes",
        "subject": SUBJECT_MATHS,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "Shapes",
        "emoji": "🔺",
        "order": 7,
        "description": "Recognise triangles, squares, rectangles and circles.",
        "explanation": (
            "Shapes are all around us. A triangle has 3 sides, a square has 4 "
            "equal sides, a rectangle has 4 sides with opposite sides equal, and "
            "a circle is round with no corners.\n\n"
            "We can describe a shape by its sides and corners. A square and a "
            "rectangle both have 4 corners, but only a square has all four sides "
            "the same length."
        ),
        "examples": [
            {"title": "Triangle", "body": "3 sides, 3 corners", "emoji": "🔺"},
            {"title": "Square", "body": "4 equal sides, 4 corners", "emoji": "🟦"},
            {"title": "Circle", "body": "Round, no corners", "emoji": "⭕"},
        ],
        "key_points": [
            "Count the sides and corners to name a shape.",
            "A square has four equal sides.",
            "A circle has no straight sides or corners.",
        ],
        "class_tips": {
            "1": "Find a circle and a square in your classroom.",
            "2": "Draw a triangle and count its sides.",
            "3": "Sort shapes by the number of sides.",
            "4": "Find the perimeter of a square.",
            "5": "Design a picture using at least five shapes.",
        },
    },
    {
        "slug": "fractions",
        "title": "Fractions",
        "subject": SUBJECT_MATHS,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "PieChart",
        "emoji": "🍕",
        "order": 8,
        "description": "Understand equal parts of a whole using simple fractions.",
        "explanation": (
            "A fraction shows a part of a whole. If a pizza is cut into 4 equal "
            "pieces and you eat 1 piece, you have eaten 1/4 of the pizza.\n\n"
            "The number below the line is the denominator. It tells how many "
            "equal parts the whole is divided into. The number above the line is "
            "the numerator. It tells how many parts you have."
        ),
        "examples": [
            {"title": "One quarter", "body": "1 out of 4 equal parts = 1/4", "emoji": "🍕"},
            {"title": "One half", "body": "1 out of 2 equal parts = 1/2", "emoji": "🍰"},
            {"title": "Three quarters", "body": "3 out of 4 equal parts = 3/4", "emoji": "🧇"},
        ],
        "key_points": [
            "A fraction shows equal parts of a whole.",
            "The denominator tells the number of equal parts.",
            "The numerator tells how many parts are taken.",
        ],
        "class_tips": {
            "1": "Break a biscuit into two equal parts.",
            "2": "Colour half of a shape.",
            "3": "Write the fraction for three out of five parts.",
            "4": "Compare 1/2 and 1/4.",
            "5": "Find 1/3 of 12 objects.",
        },
    },
    {
        "slug": "measurement",
        "title": "Measurement",
        "subject": SUBJECT_MATHS,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "Ruler",
        "emoji": "📏",
        "order": 9,
        "description": "Measure length, weight and capacity using the right units.",
        "explanation": (
            "We measure things to find out how long, how heavy or how much they "
            "are. Length is measured in centimetres (cm) and metres (m). Weight "
            "is measured in grams (g) and kilograms (kg). Capacity, or how much "
            "a container holds, is measured in millilitres (mL) and litres (L).\n\n"
            "Choose the unit that fits the object: a pencil is about 15 cm, a "
            "door is about 2 m, and a bottle of water may hold 1 L. 100 cm makes "
            "1 m, 1000 g makes 1 kg, and 1000 mL makes 1 L."
        ),
        "examples": [
            {"title": "Length", "body": "A pencil is about 15 cm long.", "emoji": "✏️"},
            {"title": "Weight", "body": "A bag of rice may weigh 5 kg.", "emoji": "⚖️"},
            {"title": "Capacity", "body": "A small bottle holds 500 mL.", "emoji": "🍶"},
        ],
        "key_points": [
            "Length uses cm and m; 100 cm = 1 m.",
            "Weight uses g and kg; 1000 g = 1 kg.",
            "Capacity uses mL and L; 1000 mL = 1 L.",
            "Pick the unit that matches the size of the object.",
        ],
        "class_tips": {
            "1": "Use your hand spans to measure the table.",
            "2": "Measure your pencil with a ruler and say the length in cm.",
            "3": "Compare the weight of a book and a lunch box.",
            "4": "Convert 3 m into centimetres.",
            "5": "Find how many 250 mL cups fill a 1 L bottle.",
        },
    },
    {
        "slug": "time-and-money",
        "title": "Time and Money",
        "subject": SUBJECT_MATHS,
        "level": "Primary",
        "classes": PRIMARY_CLASSES,
        "icon": "Clock3",
        "emoji": "🕒",
        "order": 10,
        "description": "Read clocks, work out elapsed time and handle money.",
        "explanation": (
            "A clock has two hands. The short hand shows the hour and the long "
            "hand shows the minutes. The minute hand moves 5 minutes for each "
            "number on the clock face, so 12 means 0 minutes, 3 means 15 minutes "
            "and 6 means 30 minutes.\n\n"
            "Money helps us buy things. We add coins and notes to find a total, "
            "and subtract to find change. If an item costs ₹40 and you pay ₹100, "
            "your change is ₹60."
        ),
        "examples": [
            {"title": "Telling time", "body": "Short hand on 3, long hand on 12 → 3 o'clock", "emoji": "🕒"},
            {"title": "Elapsed time", "body": "From 4:00 to 4:30 is 30 minutes", "emoji": "⏳"},
            {"title": "Money", "body": "₹25 + ₹30 = ₹55", "emoji": "💰"},
        ],
        "key_points": [
            "The short hand shows hours; the long hand shows minutes.",
            "Each number on the clock is 5 minutes.",
            "Add money to find the total; subtract to find change.",
            "60 minutes make 1 hour.",
        ],
        "class_tips": {
            "1": "Say the time when the short hand points to 3.",
            "2": "Show 6 o'clock on a paper clock.",
            "3": "Count the minutes from 2:00 to 2:30.",
            "4": "Add ₹35 and ₹48.",
            "5": "Find the change from ₹100 after spending ₹65.",
        },
    },
    # ------------------------------------------------------------------ Secondary English
    {
        "slug": "parts-of-speech",
        "title": "Parts of Speech",
        "subject": SUBJECT_ENGLISH,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "Blocks",
        "emoji": "🧱",
        "order": 1,
        "description": "Identify nouns, pronouns, verbs, adjectives and adverbs.",
        "explanation": (
            "Every word in a sentence has a job. These jobs are called parts of "
            "speech. The main ones are nouns (names), pronouns (replace nouns), "
            "verbs (actions), adjectives (describe nouns) and adverbs (describe "
            "verbs or adjectives).\n\n"
            "Knowing the job of a word helps you write correct sentences and "
            "understand new words."
        ),
        "examples": [
            {"title": "Noun", "body": "The teacher explained the lesson.", "emoji": "👩‍🏫"},
            {"title": "Verb", "body": "She explained it clearly.", "emoji": "🏃"},
            {"title": "Adjective + adverb", "body": "The bright sun shines brightly.", "emoji": "☀️"},
        ],
        "key_points": [
            "A noun names a person, place, thing or idea.",
            "A verb shows an action or state.",
            "An adjective describes a noun; an adverb describes a verb.",
        ],
        "class_tips": {
            "6": "Label the nouns and verbs in a sentence.",
            "7": "Find two adjectives in a newspaper headline.",
            "8": "Sort ten words into parts of speech.",
            "9": "Explain the difference between an adjective and an adverb.",
            "10": "Analyse a paragraph and label every part of speech.",
        },
    },
    {
        "slug": "tenses",
        "title": "Tenses",
        "subject": SUBJECT_ENGLISH,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "Clock3",
        "emoji": "⏰",
        "order": 2,
        "description": "Use present, past and future tenses accurately.",
        "explanation": (
            "Tense tells us when an action happens. Simple present describes "
            "habits and facts. Simple past describes completed actions. Simple "
            "future describes actions that will happen.\n\n"
            "Continuous tenses show an action in progress, and perfect tenses "
            "connect two moments in time."
        ),
        "examples": [
            {"title": "Present", "body": "She studies every evening.", "emoji": "📅"},
            {"title": "Past", "body": "She studied yesterday.", "emoji": "⬅️"},
            {"title": "Future", "body": "She will study tomorrow.", "emoji": "➡️"},
        ],
        "key_points": [
            "Tense shows the time of an action.",
            "Regular past forms usually add -ed.",
            "Use 'will' for the simple future.",
        ],
        "class_tips": {
            "6": "Write one sentence in each simple tense.",
            "7": "Change present sentences to past tense.",
            "8": "Use present continuous correctly.",
            "9": "Compare simple past and present perfect.",
            "10": "Write a paragraph using three different tenses.",
        },
    },
    {
        "slug": "active-passive-voice",
        "title": "Active and Passive Voice",
        "subject": SUBJECT_ENGLISH,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "ArrowLeftRight",
        "emoji": "🔄",
        "order": 3,
        "description": "Change the focus of a sentence without changing the meaning.",
        "explanation": (
            "In active voice, the subject does the action: 'Riya wrote a poem.' "
            "In passive voice, the action is done to the subject: 'A poem was "
            "written by Riya.'\n\n"
            "Passive voice is useful when the doer is unknown or less important. "
            "Most school writing uses active voice because it is clearer."
        ),
        "examples": [
            {"title": "Active", "body": "The chef cooked the meal.", "emoji": "👩‍🍳"},
            {"title": "Passive", "body": "The meal was cooked by the chef.", "emoji": "🍲"},
            {"title": "Unknown doer", "body": "The window was broken.", "emoji": "🪟"},
        ],
        "key_points": [
            "Active: subject + verb + object.",
            "Passive: object + be + past participle + by + subject.",
            "Only transitive verbs can usually be passive.",
        ],
        "class_tips": {
            "6": "Find the verb in an active sentence.",
            "7": "Change three active sentences to passive.",
            "8": "Change passive sentences back to active.",
            "9": "Explain when passive voice is useful.",
            "10": "Rewrite a news report in active voice.",
        },
    },
    {
        "slug": "direct-indirect-speech",
        "title": "Direct and Indirect Speech",
        "subject": SUBJECT_ENGLISH,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "Quote",
        "emoji": "💬",
        "order": 4,
        "description": "Report what someone said using direct or indirect speech.",
        "explanation": (
            "Direct speech repeats the exact words inside quotation marks: "
            "She said, 'I am tired.' Indirect speech reports the meaning without "
            "the exact words: She said that she was tired.\n\n"
            "When we change to indirect speech, pronouns and tenses often change. "
            "The reporting verb (said, told, asked) introduces the report."
        ),
        "examples": [
            {"title": "Direct", "body": "Rahul said, \"I will come tomorrow.\"", "emoji": "🗣️"},
            {"title": "Indirect", "body": "Rahul said that he would come the next day.", "emoji": "📝"},
            {"title": "Question", "body": "She asked if I was ready.", "emoji": "❓"},
        ],
        "key_points": [
            "Direct speech uses quotation marks.",
            "Indirect speech reports the words without quotation marks.",
            "Tenses and pronouns may shift back one step.",
        ],
        "class_tips": {
            "6": "Copy one sentence of direct speech.",
            "7": "Change one direct sentence into indirect speech.",
            "8": "Report a simple question.",
            "9": "Practice tense changes in reported speech.",
            "10": "Report a short conversation in indirect speech.",
        },
    },
    {
        "slug": "vocabulary-building",
        "title": "Vocabulary Building",
        "subject": SUBJECT_ENGLISH,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "Library",
        "emoji": "📖",
        "order": 5,
        "description": "Grow your word bank with synonyms, antonyms and context.",
        "explanation": (
            "A strong vocabulary helps you read faster and write more precisely. "
            "Synonyms are words with similar meanings, such as 'happy' and "
            "'joyful'. Antonyms are opposites, such as 'ancient' and 'modern'.\n\n"
            "Learn a word with its meaning, a synonym, an antonym and one example "
            "sentence. This makes the word easier to recall."
        ),
        "examples": [
            {"title": "Synonyms", "body": "brave = courageous", "emoji": "🦁"},
            {"title": "Antonyms", "body": "expand ≠ shrink", "emoji": "↔️"},
            {"title": "Context", "body": "The arid desert had very little rain.", "emoji": "🏜️"},
        ],
        "key_points": [
            "Synonyms have similar meanings.",
            "Antonyms have opposite meanings.",
            "Context clues help you guess an unfamiliar word.",
        ],
        "class_tips": {
            "6": "Learn five new words from a story.",
            "7": "Write a synonym for ten common words.",
            "8": "Write an antonym for ten words.",
            "9": "Use context clues to guess a word's meaning.",
            "10": "Use five new words in a short essay.",
        },
    },
    {
        "slug": "sentence-correction",
        "title": "Sentence Correction",
        "subject": SUBJECT_ENGLISH,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "CheckCheck",
        "emoji": "✅",
        "order": 6,
        "description": "Spot grammar mistakes and write cleaner sentences.",
        "explanation": (
            "A correct sentence follows grammar rules and makes sense. Common "
            "problems include missing capital letters, wrong verb forms, "
            "double negatives and punctuation errors.\n\n"
            "Read the sentence aloud, check the subject and verb, then check the "
            "spelling and punctuation."
        ),
        "examples": [
            {"title": "Verb agreement", "body": "She goes to school. (not She go)", "emoji": "🏫"},
            {"title": "Double negative", "body": "I did not see anyone. (not I didn't see nobody.)", "emoji": "🚫"},
            {"title": "Punctuation", "body": "Where are you going?", "emoji": "❓"},
        ],
        "key_points": [
            "Check that the subject and verb agree.",
            "Use only one negative word in a negative sentence.",
            "End questions with a question mark.",
        ],
        "class_tips": {
            "6": "Fix the capital letters in three sentences.",
            "7": "Choose the correct verb form.",
            "8": "Remove double negatives.",
            "9": "Correct a short paragraph.",
            "10": "Proofread your own writing and list the corrections.",
        },
    },
    {
        "slug": "reading-comprehension-secondary",
        "title": "Reading Comprehension",
        "subject": SUBJECT_ENGLISH,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "BookOpenCheck",
        "emoji": "📰",
        "order": 7,
        "description": "Find main ideas, details and inferences in a passage.",
        "explanation": (
            "Comprehension questions test whether you understand a passage, not "
            "just whether you can read the words. The main idea is what the "
            "passage is mostly about. A detail supports the main idea. An "
            "inference is a conclusion you draw from clues in the text.\n\n"
            "Read the passage twice. Underline the topic sentence and any words "
            "that answer the question."
        ),
        "examples": [
            {"title": "Main idea", "body": "What is the passage mostly about?", "emoji": "🎯"},
            {"title": "Detail", "body": "Which fact is stated in the passage?", "emoji": "🔍"},
            {"title": "Inference", "body": "What can you conclude from the last line?", "emoji": "💡"},
        ],
        "key_points": [
            "The main idea is the central message.",
            "Details support the main idea.",
            "Inferences use clues plus your own reasoning.",
        ],
        "class_tips": {
            "6": "Find the main idea of a short paragraph.",
            "7": "Underline two supporting details.",
            "8": "Answer a 'why' question using evidence.",
            "9": "Distinguish fact from opinion.",
            "10": "Write a one-paragraph summary of a passage.",
        },
    },
    {
        "slug": "basic-writing-skills",
        "title": "Basic Writing Skills",
        "subject": SUBJECT_ENGLISH,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "PenLine",
        "emoji": "✍️",
        "order": 8,
        "description": "Plan clear paragraphs, letters and short answers.",
        "explanation": (
            "Good writing is organised writing. A paragraph usually has a topic "
            "sentence, supporting sentences and a closing sentence. A formal "
            "letter has a clear purpose, polite language and a proper ending.\n\n"
            "Plan before you write: note your main idea, three supporting points "
            "and a conclusion. Then write, revise and proofread."
        ),
        "examples": [
            {"title": "Topic sentence", "body": "Trees are important for every living thing.", "emoji": "🌳"},
            {"title": "Supporting sentence", "body": "They give us oxygen and shade.", "emoji": "🍃"},
            {"title": "Formal ending", "body": "Yours sincerely, Riya", "emoji": "✉️"},
        ],
        "key_points": [
            "Start a paragraph with a clear topic sentence.",
            "Support the main idea with examples.",
            "Proofread for spelling, grammar and punctuation.",
        ],
        "class_tips": {
            "6": "Write a five-sentence paragraph about your school.",
            "7": "Write a short informal letter to a friend.",
            "8": "Write a formal letter asking for information.",
            "9": "Write a balanced paragraph with a clear conclusion.",
            "10": "Plan and write a 150-word argument on a school topic.",
        },
    },
    # ------------------------------------------------------------------ Secondary Mathematics
    {
        "slug": "integers",
        "title": "Integers",
        "subject": SUBJECT_MATHS,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "ArrowUpDown",
        "emoji": "🌡️",
        "order": 1,
        "description": "Work with positive and negative whole numbers.",
        "explanation": (
            "Integers are whole numbers that can be positive, negative or zero: "
            "... -3, -2, -1, 0, 1, 2, 3 ... We use them for temperatures, bank "
            "balances and positions above or below sea level.\n\n"
            "When adding integers with the same sign, add the numbers and keep "
            "the sign. When signs are different, subtract the smaller absolute "
            "value from the larger one and keep the sign of the larger value."
        ),
        "examples": [
            {"title": "Temperature", "body": "-5°C is colder than 2°C.", "emoji": "🌡️"},
            {"title": "Addition", "body": "-7 + 3 = -4", "emoji": "➕"},
            {"title": "Multiplication", "body": "-4 × -3 = 12", "emoji": "✖️"},
        ],
        "key_points": [
            "Integers include negative numbers and zero.",
            "Two negatives multiplied give a positive.",
            "A number line helps compare integers.",
        ],
        "class_tips": {
            "6": "Place -3, 0 and 4 on a number line.",
            "7": "Add and subtract small integers.",
            "8": "Multiply and divide integers.",
            "9": "Solve a word problem with negative numbers.",
            "10": "Simplify a mixed integer expression using order of operations.",
        },
    },
    {
        "slug": "fractions-decimals",
        "title": "Fractions and Decimals",
        "subject": SUBJECT_MATHS,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "Percent",
        "emoji": "🔟",
        "order": 2,
        "description": "Convert, compare and calculate with fractions and decimals.",
        "explanation": (
            "A fraction shows parts of a whole, such as 3/4. A decimal uses place "
            "value, such as 0.75. They can show the same amount.\n\n"
            "To convert a fraction to a decimal, divide the numerator by the "
            "denominator. To add fractions, first make the denominators the same."
        ),
        "examples": [
            {"title": "Convert", "body": "1/2 = 0.5", "emoji": "➗"},
            {"title": "Add", "body": "1/4 + 2/4 = 3/4", "emoji": "➕"},
            {"title": "Compare", "body": "0.6 > 0.45", "emoji": "⚖️"},
        ],
        "key_points": [
            "The denominator tells how many equal parts there are.",
            "Divide numerator by denominator to get a decimal.",
            "Line up decimal points when adding decimals.",
        ],
        "class_tips": {
            "6": "Convert 1/2, 1/4 and 1/5 to decimals.",
            "7": "Add fractions with the same denominator.",
            "8": "Add fractions with different denominators.",
            "9": "Multiply and divide fractions.",
            "10": "Solve a real-life problem using fractions and decimals.",
        },
    },
    {
        "slug": "percentages",
        "title": "Percentages",
        "subject": SUBJECT_MATHS,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "PercentCircle",
        "emoji": "💯",
        "order": 3,
        "description": "Find percentages and use them in everyday situations.",
        "explanation": (
            "Percent means 'per hundred'. 25% means 25 out of every 100, which is "
            "the same as 1/4 or 0.25.\n\n"
            "To find a percentage of a number, change the percentage to a decimal "
            "and multiply. For example, 20% of 50 = 0.20 × 50 = 10."
        ),
        "examples": [
            {"title": "10%", "body": "10% of 80 = 8", "emoji": "💯"},
            {"title": "25%", "body": "25% of 40 = 10", "emoji": "🍕"},
            {"title": "Increase", "body": "A ₹200 item with 10% off costs ₹180.", "emoji": "🏷️"},
        ],
        "key_points": [
            "Percent means per hundred.",
            "Convert a percentage to a decimal before multiplying.",
            "Discounts and interest often use percentages.",
        ],
        "class_tips": {
            "6": "Find 10% of 50 and 100.",
            "7": "Find 25% of 80.",
            "8": "Calculate a discount.",
            "9": "Calculate percentage increase and decrease.",
            "10": "Solve a percentage word problem with two steps.",
        },
    },
    {
        "slug": "ratio-proportion",
        "title": "Ratio and Proportion",
        "subject": SUBJECT_MATHS,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "Scale",
        "emoji": "⚖️",
        "order": 4,
        "description": "Compare quantities and solve proportion problems.",
        "explanation": (
            "A ratio compares two quantities, such as 3 boys to 2 girls (3:2). "
            "A proportion says two ratios are equal, such as 3:2 = 6:4.\n\n"
            "To share an amount in a ratio, add the parts, divide the total by the "
            "number of parts, then multiply by each part."
        ),
        "examples": [
            {"title": "Simplify", "body": "8:12 = 2:3", "emoji": "➗"},
            {"title": "Share", "body": "₹100 in 2:3 = ₹40 and ₹60", "emoji": "💰"},
            {"title": "Proportion", "body": "2:5 = 4:10", "emoji": "⚖️"},
        ],
        "key_points": [
            "Ratios compare quantities of the same kind.",
            "Divide both parts by the same number to simplify.",
            "Proportions state that two ratios are equal.",
        ],
        "class_tips": {
            "6": "Write the ratio of 4 red balls to 6 blue balls.",
            "7": "Simplify 10:15.",
            "8": "Share 60 sweets in the ratio 2:3.",
            "9": "Solve a direct proportion problem.",
            "10": "Use ratio to solve a map-scale problem.",
        },
    },
    {
        "slug": "algebra",
        "title": "Algebra",
        "subject": SUBJECT_MATHS,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "Variable",
        "emoji": "🔤",
        "order": 5,
        "description": "Use letters to represent unknown numbers and simplify expressions.",
        "explanation": (
            "Algebra uses letters such as x and y to stand for unknown numbers. "
            "An expression such as 2x + 3 means 'two times x, plus three'.\n\n"
            "We simplify expressions by collecting like terms: 3x + 2x = 5x. We "
            "evaluate an expression by replacing the letter with a number."
        ),
        "examples": [
            {"title": "Collect terms", "body": "3x + 2x = 5x", "emoji": "🧩"},
            {"title": "Evaluate", "body": "If x = 4, then 2x + 3 = 11.", "emoji": "🔢"},
            {"title": "Expand", "body": "2(x + 3) = 2x + 6", "emoji": "📦"},
        ],
        "key_points": [
            "A letter can represent an unknown number.",
            "Only like terms can be added or subtracted.",
            "Substitute carefully when evaluating.",
        ],
        "class_tips": {
            "6": "Write an expression for '5 more than x'.",
            "7": "Simplify 4x + 3x.",
            "8": "Evaluate 3x + 2 when x = 5.",
            "9": "Expand 3(x + 4).",
            "10": "Factorise a simple quadratic expression.",
        },
    },
    {
        "slug": "geometry",
        "title": "Geometry",
        "subject": SUBJECT_MATHS,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "Compass",
        "emoji": "📐",
        "order": 6,
        "description": "Explore angles, triangles, circles and area.",
        "explanation": (
            "Geometry is the mathematics of shape, size and space. Angles are "
            "measured in degrees. A right angle is 90°, a straight line is 180° "
            "and a full turn is 360°.\n\n"
            "The angles inside a triangle add up to 180°. Area measures the space "
            "inside a shape, and perimeter measures the distance around it."
        ),
        "examples": [
            {"title": "Triangle", "body": "60° + 60° + 60° = 180°", "emoji": "🔺"},
            {"title": "Rectangle area", "body": "length × width = 5 × 3 = 15 cm²", "emoji": "🟦"},
            {"title": "Circle", "body": "Circumference = 2πr", "emoji": "⭕"},
        ],
        "key_points": [
            "Angles in a triangle add to 180°.",
            "Area of a rectangle = length × width.",
            "Perimeter is the total distance around a shape.",
        ],
        "class_tips": {
            "6": "Measure three angles with a protractor.",
            "7": "Find the missing angle in a triangle.",
            "8": "Calculate the area of a rectangle.",
            "9": "Use the Pythagorean theorem in a right triangle.",
            "10": "Solve a circle area or circumference problem.",
        },
    },
    {
        "slug": "linear-equations",
        "title": "Linear Equations",
        "subject": SUBJECT_MATHS,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "Equal",
        "emoji": "🟰",
        "order": 7,
        "description": "Solve equations by keeping both sides balanced.",
        "explanation": (
            "An equation says two expressions are equal, such as x + 3 = 7. To "
            "solve it, we find the value of x that makes the equation true.\n\n"
            "Whatever we do to one side, we must do to the other side. For "
            "2x + 4 = 10, subtract 4 from both sides to get 2x = 6, then divide "
            "both sides by 2 to get x = 3."
        ),
        "examples": [
            {"title": "One step", "body": "x + 3 = 7 → x = 4", "emoji": "🟰"},
            {"title": "Two steps", "body": "2x + 4 = 10 → x = 3", "emoji": "🧮"},
            {"title": "Check", "body": "2(3) + 4 = 10 ✓", "emoji": "✅"},
        ],
        "key_points": [
            "Keep the equation balanced.",
            "Undo addition with subtraction, and multiplication with division.",
            "Substitute your answer back to check it.",
        ],
        "class_tips": {
            "6": "Solve x + 5 = 12.",
            "7": "Solve 3x = 15.",
            "8": "Solve 2x + 3 = 11.",
            "9": "Solve an equation with x on both sides.",
            "10": "Form and solve an equation from a word problem.",
        },
    },
    {
        "slug": "basic-statistics",
        "title": "Basic Statistics",
        "subject": SUBJECT_MATHS,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "BarChart3",
        "emoji": "📊",
        "order": 8,
        "description": "Find mean, median, mode and range from data.",
        "explanation": (
            "Statistics helps us understand data. The mean is the average: add "
            "all values and divide by how many there are. The median is the "
            "middle value when the data is ordered. The mode is the most common "
            "value, and the range is the largest minus the smallest.\n\n"
            "These measures help us compare sets of numbers and describe what is "
            "typical."
        ),
        "examples": [
            {"title": "Mean", "body": "2, 4, 6 → (2+4+6)/3 = 4", "emoji": "📊"},
            {"title": "Median", "body": "1, 3, 5, 7 → middle two average = 4", "emoji": "🎯"},
            {"title": "Range", "body": "Largest 9, smallest 2 → range 7", "emoji": "↔️"},
        ],
        "key_points": [
            "Mean = total ÷ number of values.",
            "Median = middle value after ordering.",
            "Range = largest value − smallest value.",
        ],
        "class_tips": {
            "6": "Find the mean of 2, 4 and 6.",
            "7": "Find the median of five numbers.",
            "8": "Find the mode and range of a data set.",
            "9": "Compare two data sets using mean and range.",
            "10": "Calculate a missing value from a given mean.",
        },
    },
    {
        "slug": "mensuration",
        "title": "Mensuration",
        "subject": SUBJECT_MATHS,
        "level": "Secondary",
        "classes": SECONDARY_CLASSES,
        "icon": "Box",
        "emoji": "📦",
        "order": 9,
        "description": "Find perimeter, area and volume of common shapes.",
        "explanation": (
            "Mensuration is the mathematics of measuring shapes. Perimeter is "
            "the distance around a shape. Area is the amount of surface it "
            "covers, measured in square units. Volume is the space inside a "
            "solid, measured in cubic units.\n\n"
            "Useful formulas: perimeter of a rectangle = 2(l + w); area of a "
            "rectangle = l × w; area of a triangle = ½ × base × height; volume "
            "of a cuboid = l × w × h. Always write the correct unit with your "
            "answer, such as cm, cm² or cm³."
        ),
        "examples": [
            {"title": "Perimeter", "body": "Rectangle 6 cm by 4 cm → 2(6 + 4) = 20 cm", "emoji": "📐"},
            {"title": "Area", "body": "Triangle base 8 cm, height 5 cm → ½ × 8 × 5 = 20 cm²", "emoji": "🔺"},
            {"title": "Volume", "body": "Cuboid 3 cm × 4 cm × 5 cm → 60 cm³", "emoji": "📦"},
        ],
        "key_points": [
            "Perimeter is the distance around the outside.",
            "Area of a rectangle = length × width.",
            "Area of a triangle = ½ × base × height.",
            "Volume of a cuboid = length × width × height.",
            "Use cm² for area and cm³ for volume.",
        ],
        "class_tips": {
            "6": "Find the perimeter of a rectangle 7 cm by 3 cm.",
            "7": "Find the area of a square with side 6 cm.",
            "8": "Find the area of a triangle with base 10 cm and height 4 cm.",
            "9": "Find the volume of a cuboid 5 cm × 3 cm × 2 cm.",
            "10": "Find the cost of painting a wall using its area.",
        },
    },
]


TOPIC_BY_SLUG = {topic["slug"]: topic for topic in TOPICS}


def topics_for_class(class_level: int, subject: str | None = None):
    """Return topic documents that match a class and optional subject."""
    level = level_for_class(class_level)
    items = [topic for topic in TOPICS if topic["level"] == level]
    if subject:
        items = [topic for topic in items if topic["subject"] == subject]
    return sorted(items, key=lambda item: (item["subject"], item["order"]))


def topic_document(topic, class_level: int | None = None):
    """Convert a curriculum entry into the shape stored in MongoDB."""
    doc = {
        "_id": topic["slug"],
        "slug": topic["slug"],
        "title": topic["title"],
        "subject": topic["subject"],
        "level": topic["level"],
        "classes": topic["classes"],
        "icon": topic["icon"],
        "emoji": topic["emoji"],
        "order": topic["order"],
        "description": topic["description"],
        "explanation": topic["explanation"],
        "examples": topic["examples"],
        "key_points": topic["key_points"],
        "class_tips": topic["class_tips"],
        "estimated_minutes": 7 if topic["level"] == "Primary" else 10,
    }
    if class_level:
        doc["class_tip"] = topic["class_tips"].get(str(class_level), "")
    return doc


# ---------------------------------------------------------------------------
# Question helpers
# ---------------------------------------------------------------------------
def _shuffle_with_correct(correct, distractors):
    """Return four unique options and the index of the correct one."""
    options = []
    for item in [correct, *distractors]:
        text = str(item)
        if text not in options:
            options.append(text)
    # Fallback padding for accidental duplicates.
    filler = 1
    while len(options) < 4:
        candidate = f"{correct} {'' if filler == 1 else filler}".strip()
        if candidate not in options:
            options.append(candidate)
        filler += 1
    random.shuffle(options)
    return options, options.index(str(correct))


def _numeric_options(correct, distractors=None, low=None):
    """Build four numeric options around a correct answer."""
    correct = int(correct)
    candidates = list(distractors or [])
    for step in (1, 2, 3, 5, 10):
        candidates.extend([correct + step, correct - step])
    options = []
    for value in [correct, *candidates]:
        value = int(value)
        if low is not None and value < low:
            continue
        if str(value) not in options:
            options.append(str(value))
        if len(options) == 4:
            break
    while len(options) < 4:
        value = correct + len(options) + 1
        if str(value) not in options:
            options.append(str(value))
    random.shuffle(options)
    return options, options.index(str(correct))


def _make(topic_slug, difficulty, question, options, correct_index, explanation,
          simpler_example=None):
    return {
        "id": f"{topic_slug}-{difficulty}-{random.randint(100000, 999999)}",
        "topic_slug": topic_slug,
        "difficulty": difficulty,
        "question": question,
        "options": options,
        "correct_index": correct_index,
        "explanation": explanation,
        "simpler_example": simpler_example or explanation,
    }


def _range_for(class_level, difficulty, base_primary=20, base_secondary=50):
    """A rough number ceiling that grows with class and difficulty."""
    if class_level <= 2:
        ceiling = 10
    elif class_level <= 5:
        ceiling = 20 + class_level * 10
    else:
        ceiling = base_secondary + class_level * 10
    factor = {"easy": 0.6, "medium": 1.0, "hard": 1.6}.get(difficulty, 1.0)
    return max(5, int(ceiling * factor))


# ---------------------------------------------------------------------------
# Primary Mathematics generators
# ---------------------------------------------------------------------------
def _q_counting(c, d):
    ceiling = 10 if c <= 2 else 20 if c <= 4 else 50
    emoji = random.choice(["⭐", "🍎", "🐰", "🎈", "🍪", "🌸"])
    if d == "easy":
        n = random.randint(3, min(ceiling, 12))
        options, index = _numeric_options(n, low=0)
        return _make(
            "counting", d,
            f"How many {emoji} do you see?  {emoji * n}",
            options, index,
            f"Count one by one: there are {n} {emoji}.",
            f"Touch each {emoji} and say a number aloud: 1, 2, 3 ...",
        )
    if d == "medium":
        step = random.choice([2, 2, 5, 10])
        start = random.randint(1, max(2, ceiling // 2))
        seq = [start + step * i for i in range(4)]
        missing = random.randint(1, 3)
        shown = ", ".join("__" if i == missing else str(value) for i, value in enumerate(seq))
        options, index = _numeric_options(seq[missing], low=0)
        return _make(
            "counting", d,
            f"What number is missing?  {shown}",
            options, index,
            f"The pattern goes up by {step}. The missing number is {seq[missing]}.",
            f"Add {step} each time: {seq[0]}, {seq[0] + step}, ...",
        )
    n = random.randint(2, ceiling)
    direction = random.choice(["after", "before"])
    answer = n + 1 if direction == "after" else max(0, n - 1)
    options, index = _numeric_options(answer, low=0)
    return _make(
        "counting", d,
        f"Which number comes {direction} {n}?",
        options, index,
        f"On a number line, {answer} comes {direction} {n}.",
        f"Count forwards or backwards from {n}.",
    )


def _q_addition(c, d):
    ceiling = _range_for(c, d, base_secondary=40)
    if d == "easy":
        a = random.randint(1, max(3, min(ceiling, 10)))
        b = random.randint(1, max(3, min(ceiling, 10)))
    elif d == "medium":
        a = random.randint(10, max(20, ceiling))
        b = random.randint(1, max(10, ceiling // 2))
    else:
        a = random.randint(20, max(50, ceiling * 2))
        b = random.randint(10, max(20, ceiling))
    total = a + b
    options, index = _numeric_options(total, low=0)
    return _make(
        "addition", d,
        f"What is {a} + {b}?",
        options, index,
        f"Add the ones, then the tens: {a} + {b} = {total}.",
        f"Start at {a} and count on {b} steps.",
    )


def _q_subtraction(c, d):
    ceiling = _range_for(c, d, base_secondary=40)
    if d == "easy":
        a = random.randint(3, max(5, min(ceiling, 10)))
        b = random.randint(1, a)
    elif d == "medium":
        a = random.randint(15, max(25, ceiling))
        b = random.randint(1, max(10, a - 1))
    else:
        a = random.randint(50, max(80, ceiling * 2))
        b = random.randint(10, max(20, a - 1))
    answer = a - b
    options, index = _numeric_options(answer, low=0)
    return _make(
        "subtraction", d,
        f"What is {a} - {b}?",
        options, index,
        f"Subtract {b} from {a}. The difference is {answer}.",
        f"Count back {b} steps from {a}.",
    )


def _q_multiplication(c, d):
    if c <= 2 or d == "easy":
        a, b = random.randint(1, 5), random.randint(1, 10)
    elif d == "medium":
        a, b = random.randint(2, 10), random.randint(2, 10)
    else:
        a, b = random.randint(11, 30), random.randint(2, 9)
    product = a * b
    options, index = _numeric_options(product, low=0)
    if d == "hard" and random.random() < 0.4:
        missing = random.choice([a, b])
        answer = missing
        options, index = _numeric_options(answer, low=1)
        return _make(
            "multiplication", d,
            f"Which number makes this true?  __ × {b if missing == a else a} = {product}",
            options, index,
            f"{a} × {b} = {product}, so the missing factor is {missing}.",
            f"Use the times table: {product} divided by {(b if missing == a else a)} equals {answer}.",
        )
    return _make(
        "multiplication", d,
        f"What is {a} × {b}?",
        options, index,
        f"{a} groups of {b} make {product}.",
        f"Repeated addition: " + " + ".join([str(b)] * min(a, 5)) + (f" ... = {product}" if a > 5 else f" = {product}"),
    )


def _q_division(c, d):
    divisor = random.randint(2, 5 if d == "easy" else 9)
    quotient = random.randint(1, 5 if d == "easy" else 10)
    dividend = divisor * quotient
    options, index = _numeric_options(quotient, low=1)
    if d == "hard" and random.random() < 0.45:
        missing_divisor = divisor
        options, index = _numeric_options(missing_divisor, low=1)
        return _make(
            "division", d,
            f"Which number makes this true?  {dividend} ÷ __ = {quotient}",
            options, index,
            f"{dividend} ÷ {missing_divisor} = {quotient}, because {missing_divisor} × {quotient} = {dividend}.",
            f"Think: {quotient} equal groups make {dividend}.",
        )
    return _make(
        "division", d,
        f"What is {dividend} ÷ {divisor}?",
        options, index,
        f"{dividend} shared into {divisor} equal groups gives {quotient} in each group.",
        f"Use multiplication: {divisor} × ? = {dividend}.",
    )


def _q_number_patterns(c, d):
    step = random.choice([1, 2, 5]) if d == "easy" else random.choice([3, 4, 6, 10]) if d == "medium" else random.choice([7, 8, 9, 12])
    start = random.randint(0, 20)
    seq = [start + step * i for i in range(5)]
    missing = random.randint(1, 4)
    shown = ", ".join("__" if i == missing else str(value) for i, value in enumerate(seq))
    options, index = _numeric_options(seq[missing], low=0)
    return _make(
        "number-patterns", d,
        f"Find the missing number:  {shown}",
        options, index,
        f"The pattern adds {step} each time. The missing number is {seq[missing]}.",
        f"Look at two numbers next to each other and find the difference.",
    )


def _q_shapes(c, d):
    shapes = [
        ("triangle", 3, "🔺"), ("square", 4, "🟦"), ("rectangle", 4, "▭"),
        ("circle", 0, "⭕"), ("pentagon", 5, "⬠"), ("hexagon", 6, "⬡"),
    ]
    name, sides, emoji = random.choice(shapes)
    if d == "easy":
        correct = name
        distractors = [item[0] for item in shapes if item[0] != name][:3]
        question = f"Which shape is {emoji}?"
        explanation = f"{emoji} is a {name}."
    elif d == "medium":
        correct = str(sides) if sides else "0"
        distractors = [value for value in ["3", "4", "5", "6", "0"] if value != correct][:3]
        question = f"How many sides does a {name} have?"
        explanation = f"A {name} has {sides} straight sides."
    else:
        pairs = [
            ("Which shape has 4 equal sides?", "square", ["rectangle", "triangle", "circle"]),
            ("Which shape has no corners?", "circle", ["square", "triangle", "rectangle"]),
            ("Which shape has 3 sides?", "triangle", ["square", "circle", "rectangle"]),
        ]
        question, correct, distractors = random.choice(pairs)
        explanation = f"The correct answer is {correct}."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("basic-shapes", d, question, options, index, explanation,
                 "Count the sides and corners carefully.")


def _q_fractions(c, d):
    if d == "easy":
        n = random.choice([2, 3, 4, 5, 6, 8])
        k = random.randint(1, n - 1)
        correct = f"{k}/{n}"
        distractors = [f"{n}/{k}", f"{k}/{n - k}", f"{n - k}/{n}"]
        question = (
            f"A pizza is cut into {n} equal parts. You eat {k} part(s). "
            "What fraction of the pizza did you eat?"
        )
        explanation = f"You ate {k} out of {n} equal parts, so the fraction is {k}/{n}."
        simpler = "The bottom number is the total number of equal parts."
    elif d == "medium":
        pairs = [
            ("Which fraction is equal to 1/2?", "2/4", ["1/3", "2/5", "3/4"]),
            ("Which fraction is equal to 1/4?", "2/8", ["1/2", "2/6", "3/8"]),
            ("Which fraction is greater: 1/2 or 1/4?", "1/2", ["1/4", "They are equal", "Cannot compare"]),
        ]
        question, correct, distractors = random.choice(pairs)
        explanation = f"{correct} is the correct choice."
        simpler = "Draw a shape and shade the fractions to compare them."
    else:
        n = random.choice([4, 5, 6, 8, 10])
        a = random.randint(1, n - 2)
        b = random.randint(1, n - a - 1)
        correct = f"{a + b}/{n}"
        distractors = [f"{a + b}/{n + n}", f"{a * b}/{n}", f"{a + b + 1}/{n}"]
        question = f"What is {a}/{n} + {b}/{n}?"
        explanation = f"The denominators are the same, so add the numerators: {a} + {b} = {a + b}. The answer is {a + b}/{n}."
        simpler = "When the bottom numbers are the same, add only the top numbers."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("fractions", d, question, options, index, explanation, simpler)


def _q_measurement(c, d):
    if d == "easy":
        items = [
            ("pencil", "cm", ["kg", "L", "minutes"]),
            ("school bag", "kg", ["cm", "mL", "hours"]),
            ("water bottle", "L", ["cm", "g", "days"]),
            ("classroom door", "m", ["g", "mL", "seconds"]),
        ]
        item, correct, distractors = random.choice(items)
        question = f"Which unit is best for measuring a {item}?"
        explanation = f"A {item} is measured in {correct}."
        simpler = "Length uses cm or m, weight uses g or kg, and capacity uses mL or L."
        options, index = _shuffle_with_correct(correct, distractors)
        return _make("measurement", d, question, options, index, explanation, simpler)
    if d == "medium":
        big, small, factor = random.choice([("m", "cm", 100), ("kg", "g", 1000), ("L", "mL", 1000)])
        amount = random.randint(2, 9)
        answer = amount * factor
        question = f"How many {small} are in {amount} {big}?"
        explanation = f"1 {big} = {factor} {small}, so {amount} × {factor} = {answer} {small}."
        simpler = f"Multiply by {factor} to change {big} into {small}."
        options, index = _numeric_options(answer, low=0)
        return _make("measurement", d, question, options, index, explanation, simpler)
    item, big, small, factor = random.choice(
        [("rope", "m", "cm", 100), ("bag of rice", "kg", "g", 1000), ("jug of juice", "L", "mL", 1000)]
    )
    whole = random.randint(1, 4)
    extra = random.choice([10, 20, 25, 40, 50])
    answer = whole * factor + extra
    question = f"A {item} measures {whole} {big} {extra} {small}. How many {small} is that in total?"
    explanation = (
        f"{whole} {big} = {whole * factor} {small}. Add {extra} {small}: "
        f"{whole * factor} + {extra} = {answer} {small}."
    )
    simpler = f"Change the {big} into {small} first, then add the extra {small}."
    options, index = _numeric_options(answer, low=0)
    return _make("measurement", d, question, options, index, explanation, simpler)


def _clock(hour, minutes):
    hour = hour % 12 or 12
    return f"{hour}:{minutes:02d}"


def _q_time_money(c, d):
    if d == "easy":
        if random.random() < 0.5:
            hour = random.randint(1, 11)
            correct = f"{hour} o'clock"
            distractors = [f"{hour % 12 + 1} o'clock", f"{hour}:30", f"{hour - 1 if hour > 1 else 12} o'clock"]
            question = (
                f"The short hand points to {hour} and the long hand points to 12. "
                "What time is it?"
            )
            explanation = f"The long hand on 12 means o'clock, so the time is {correct}."
            simpler = "The short hand tells the hour and the long hand on 12 means o'clock."
            options, index = _shuffle_with_correct(correct, distractors)
            return _make("time-and-money", d, question, options, index, explanation, simpler)
        a = random.choice([5, 10, 20, 25, 50])
        b = random.choice([5, 10, 20, 25, 50])
        answer = a + b
        question = f"You have ₹{a} and ₹{b}. How much money do you have in total?"
        explanation = f"Add the amounts: ₹{a} + ₹{b} = ₹{answer}."
        simpler = "Add the rupees together to find the total."
        options, index = _numeric_options(answer, low=0)
        return _make("time-and-money", d, question, options, index, explanation, simpler)
    if d == "medium":
        if random.random() < 0.5:
            hour = random.randint(1, 10)
            duration = random.choice([15, 30, 45, 60])
            end_minutes = duration % 60
            correct = _clock(hour + duration // 60, end_minutes)
            candidates = [
                _clock(hour, (duration + 15) % 60),
                _clock(hour + 1, end_minutes),
                _clock(hour + 2, (end_minutes + 15) % 60),
                _clock(hour, 0),
            ]
            distractors = []
            for value in candidates:
                if value != correct and value not in distractors:
                    distractors.append(value)
                if len(distractors) == 3:
                    break
            question = (
                f"A lesson starts at {_clock(hour, 0)} and lasts {duration} minutes. "
                "What time does it end?"
            )
            explanation = f"Add {duration} minutes to {_clock(hour, 0)}. The lesson ends at {correct}."
            simpler = "30 minutes is half an hour and 60 minutes is one whole hour."
            options, index = _shuffle_with_correct(correct, distractors)
            return _make("time-and-money", d, question, options, index, explanation, simpler)
        cost = random.choice([25, 35, 40, 45, 55, 65])
        paid = random.choice([100, 100, 200])
        answer = paid - cost
        question = f"An item costs ₹{cost}. You pay with ₹{paid}. How much change do you get?"
        explanation = f"Change = amount paid − cost = ₹{paid} − ₹{cost} = ₹{answer}."
        simpler = "Subtract the cost from the money you paid."
        options, index = _numeric_options(answer, low=0)
        return _make("time-and-money", d, question, options, index, explanation, simpler)
    if random.random() < 0.5:
        start_hour = random.randint(1, 8)
        start_minutes = random.choice([0, 15, 30])
        end_hour = start_hour + random.randint(1, 3)
        end_minutes = random.choice([0, 15, 30, 45])
        start_total = start_hour * 60 + start_minutes
        end_total = end_hour * 60 + end_minutes
        answer = end_total - start_total
        question = (
            f"A film starts at {_clock(start_hour, start_minutes)} and ends at "
            f"{_clock(end_hour, end_minutes)}. How many minutes long is the film?"
        )
        explanation = (
            f"From {_clock(start_hour, start_minutes)} to {_clock(end_hour, end_minutes)} "
            f"is {answer} minutes."
        )
        simpler = "Count the whole hours first (60 minutes each), then add the extra minutes."
        options, index = _numeric_options(answer, low=0)
        return _make("time-and-money", d, question, options, index, explanation, simpler)
    notebook = random.choice([25, 30, 35, 40])
    pen = random.choice([10, 15, 18, 20])
    count = random.choice([2, 3])
    answer = notebook * count + pen
    question = (
        f"A notebook costs ₹{notebook} and a pen costs ₹{pen}. "
        f"How much do {count} notebooks and 1 pen cost in total?"
    )
    explanation = (
        f"{count} notebooks cost {count} × ₹{notebook} = ₹{notebook * count}. "
        f"Add the pen: ₹{notebook * count} + ₹{pen} = ₹{answer}."
    )
    simpler = "Find the cost of the notebooks first, then add the pen."
    options, index = _numeric_options(answer, low=0)
    return _make("time-and-money", d, question, options, index, explanation, simpler)


# ---------------------------------------------------------------------------
# Secondary Mathematics generators
# ---------------------------------------------------------------------------
def _q_integers(c, d):
    if d == "easy":
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        answer = a + b
        question = f"What is {a} + ({b})?"
        explanation = f"{a} + ({b}) = {answer}."
        simpler = "Use a number line: start at the first number and move right for a positive number, left for a negative number."
    elif d == "medium":
        a = random.randint(-9, 9)
        b = random.randint(-9, 9)
        answer = a * b
        question = f"What is {a} × ({b})?"
        explanation = f"{a} × ({b}) = {answer}. Two negative signs give a positive result."
        simpler = "Multiply the numbers first, then decide the sign."
    else:
        a = random.randint(-8, 8)
        b = random.randint(2, 8)
        cval = random.randint(1, 6)
        answer = a + b * cval
        question = f"What is {a} + {b} × {cval}?"
        explanation = f"Use order of operations: {b} × {cval} = {b * cval}, then {a} + {b * cval} = {answer}."
        simpler = "Multiplication comes before addition."
    options, index = _numeric_options(answer)
    return _make("integers", d, question, options, index, explanation, simpler)


def _q_fractions_decimals(c, d):
    if d == "easy":
        pairs = [("1/2", "0.5"), ("1/4", "0.25"), ("3/4", "0.75"), ("1/5", "0.2"), ("1/10", "0.1")]
        fraction, decimal = random.choice(pairs)
        correct = decimal
        distractors = [value for _, value in pairs if value != decimal][:3]
        question = f"What is {fraction} as a decimal?"
        explanation = f"Divide the top number by the bottom number: {fraction} = {decimal}."
        simpler = "The line in a fraction means divide."
    elif d == "medium":
        n = random.choice([4, 5, 6, 8, 10])
        a = random.randint(1, n - 2)
        b = random.randint(1, n - a)
        correct = f"{a + b}/{n}"
        distractors = [f"{a + b}/{n + 1}", f"{a * b}/{n}", f"{a + b + 1}/{n}"]
        question = f"What is {a}/{n} + {b}/{n}?"
        explanation = f"Add the numerators because the denominators match: {a} + {b} = {a + b}. The answer is {correct}."
        simpler = "Same denominator? Add the top numbers only."
    else:
        whole = random.choice([12, 20, 24, 30, 40])
        n = random.choice([3, 4, 5, 6])
        correct = str(whole // n)
        distractors = [str(whole // n + 1), str(whole // n - 1), str(whole)]
        question = f"What is 1/{n} of {whole}?"
        explanation = f"Divide {whole} into {n} equal parts: {whole} ÷ {n} = {whole // n}."
        simpler = "'Of' can mean multiply: 1/{n} × {whole}."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("fractions-decimals", d, question, options, index, explanation, simpler)


def _q_percentages(c, d):
    if d == "easy":
        percent = random.choice([10, 50, 100])
        number = random.choice([20, 40, 50, 60, 80, 100])
    elif d == "medium":
        percent = random.choice([20, 25, 50, 75])
        number = random.choice([20, 40, 60, 80, 100, 120])
    else:
        percent = random.choice([15, 20, 25, 30, 40])
        number = random.choice([80, 120, 150, 200, 240])
    answer = int(number * percent / 100)
    options, index = _numeric_options(answer, low=0)
    question = f"What is {percent}% of {number}?"
    explanation = f"{percent}% = {percent / 100}, and {number} × {percent / 100} = {answer}."
    simpler = f"10% of {number} is {number // 10}. Use that to build {percent}%."
    return _make("percentages", d, question, options, index, explanation, simpler)


def _q_ratio(c, d):
    if d == "easy":
        a = random.randint(2, 6)
        b = random.randint(2, 6)
        factor = random.randint(2, 5)
        correct = f"{a}:{b}"
        distractors = [f"{a + 1}:{b}", f"{a}:{b + 1}", f"{b}:{a}"]
        question = f"Simplify the ratio {a * factor}:{b * factor}."
        explanation = f"Divide both parts by {factor}: {a * factor}:{b * factor} = {a}:{b}."
        simpler = "Divide both numbers by the same common factor."
    elif d == "medium":
        total = random.choice([30, 40, 60, 80, 100])
        a, b = random.choice([(2, 3), (1, 4), (3, 5), (2, 5)])
        part = total // (a + b)
        correct = str(a * part)
        distractors = [str(b * part), str(part), str(total - a * part + 1)]
        question = f"Divide {total} in the ratio {a}:{b}. What is the smaller share?"
        explanation = f"There are {a + b} parts. One part is {total} ÷ {a + b} = {part}. The smaller share is {min(a, b)} × {part} = {min(a, b) * part}."
        simpler = "Add the ratio parts first, then divide the total by that sum."
    else:
        a, b = random.choice([(2, 5), (3, 4), (5, 7), (4, 9)])
        factor = random.randint(2, 6)
        correct = str(b * factor)
        distractors = [str(b + factor), str(a * factor), str(b * factor + 1)]
        question = f"If {a}:{b} = {a * factor}:x, what is x?"
        explanation = f"The first part is multiplied by {factor}: {a} × {factor} = {a * factor}. So x = {b} × {factor} = {b * factor}."
        simpler = "Find what the first ratio number was multiplied by, then do the same to the second."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("ratio-proportion", d, question, options, index, explanation, simpler)


def _q_algebra(c, d):
    if d == "easy":
        a = random.randint(2, 6)
        b = random.randint(2, 6)
        correct = f"{a + b}x"
        distractors = [f"{a * b}x", f"{a + b}", f"{abs(a - b)}x"]
        question = f"Simplify {a}x + {b}x."
        explanation = f"Add the coefficients: {a} + {b} = {a + b}. The answer is {a + b}x."
        simpler = "Think of x as an object: 3 apples + 2 apples = 5 apples."
    elif d == "medium":
        a = random.randint(2, 6)
        b = random.randint(1, 9)
        x = random.randint(1, 6)
        correct = str(a * x + b)
        distractors = [str(a * x), str((a + x) * b), str(a + x + b)]
        question = f"If x = {x}, what is {a}x + {b}?"
        explanation = f"Replace x with {x}: {a} × {x} + {b} = {a * x} + {b} = {a * x + b}."
        simpler = "Put the number in place of x, then follow order of operations."
    else:
        a = random.randint(2, 5)
        b = random.randint(2, 7)
        correct = f"{a * b}x + {a * b}"
        distractors = [f"{a}x + {a * b}", f"{a * b}x + {b}", f"{a + b}x + {a * b}"]
        question = f"Expand {a}(x + {b})."
        explanation = f"Multiply each term inside the bracket by {a}: {a}x + {a * b}."
        simpler = "Multiply the outside number by every term inside the brackets."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("algebra", d, question, options, index, explanation, simpler)


def _q_geometry(c, d):
    if d == "easy":
        a = random.choice([40, 50, 60, 70])
        b = random.choice([40, 50, 60, 70])
        third = 180 - a - b
        correct = f"{third}°"
        distractors = [f"{third + 10}°", f"{180 - third}°", f"{a + b}°"]
        question = f"Two angles of a triangle are {a}° and {b}°. What is the third angle?"
        explanation = f"The angles of a triangle add to 180°. 180 - {a} - {b} = {third}°."
        simpler = "Add the two known angles, then subtract from 180."
    elif d == "medium":
        length = random.randint(4, 15)
        width = random.randint(3, 12)
        correct = str(length * width)
        distractors = [str(2 * (length + width)), str(length + width), str(length * width + 2)]
        question = f"A rectangle is {length} cm long and {width} cm wide. What is its area?"
        explanation = f"Area of a rectangle = length × width = {length} × {width} = {length * width} cm²."
        simpler = "Area is the number of unit squares inside the shape."
    else:
        radius = random.choice([7, 14, 21])
        correct = str(round(2 * 3.14 * radius, 2))
        distractors = [str(round(3.14 * radius * radius, 2)), str(round(3.14 * radius, 2)), str(round(2 * radius, 2))]
        question = f"What is the circumference of a circle with radius {radius} cm? (Use π ≈ 3.14)"
        explanation = f"Circumference = 2πr = 2 × 3.14 × {radius} = {correct} cm."
        simpler = "Circumference is the distance around the circle. Use 2πr."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("geometry", d, question, options, index, explanation, simpler)


def _q_linear_equations(c, d):
    if d == "easy":
        a = random.randint(1, 10)
        x = random.randint(1, 10)
        b = x + a
        correct = str(x)
        distractors = [str(b + a), str(b - a + 1), str(a)]
        question = f"Solve x + {a} = {b}."
        explanation = f"Subtract {a} from both sides: x = {b} - {a} = {x}."
        simpler = "Undo the addition with subtraction."
    elif d == "medium":
        a = random.randint(2, 9)
        x = random.randint(2, 9)
        b = a * x
        correct = str(x)
        distractors = [str(b + a), str(b - a), str(a)]
        question = f"Solve {a}x = {b}."
        explanation = f"Divide both sides by {a}: x = {b} ÷ {a} = {x}."
        simpler = "Undo multiplication with division."
    else:
        a = random.randint(2, 6)
        b = random.randint(2, 9)
        x = random.randint(2, 8)
        cval = a * x + b
        correct = str(x)
        distractors = [str(x + 1), str(x - 1), str(cval - b)]
        question = f"Solve {a}x + {b} = {cval}."
        explanation = f"Subtract {b}: {a}x = {cval - b}. Divide by {a}: x = {x}."
        simpler = "Do the opposite operations in reverse order."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("linear-equations", d, question, options, index, explanation, simpler)


def _q_statistics(c, d):
    values = [random.randint(1, 20) for _ in range(5)]
    if d == "easy":
        correct = str(round(sum(values) / len(values), 1))
        distractors = [str(sum(values)), str(max(values)), str(min(values))]
        question = f"Find the mean of {', '.join(map(str, values))}."
        explanation = f"Mean = total ÷ number of values = {sum(values)} ÷ {len(values)} = {correct}."
        simpler = "Add all the numbers, then divide by how many numbers there are."
    elif d == "medium":
        ordered = sorted(values)
        correct = str(ordered[len(ordered) // 2])
        distractors = [str(ordered[0]), str(ordered[-1]), str(ordered[1])]
        question = f"Find the median of {', '.join(map(str, values))}."
        explanation = f"Order the numbers: {', '.join(map(str, ordered))}. The middle value is {correct}."
        simpler = "The median is the middle number after sorting."
    else:
        values = [random.randint(1, 10) for _ in range(6)]
        ordered = sorted(values)
        correct = str(ordered[-1] - ordered[0])
        distractors = [str(ordered[-1]), str(ordered[0]), str(sum(ordered))]
        question = f"Find the range of {', '.join(map(str, values))}."
        explanation = f"Range = largest − smallest = {ordered[-1]} − {ordered[0]} = {correct}."
        simpler = "Range tells how spread out the data is."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("basic-statistics", d, question, options, index, explanation, simpler)


def _q_mensuration(c, d):
    if d == "easy":
        length = random.randint(3, 15)
        width = random.randint(2, 12)
        answer = 2 * (length + width)
        question = f"A rectangle is {length} cm long and {width} cm wide. What is its perimeter?"
        explanation = f"Perimeter = 2 × (length + width) = 2 × ({length} + {width}) = {answer} cm."
        simpler = "Perimeter is the distance all the way around the shape."
        options, index = _numeric_options(answer, low=0)
        return _make("mensuration", d, question, options, index, explanation, simpler)
    if d == "medium":
        if random.random() < 0.5:
            length = random.randint(4, 15)
            width = random.randint(3, 12)
            answer = length * width
            question = f"A rectangle is {length} cm long and {width} cm wide. What is its area?"
            explanation = f"Area = length × width = {length} × {width} = {answer} cm²."
            simpler = "Area is the number of unit squares that fit inside the shape."
        else:
            base = random.choice([4, 6, 8, 10, 12])
            height = random.randint(3, 9)
            answer = (base * height) // 2
            question = f"A triangle has a base of {base} cm and a height of {height} cm. What is its area?"
            explanation = f"Area = ½ × base × height = ½ × {base} × {height} = {answer} cm²."
            simpler = "Multiply base by height, then divide by 2."
        options, index = _numeric_options(answer, low=0)
        return _make("mensuration", d, question, options, index, explanation, simpler)
    length = random.randint(3, 9)
    width = random.randint(2, 7)
    height = random.randint(2, 6)
    answer = length * width * height
    question = (
        f"A cuboid is {length} cm long, {width} cm wide and {height} cm high. "
        "What is its volume?"
    )
    explanation = f"Volume = length × width × height = {length} × {width} × {height} = {answer} cm³."
    simpler = "Volume is the space inside a solid. Multiply the three dimensions."
    options, index = _numeric_options(answer, low=0)
    return _make("mensuration", d, question, options, index, explanation, simpler)


# ---------------------------------------------------------------------------
# Primary English generators
# ---------------------------------------------------------------------------
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
VOWELS = set("AEIOU")


def _q_alphabet(c, d):
    if d == "easy":
        index = random.randint(0, len(ALPHABET) - 2)
        after = random.random() < 0.5
        letter = ALPHABET[index]
        correct = ALPHABET[index + 1] if after else ALPHABET[max(0, index - 1)]
        distractors = [ALPHABET[max(0, index - 2)], ALPHABET[min(25, index + 2)], ALPHABET[random.randint(0, 25)]]
        question = f"Which letter comes {'after' if after else 'before'} {letter}?"
        explanation = f"In the alphabet, {correct} comes {'after' if after else 'before'} {letter}."
        simpler = "Say the alphabet song and stop at the letter."
    elif d == "medium":
        word = random.choice(["apple", "ball", "cat", "dog", "fish", "mango", "sun", "tree"])
        correct = word[0].upper()
        distractors = [letter for letter in ALPHABET if letter != correct][:3]
        question = f"Which letter does the word '{word}' begin with?"
        explanation = f"'{word}' begins with the letter {correct}."
        simpler = "Say the word slowly and listen to the first sound."
    else:
        correct = random.choice(list(VOWELS))
        distractors = [letter for letter in "BCDFGH" if letter not in VOWELS][:3]
        question = "Which of these is a vowel?"
        explanation = f"{correct} is a vowel. The vowels are A, E, I, O and U."
        simpler = "The vowels are A, E, I, O and U."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("alphabet-recognition", d, question, options, index, explanation, simpler)


VOCAB_MEANINGS = [
    ("a baby dog", "puppy", ["kitten", "calf", "chick"]),
    ("a baby cat", "kitten", ["puppy", "foal", "duckling"]),
    ("a place where we borrow books", "library", ["market", "hospital", "station"]),
    ("a person who teaches us", "teacher", ["farmer", "doctor", "driver"]),
    ("a meal we eat in the morning", "breakfast", ["dinner", "lunch", "supper"]),
    ("a large animal with a trunk", "elephant", ["giraffe", "monkey", "zebra"]),
    ("a shape with three sides", "triangle", ["square", "circle", "rectangle"]),
    ("a colour like the sky", "blue", ["red", "green", "yellow"]),
]
OPPOSITES = [
    ("big", "small"), ("hot", "cold"), ("happy", "sad"), ("fast", "slow"),
    ("day", "night"), ("open", "closed"), ("old", "new"), ("clean", "dirty"),
    ("bright", "dark"), ("loud", "quiet"),
]
CONTEXT_WORDS = [
    ("The desert is very ___.", "dry", ["wet", "cold", "noisy"]),
    ("She was ___ after winning the race.", "happy", ["angry", "sleepy", "sad"]),
    ("The turtle moves very ___.", "slowly", ["quickly", "loudly", "brightly"]),
]


def _q_vocabulary(c, d):
    if d == "easy":
        meaning, correct, distractors = random.choice(VOCAB_MEANINGS)
        question = f"Which word means {meaning}?"
        explanation = f"The correct word is '{correct}'."
        simpler = "Picture the meaning in your mind, then choose the word that matches."
    elif d == "medium":
        word, opposite = random.choice(OPPOSITES)
        correct = opposite
        distractors = [item[1] for item in OPPOSITES if item[1] != opposite][:3]
        question = f"Which word is the opposite of '{word}'?"
        explanation = f"The opposite of '{word}' is '{opposite}'."
        simpler = "An opposite word has a completely different meaning."
    else:
        sentence, correct, distractors = random.choice(CONTEXT_WORDS)
        question = f"Choose the best word: {sentence}"
        explanation = f"'{correct}' fits the sentence meaning."
        simpler = "Read the whole sentence and choose the word that makes sense."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("basic-vocabulary", d, question, options, index, explanation, simpler)


NAMING_SENTENCES = [
    ("The dog runs fast.", "dog", ["runs", "fast", "the"]),
    ("Riya reads a book.", "book", ["reads", "a", "Riya"]),
    ("The school is near the park.", "school", ["near", "the", "is"]),
    ("My mother cooks dinner.", "mother", ["cooks", "dinner", "my"]),
    ("The bird sings sweetly.", "bird", ["sings", "sweetly", "the"]),
]


def _q_naming_words(c, d):
    if d == "easy":
        sentence, correct, distractors = random.choice(NAMING_SENTENCES)
        question = f"Which word is a naming word?  '{sentence}'"
        explanation = f"'{correct}' names a person, place, animal or thing, so it is a noun."
        simpler = "A naming word tells us who or what the sentence is about."
    elif d == "medium":
        groups = [
            ("Which word names a place?", "garden", ["run", "happy", "quickly"]),
            ("Which word names a person?", "doctor", ["hospital", "medicine", "heal"]),
            ("Which word names an animal?", "rabbit", ["hop", "carrot", "fast"]),
            ("Which word names a thing?", "pencil", ["write", "sharp", "desk"]),
        ]
        question, correct, distractors = random.choice(groups)
        explanation = f"'{correct}' is a naming word."
        simpler = "Ask: can I touch or visit it? Then it may be a naming word."
    else:
        sentence, correct, distractors = random.choice(NAMING_SENTENCES)
        question = f"Which word is NOT a naming word in: '{sentence}'?"
        correct = distractors[0]
        other_options = [word for word in sentence.replace(".", "").split() if word.lower() != correct.lower()][:2]
        distractors = other_options + ["table"]
        explanation = f"'{correct}' is an action or describing word, not a naming word in this sentence."
        simpler = "Naming words are people, places, animals and things."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("naming-words", d, question, options, index, explanation, simpler)


ARTICLE_WORDS = [
    ("apple", "an"), ("elephant", "an"), ("orange", "an"), ("umbrella", "an"),
    ("cat", "a"), ("book", "a"), ("school", "a"), ("tree", "a"),
    ("hour", "an"), ("house", "a"), ("uncle", "an"), ("university", "a"),
]


def _q_articles(c, d):
    if d == "easy":
        word, correct = random.choice(ARTICLE_WORDS)
        question = f"Choose the correct article: ___ {word}"
        explanation = f"We use '{correct}' before '{word}' because of its starting sound."
        simpler = "Use 'an' before a vowel sound and 'a' before a consonant sound."
        distractors = ["a", "an", "the"]
    elif d == "medium":
        word, correct = random.choice(ARTICLE_WORDS)
        question = f"Complete the sentence: I saw ___ {word} in the park."
        explanation = f"The correct article is '{correct}'."
        simpler = "Say the sentence aloud and listen to the sound after the blank."
        distractors = ["a", "an", "the"] if correct != "the" else ["a", "an", "some"]
    else:
        correct = "the"
        distractors = ["a", "an", "some"]
        question = "Choose the best article: ___ sun rises in the east."
        explanation = "We use 'the' for a unique thing, such as the sun."
        simpler = "There is only one sun, so we say 'the sun'."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("articles", d, question, options, index, explanation, simpler)


def _q_simple_sentences(c, d):
    if d == "easy":
        correct = "The cat sleeps on the mat."
        distractors = ["sleeps on the mat", "cat on mat", "The cat on"]
        question = "Which group of words is a complete sentence?"
        explanation = "A sentence needs a subject and a verb and must make complete sense."
        simpler = "A complete sentence tells us who or what and what happens."
    elif d == "medium":
        correct = "Where is my bag?"
        distractors = ["where is my bag.", "Where is my bag", "where is my bag?"]
        question = "Which sentence has correct capital letters and punctuation?"
        explanation = "A question begins with a capital letter and ends with a question mark."
        simpler = "Questions need a capital letter at the start and a ? at the end."
    else:
        correct = "The children are playing in the garden."
        distractors = ["The children is playing in the garden.", "The children playing garden.", "Children are play in garden."]
        question = "Which sentence is grammatically correct?"
        explanation = "The subject 'children' is plural, so we use 'are playing'."
        simpler = "Check that the verb matches the subject."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("simple-sentences", d, question, options, index, explanation, simpler)


PLURALS = [
    ("cat", "cats"), ("dog", "dogs"), ("box", "boxes"), ("bus", "buses"),
    ("baby", "babies"), ("city", "cities"), ("child", "children"), ("man", "men"),
    ("woman", "women"), ("leaf", "leaves"),
]


def _q_basic_grammar(c, d):
    if d == "easy":
        singular, plural = random.choice(PLURALS)
        correct = plural
        distractors = [singular + "s", singular + "es", singular]
        question = f"What is the plural of '{singular}'?"
        explanation = f"The plural of '{singular}' is '{plural}'."
        simpler = "A plural means more than one."
    elif d == "medium":
        correct = "are"
        distractors = ["is", "am", "be"]
        question = "Choose the correct verb: The students ___ in the classroom."
        explanation = "'Students' is plural, so we use 'are'."
        simpler = "Singular goes with 'is'; plural goes with 'are'."
    else:
        correct = "She"
        distractors = ["Her", "Hers", "Herself"]
        question = "Choose the correct pronoun: ___ is my sister."
        explanation = "'She' is the subject pronoun used before the verb."
        simpler = "Use 'she' when the pronoun is doing the action."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("basic-grammar", d, question, options, index, explanation, simpler)


PRIMARY_PASSAGES = [
    {
        "text": "Mia has a red ball. She plays with it in the park. Her friend Sam joins her.",
        "easy": ("What colour is Mia's ball?", "Red", ["Blue", "Green", "Yellow"]),
        "medium": ("Where does Mia play?", "In the park", ["At school", "At home", "In a shop"]),
        "hard": ("How do you know Sam is Mia's friend?", "The passage says Sam is her friend.", ["Sam has a ball.", "Mia is at home.", "Sam is a teacher."]),
    },
    {
        "text": "The sun is bright today. Ravi puts on his cap and goes outside. He waters the plants.",
        "easy": ("What does Ravi put on?", "A cap", ["A coat", "Shoes", "Glasses"]),
        "medium": ("What does Ravi do outside?", "He waters the plants.", ["He reads a book.", "He cooks food.", "He sleeps."]),
        "hard": ("Why does Ravi wear a cap?", "The sun is bright.", ["It is raining.", "He is cold.", "He is going to school."]),
    },
    {
        "text": "A little bird sits on a tree. It sings a sweet song. A cat watches from below.",
        "easy": ("Where is the bird?", "On a tree", ["In a nest", "On the ground", "In a house"]),
        "medium": ("What does the bird do?", "It sings.", ["It runs.", "It swims.", "It sleeps."]),
        "hard": ("Why might the bird be in danger?", "A cat is watching it.", ["The tree is tall.", "The song is sweet.", "The bird is little."]),
    },
]


def _q_reading_primary(c, d):
    passage = random.choice(PRIMARY_PASSAGES)
    question, correct, distractors = passage[d]
    options, index = _shuffle_with_correct(correct, distractors)
    full = f"Read: {passage['text']}\n\n{question}"
    return _make(
        "reading-comprehension", d, full, options, index,
        f"The passage says: {correct}",
        "Read the passage again and look for the sentence that answers the question.",
    )


SPELLING_WORDS = {
    "easy": ["cat", "dog", "sun", "book", "tree", "milk", "ball"],
    "medium": ["school", "friend", "garden", "yellow", "family", "water", "happy"],
    "hard": ["beautiful", "because", "different", "important", "together", "thought", "question"],
}


def _misspell(word):
    """Create a believable misspelling of a word."""
    if len(word) < 4:
        return word[0] + word[2:] if len(word) > 2 else word + "e"
    variants = [
        word.replace("ie", "ei", 1) if "ie" in word else word,
        word[:-2] + word[-1] + word[-2] if len(word) > 3 else word,
        word.replace("a", "e", 1) if "a" in word else word,
        word.replace("o", "u", 1) if "o" in word else word,
    ]
    for variant in variants:
        if variant != word:
            return variant
    return word + "e"


def _q_spelling(c, d):
    word = random.choice(SPELLING_WORDS[d])
    distractors = []
    for _ in range(6):
        variant = _misspell(word)
        if variant != word and variant not in distractors:
            distractors.append(variant)
        if len(distractors) == 3:
            break
    while len(distractors) < 3:
        distractors.append(word + "e" * len(distractors))
    options, index = _shuffle_with_correct(word, distractors)
    return _make(
        "spelling-practice", d,
        "Which spelling is correct?",
        options, index,
        f"The correct spelling is '{word}'.",
        "Say the word slowly, then look for the spelling pattern.",
    )


# ---------------------------------------------------------------------------
# Secondary English generators
# ---------------------------------------------------------------------------
PARTS_SENTENCES = [
    ("The brave firefighter rescued the child.", "brave", "adjective", ["noun", "verb", "adverb"]),
    ("She quickly finished her homework.", "quickly", "adverb", ["noun", "verb", "adjective"]),
    ("The teacher explained the lesson.", "explained", "verb", ["noun", "adjective", "adverb"]),
    ("Rohan visited the museum.", "Rohan", "noun", ["verb", "adjective", "adverb"]),
    ("The garden looks beautiful.", "beautiful", "adjective", ["noun", "verb", "adverb"]),
    ("They sang loudly in the hall.", "loudly", "adverb", ["noun", "verb", "adjective"]),
]


def _q_parts_of_speech(c, d):
    sentence, word, correct, distractors = random.choice(PARTS_SENTENCES)
    if d == "hard":
        question = f"Which part of speech is the word '{word}' in: '{sentence}'?"
        explanation = f"'{word}' functions as a {correct} in this sentence."
        simpler = "Ask what job the word is doing in the sentence."
    else:
        question = f"Which part of speech is '{word}' in: '{sentence}'?"
        explanation = f"'{word}' is a {correct} here."
        simpler = "Nouns name, verbs show action, adjectives describe nouns and adverbs describe verbs."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("parts-of-speech", d, question, options, index, explanation, simpler)


TENSE_ITEMS = [
    ("She ___ to school every day.", "goes", ["go", "going", "gone"], "simple present"),
    ("They ___ football yesterday.", "played", ["play", "playing", "will play"], "simple past"),
    ("I ___ finish my project tomorrow.", "will", ["am", "was", "did"], "simple future"),
    ("He ___ reading when I called.", "was", ["is", "were", "has"], "past continuous"),
    ("We ___ lived here for five years.", "have", ["has", "had", "will"], "present perfect"),
    ("By 8 pm, she ___ finished dinner.", "had", ["has", "have", "will"], "past perfect"),
]


def _q_tenses(c, d):
    sentence, correct, distractors, tense = random.choice(TENSE_ITEMS)
    question = f"Choose the correct verb form: {sentence}"
    explanation = f"The sentence needs the {tense} form, so '{correct}' is correct."
    simpler = "Look for the time clue: every day, yesterday or tomorrow."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("tenses", d, question, options, index, explanation, simpler)


VOICE_ITEMS = [
    ("The chef cooked the meal.", "The meal was cooked by the chef.", ["The meal cooked the chef.", "The chef was cooked by the meal.", "The meal is cook by the chef."]),
    ("Riya wrote a poem.", "A poem was written by Riya.", ["A poem wrote Riya.", "Riya was written by a poem.", "A poem is write by Riya."]),
    ("The children cleaned the classroom.", "The classroom was cleaned by the children.", ["The classroom cleaned the children.", "The children were cleaned by the classroom.", "The classroom is clean by the children."]),
]


def _q_voice(c, d):
    active, correct, distractors = random.choice(VOICE_ITEMS)
    if d == "easy":
        question = f"Which sentence is in passive voice?  Active sentence: '{active}'"
        explanation = f"Passive voice: {correct}"
        simpler = "Passive voice often uses 'was/were' plus a past participle."
    else:
        question = f"Change to passive voice: '{active}'"
        explanation = f"The passive form is: {correct}"
        simpler = "Move the object to the front and use 'was/were' plus the past participle."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("active-passive-voice", d, question, options, index, explanation, simpler)


SPEECH_ITEMS = [
    ('She said, "I am happy."', "She said that she was happy.", ["She said that she is happy.", "She says that she was happy.", "She said she is happy."]),
    ('He said, "I will come tomorrow."', "He said that he would come the next day.", ["He said that he will come tomorrow.", "He says he would come tomorrow.", "He said he comes the next day."]),
    ('The teacher said, "Open your books."', "The teacher told us to open our books.", ["The teacher said us to open our books.", "The teacher told that open your books.", "The teacher says open your books."]),
]


def _q_speech(c, d):
    direct, correct, distractors = random.choice(SPEECH_ITEMS)
    if d == "easy":
        question = f"Which sentence uses indirect speech?  Direct: {direct}"
        explanation = f"Indirect speech reports the words without quotation marks: {correct}"
        simpler = "Indirect speech does not use quotation marks."
    else:
        question = f"Change to indirect speech: {direct}"
        explanation = f"The indirect form is: {correct}"
        simpler = "Remove the quotation marks and change the pronoun and tense if needed."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("direct-indirect-speech", d, question, options, index, explanation, simpler)


SYNONYMS = [
    ("brave", "courageous", ["afraid", "weak", "quiet"]),
    ("happy", "joyful", ["angry", "sad", "tired"]),
    ("begin", "start", ["finish", "stop", "close"]),
    ("ancient", "old", ["new", "modern", "young"]),
    ("rapid", "quick", ["slow", "lazy", "late"]),
    ("quiet", "silent", ["loud", "noisy", "busy"]),
]
ANTONYMS = [
    ("expand", "shrink", ["grow", "stretch", "open"]),
    ("generous", "stingy", ["kind", "helpful", "giving"]),
    ("ancient", "modern", ["old", "historic", "past"]),
    ("victory", "defeat", ["win", "success", "triumph"]),
    ("scarce", "plentiful", ["rare", "limited", "few"]),
]


def _q_vocab_secondary(c, d):
    if d in {"easy", "medium"}:
        word, correct, distractors = random.choice(SYNONYMS)
        question = f"Choose the synonym of '{word}'."
        explanation = f"'{correct}' has a similar meaning to '{word}'."
        simpler = "A synonym means almost the same thing."
    else:
        word, correct, distractors = random.choice(ANTONYMS)
        question = f"Choose the antonym of '{word}'."
        explanation = f"'{correct}' is the opposite of '{word}'."
        simpler = "An antonym means the opposite."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("vocabulary-building", d, question, options, index, explanation, simpler)


CORRECTION_ITEMS = [
    ("She go to school every day.", "She goes to school every day.", ["She going to school every day.", "She gone to school every day.", "She went to school every day."]),
    ("I didn't see nobody in the room.", "I didn't see anybody in the room.", ["I didn't see nobody not in the room.", "I saw nobody in the room not.", "I don't saw anybody in the room."]),
    ("Where is my bag.", "Where is my bag?", ["Where is my bag!", "where is my bag?", "Where is my bag,"]),
    ("The boys is playing outside.", "The boys are playing outside.", ["The boys am playing outside.", "The boys be playing outside.", "The boy are playing outside."]),
]


def _q_sentence_correction(c, d):
    wrong, correct, distractors = random.choice(CORRECTION_ITEMS)
    question = f"Choose the correct sentence. Incorrect: '{wrong}'"
    explanation = f"The correct sentence is: {correct}"
    simpler = "Check the verb, the capital letters and the punctuation."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("sentence-correction", d, question, options, index, explanation, simpler)


SECONDARY_PASSAGES = [
    {
        "text": "Trees are essential for life on Earth. They release oxygen, provide shade and hold soil together. However, large areas of forest are cut down every year. Planting trees and protecting existing forests can reduce the damage.",
        "easy": ("What do trees release?", "Oxygen", ["Carbon dioxide", "Water", "Smoke"]),
        "medium": ("What is the main idea of the passage?", "Trees are important and should be protected.", ["Trees are only useful for shade.", "Forests are growing quickly.", "Oxygen is harmful."]),
        "hard": ("What can be inferred from the passage?", "Protecting forests helps the environment.", ["Cutting trees is harmless.", "Trees do not affect soil.", "Oxygen is not important."]),
    },
    {
        "text": "Many students feel nervous before an exam. A little nervousness can help them focus, but too much can affect sleep and memory. Planning revision, taking short breaks and practising past questions can make exams feel more manageable.",
        "easy": ("What can too much nervousness affect?", "Sleep and memory", ["Height", "Eyesight", "Appetite only"]),
        "medium": ("Which suggestion is given in the passage?", "Planning revision", ["Skipping meals", "Studying all night", "Avoiding practice"]),
        "hard": ("What is the writer's attitude towards exam nerves?", "A small amount can be useful, but it should be managed.", ["All nerves are harmful.", "Nerves should be ignored completely.", "Exams should be removed."]),
    },
    {
        "text": "Clean water is a basic need. In many villages, people walk long distances to collect it. Simple solutions such as rainwater harvesting and repairing hand pumps can save time and improve health.",
        "easy": ("What is a basic need mentioned in the passage?", "Clean water", ["Television", "Toys", "Cars"]),
        "medium": ("What solution is mentioned?", "Rainwater harvesting", ["Building more roads", "Buying bottled water", "Using more electricity"]),
        "hard": ("Why can repairing hand pumps improve health?", "It provides easier access to clean water.", ["It makes villages louder.", "It reduces the number of trees.", "It increases walking distance."]),
    },
]


def _q_reading_secondary(c, d):
    passage = random.choice(SECONDARY_PASSAGES)
    question, correct, distractors = passage[d]
    options, index = _shuffle_with_correct(correct, distractors)
    full = f"Read: {passage['text']}\n\n{question}"
    return _make(
        "reading-comprehension-secondary", d, full, options, index,
        f"The passage supports this answer: {correct}",
        "Go back to the passage and underline the sentence that supports your answer.",
    )


WRITING_ITEMS = [
    ("Which is the best topic sentence for a paragraph about trees?", "Trees are important for every living thing.", ["I like trees.", "Trees are green.", "There are many trees."]),
    ("Which sentence is written formally?", "I am writing to request information about the course.", ["Hey, tell me about the course.", "I wanna know about the course.", "Course info please."]),
    ("Which is the best closing sentence for a paragraph about exercise?", "In short, regular exercise improves both body and mind.", ["That is all.", "Exercise is good.", "I like to run."]),
]


def _q_writing(c, d):
    question, correct, distractors = random.choice(WRITING_ITEMS)
    explanation = f"'{correct}' is the strongest choice because it is clear and complete."
    simpler = "A good topic sentence introduces the main idea of the paragraph."
    options, index = _shuffle_with_correct(correct, distractors)
    return _make("basic-writing-skills", d, question, options, index, explanation, simpler)


# ---------------------------------------------------------------------------
# Registry and public helpers
# ---------------------------------------------------------------------------
GENERATORS = {
    "counting": _q_counting,
    "addition": _q_addition,
    "subtraction": _q_subtraction,
    "multiplication": _q_multiplication,
    "division": _q_division,
    "number-patterns": _q_number_patterns,
    "basic-shapes": _q_shapes,
    "fractions": _q_fractions,
    "measurement": _q_measurement,
    "time-and-money": _q_time_money,
    "integers": _q_integers,
    "fractions-decimals": _q_fractions_decimals,
    "percentages": _q_percentages,
    "ratio-proportion": _q_ratio,
    "algebra": _q_algebra,
    "geometry": _q_geometry,
    "linear-equations": _q_linear_equations,
    "basic-statistics": _q_statistics,
    "mensuration": _q_mensuration,
    "alphabet-recognition": _q_alphabet,
    "basic-vocabulary": _q_vocabulary,
    "naming-words": _q_naming_words,
    "articles": _q_articles,
    "simple-sentences": _q_simple_sentences,
    "basic-grammar": _q_basic_grammar,
    "reading-comprehension": _q_reading_primary,
    "spelling-practice": _q_spelling,
    "parts-of-speech": _q_parts_of_speech,
    "tenses": _q_tenses,
    "active-passive-voice": _q_voice,
    "direct-indirect-speech": _q_speech,
    "vocabulary-building": _q_vocab_secondary,
    "sentence-correction": _q_sentence_correction,
    "reading-comprehension-secondary": _q_reading_secondary,
    "basic-writing-skills": _q_writing,
}


def starting_difficulty(class_level: int) -> str:
    """A sensible first question difficulty for a class."""
    if class_level <= 2:
        return "easy"
    if class_level <= 5:
        return "easy"
    return "medium"


def next_difficulty(current: str, is_correct: bool, streak: int) -> str:
    """Adaptive difficulty rule used after every answer."""
    levels = ["easy", "medium", "hard"]
    index = levels.index(current) if current in levels else 0
    if is_correct:
        if streak >= 2 and index < 2:
            return levels[index + 1]
        return current
    # A wrong answer gives an easier question straight away.
    return levels[max(0, index - 1)]


def generate_question(topic_slug: str, class_level: int, difficulty: str = "easy"):
    """Generate one class-aware question for a topic."""
    topic = TOPIC_BY_SLUG.get(topic_slug)
    if not topic:
        raise ValueError(f"Unknown topic: {topic_slug}")
    difficulty = difficulty if difficulty in {"easy", "medium", "hard"} else "easy"
    generator = GENERATORS.get(topic_slug)
    if not generator:
        raise ValueError(f"No question generator for topic: {topic_slug}")
    return generator(int(class_level), difficulty)


def practice_questions(topic_slug: str, class_level: int, count: int = 2):
    """Return a few practice questions with answers for the lesson page."""
    difficulty = "easy" if class_level <= 5 else "medium"
    questions = []
    seen = set()
    attempts = 0
    while len(questions) < count and attempts < 30:
        attempts += 1
        question = generate_question(topic_slug, class_level, difficulty)
        if question["question"] in seen:
            continue
        seen.add(question["question"])
        questions.append(question)
    return questions
