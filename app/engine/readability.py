"""
Textora AI - Readability & Writing Complexity Engine
Calculates standard readability metrics: Flesch Reading Ease, Flesch-Kincaid Grade,
Gunning Fog Index, and Coleman-Liau Index.
"""
import re
from typing import Dict, Any, List

def count_syllables_in_word(word: str) -> int:
    """
    Estimates syllable count using English phonetic heuristics.
    """
    word = word.lower().strip()
    if not word:
        return 0
    if len(word) <= 3:
        return 1
        
    # Remove non-alpha
    word = re.sub(r'[^a-z]', '', word)
    if not word:
        return 1
        
    # Exceptions
    if word.endswith('e') and not word.endswith('le') and not word.endswith('ee'):
        word = word[:-1]
        
    vowel_groups = re.findall(r'[aeiouy]+', word)
    count = len(vowel_groups)
    
    return max(1, count)

def calculate_readability(text: str, sentences: List[str], words: List[str]) -> Dict[str, Any]:
    total_sentences = max(1, len(sentences))
    total_words = max(1, len(words))
    
    total_syllables = sum(count_syllables_in_word(w) for w in words)
    complex_words = [w for w in words if count_syllables_in_word(w) >= 3]
    total_complex_words = len(complex_words)
    
    total_letters = sum(len(re.sub(r'[^a-zA-Z]', '', w)) for w in words)
    
    avg_words_per_sentence = total_words / total_sentences
    avg_syllables_per_word = total_syllables / total_words
    percent_complex_words = (total_complex_words / total_words) * 100.0
    
    # Flesch Reading Ease
    # 206.835 - 1.015 * (words/sentence) - 84.6 * (syllables/word)
    fre = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
    fre = max(0.0, min(100.0, fre))
    
    # Flesch-Kincaid Grade Level
    # 0.39 * (words/sentence) + 11.8 * (syllables/word) - 15.59
    fkgl = (0.39 * avg_words_per_sentence) + (11.8 * avg_syllables_per_word) - 15.59
    fkgl = max(1.0, round(fkgl, 1))
    
    # Gunning Fog Index
    # 0.4 * ((words/sentence) + 100 * (complex_words/words))
    gunning_fog = 0.4 * (avg_words_per_sentence + percent_complex_words)
    gunning_fog = max(1.0, round(gunning_fog, 1))
    
    # Coleman-Liau Index
    # 0.0588 * L - 0.296 * S - 15.8
    # L = avg number of letters per 100 words
    # S = avg number of sentences per 100 words
    L = (total_letters / total_words) * 100.0
    S = (total_sentences / total_words) * 100.0
    cli = 0.0588 * L - 0.296 * S - 15.8
    cli = max(1.0, round(cli, 1))
    
    # Interpret Reading Ease
    if fre >= 80:
        ease_label = "Very Easy (Elementary reading level)"
    elif fre >= 70:
        ease_label = "Easy (Conversational, 7th grade level)"
    elif fre >= 60:
        ease_label = "Standard (Plain English, 8th-9th grade level)"
    elif fre >= 50:
        ease_label = "Fairly Difficult (High school level)"
    elif fre >= 30:
        ease_label = "Difficult (College undergraduate level)"
    else:
        ease_label = "Very Difficult (Academic/Professional research level)"
        
    return {
        "flesch_reading_ease": round(fre, 1),
        "flesch_reading_ease_label": ease_label,
        "flesch_kincaid_grade": fkgl,
        "gunning_fog_index": gunning_fog,
        "coleman_liau_index": cli,
        "avg_words_per_sentence": round(avg_words_per_sentence, 1),
        "avg_syllables_per_word": round(avg_syllables_per_word, 2),
        "complex_word_count": total_complex_words,
        "complex_word_ratio": round(percent_complex_words, 1)
    }
