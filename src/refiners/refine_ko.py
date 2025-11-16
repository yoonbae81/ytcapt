#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
refine_ko.py: Korean subtitle refinement logic.
Contains heuristics to combine caption lines into coherent sentences.
"""

import re

# --- (1) Korean Refinement Constants ---

# Heuristic list of common Korean sentence endings.

# Question Endings
QUESTION_ENDINGS = (
    '까', '입니까', '합니까', '있습니까', '없습니까', '아닙니까',
    
    # Base ~요 questions
    '나요', '가요', '신가요', '인가요', '아닌가요', '뭔가요', '어떤가요',
    '건가요', '는 건가요', '은 건가요', '신 건가요',
    '까요', '을까요', 'ㄹ까요', '그럴까요', '할까요', '볼까요',

    # General Conjugations (Present) - '같아요?'
    '아요', '어요', '워요', # '?' will be added by _build_korean_endings

    # General Conjugations (Past) - '했어요?'
    '았어요', '었어요', '였어요', '웠어요', # '?' will be added
    
    # General Conjugations (Future/Conjecture) - '되겠어요?'
    '겠어요', # '?' will be added
    
    # Specific verbs (still useful)
    '있나요', '없나요',
    
    # Plain style
    '냐', '는가', '은가', 'ㄴ가', '으니', '느니',
    '인가', '을까',
)

# Statement/Command/Suggestion Endings
SENTENCE_ENDINGS = (
    # --- Formal (~ㅂ니다) ---
    '습니다', '합니다', '입니다', '있습니다', '됩니다', '않습니다', 'ㅂ니다',
    '겁니다', '것입니다', '봅니다', '생각합니다', '말입니다', '것이죠', '랍니다',
    
    # --- Informal (~요) ---
    # Base/Common
    '고요', '죠', '해요', '에요', '예요', '이예요', '이죠', '그렇죠', '지요', '거예요', '게요',
    '거든요', '잖아요', '더라고요', '인데요', '니까요', '이거든요', '하거든요',
    '걸요', '텐데요', '뿐이에요', '네요', '군요', '있네요', '그렇네요', '구먼',
    
    # Specific verbs (still useful as they are common and distinct)
    '있어요', '없어요', '하세요', '않아요', '못해요',
    '있었죠', '했죠', # '있었죠', '했죠' are past tense ~죠 forms.

    # General Conjugations (Present) - to catch '같아요', '먹어요', '추워요'
    '아요', '어요', '워요',

    # General Conjugations (Past) - to catch '봤어요', '했어요', '없었어요'
    '았어요', '었어요', '였어요', '웠어요',

    # General Conjugations (Future/Conjecture) - to catch '되겠어요'
    '겠어요',

    # --- Plain/Informal (~다 / 반말) ---
    '이다', '했다', '있다', '없다', '된다', '한다', '않는다',
    '었다', '았다', '단다', '란다',
    '거든', '잖아', '더라고', '는데', '니까', '단 말이야', '란 말이야',
    '구나', 

    # --- Noun Endings (명사형 종결) ---
    '있음', '없음', '함', '됨', '것임', '필요함', '중요함', '같음'
)

# Create an expanded set of all endings, with punctuation.
def _build_korean_endings():
    """Builds the sorted list of all Korean endings."""
    endings_set = set()
    
    # Add statement endings (with and without period)
    for ending in SENTENCE_ENDINGS:
        endings_set.add(ending)
        endings_set.add(ending + '.')

    # Add question endings (with, without period, with question mark)
    for ending in QUESTION_ENDINGS:
        endings_set.add(ending)
        endings_set.add(ending + '.')
        endings_set.add(ending + '?')

    # Sort by length (desc) to match longer endings first
    # e.g., "입니다." before "다."
    return tuple(sorted(list(endings_set), key=len, reverse=True))

# Module-level constant, built once.
ALL_ENDINGS = _build_korean_endings()

# Regex to filter out common auto-caption noise
NOISE_PATTERN = re.compile(r'\[.*?\]|\(.*?\)|\>>')


# --- (2) Public Refinement Function ---

def refine_sentences(lines: list[str]) -> str:
    """
    Language-specific refiner for Korean. Uses heuristic endings to combine lines.
    (This function is the standardized interface for all 'refine_xx' modules)
    """

    processed_sentences = []  # List to store completed sentences
    sentence_buffer = []      # Buffer for temporary sentence fragments
    last_processed_sentence = None # Track last added sentence

    for line in lines:
        # Step 1: Filter out noise like (웃음), [박수], >>
        line = NOISE_PATTERN.sub('', line).strip()
        
        if not line:
            continue

        sentence_buffer.append(line)

        # Step 2: Check if the *original* line ends with a sentence-ending affix
        is_sentence_end = False
        for ending in ALL_ENDINGS:
            if line.endswith(ending): # Check the original line
                is_sentence_end = True
                break
        
        # Step 3: If it's an end, join the buffer and process the sentence
        if is_sentence_end:
            full_sentence = " ".join(sentence_buffer)
            
            # Step 3a: Add punctuation if missing
            if not re.search(r'[.?!]$', full_sentence):
                # Check the line that triggered the end
                is_question = any(line.endswith(q) for q in QUESTION_ENDINGS)
                if is_question:
                    full_sentence += "?"
                else:
                    full_sentence += "."
            
            # Step 3b: Check for duplicates
            if full_sentence != last_processed_sentence:
                processed_sentences.append(full_sentence)
                last_processed_sentence = full_sentence
            
            sentence_buffer = [] # Clear the buffer

    # Step 4: If the loop finishes with fragments left in the buffer
    if sentence_buffer:
        full_sentence = " ".join(sentence_buffer)
        
        # Step 4a: Add punctuation if missing
        if not re.search(r'[.?!]$', full_sentence):
            last_line_in_buffer = sentence_buffer[-1]
            is_question = any(last_line_in_buffer.endswith(q) for q in QUESTION_ENDINGS)
            if is_question:
                 full_sentence += "?"
            else:
                 full_sentence += "."
        
        # Step 4b: Check for duplicates
        if full_sentence != last_processed_sentence:
            processed_sentences.append(full_sentence)

    # Return all processed sentences joined by double newlines
    return "\n\n".join(processed_sentences)