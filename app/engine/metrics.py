"""
Textora AI - Linguistic Metrics Engine
Calculates burstiness, sentence-length distribution, lexical diversity (TTR, Hapax),
n-gram repetition, and sentence-starter uniformity.
"""
import math
import re
from collections import Counter
from typing import List, Dict, Any

def calculate_burstiness(sentence_lengths: List[int]) -> Dict[str, Any]:
    """
    Computes burstiness based on sentence length variation.
    Human writing displays high burstiness (large variance between short and long sentences).
    AI generation tends to exhibit low variance (uniform, moderate sentence lengths).
    """
    n = len(sentence_lengths)
    if n == 0:
        return {
            "mean_length": 0.0,
            "std_deviation": 0.0,
            "coefficient_of_variation": 0.0,
            "burstiness_score": 50.0,
            "burstiness_label": "Neutral / Insufficient Data",
            "min_length": 0,
            "max_length": 0,
            "distribution": {}
        }
        
    mean = sum(sentence_lengths) / n
    variance = sum((x - mean) ** 2 for x in sentence_lengths) / max(1, n - 1)
    std_dev = math.sqrt(variance)
    
    # Coefficient of Variation (CV = sigma / mu)
    cv = (std_dev / mean) if mean > 0 else 0.0
    
    # Bucket distribution for charts
    distribution = {
        "short_1_to_10": sum(1 for x in sentence_lengths if x <= 10),
        "medium_11_to_20": sum(1 for x in sentence_lengths if 11 <= x <= 20),
        "long_21_to_30": sum(1 for x in sentence_lengths if 21 <= x <= 30),
        "extended_31_plus": sum(1 for x in sentence_lengths if x > 30),
    }
    
    # Human CV is typically > 0.45 (often 0.5 - 0.9)
    # AI CV is often < 0.35 (tight clustering around 15-22 words)
    # Normalizing burstiness score from 0 (very uniform / AI-like) to 100 (highly varied / Human-like)
    burstiness_score = min(100.0, max(0.0, cv * 120.0))
    
    if cv >= 0.52:
        burst_label = "High Burstiness (Natural human rhythm with varied pacing)"
    elif cv >= 0.36:
        burst_label = "Moderate Burstiness (Mixed sentence structures)"
    else:
        burst_label = "Low Burstiness (Uniform sentence pacing typical of synthetic text)"
        
    return {
        "mean_length": round(mean, 1),
        "std_deviation": round(std_dev, 2),
        "coefficient_of_variation": round(cv, 3),
        "burstiness_score": round(burstiness_score, 1),
        "burstiness_label": burst_label,
        "min_length": min(sentence_lengths),
        "max_length": max(sentence_lengths),
        "distribution": distribution
    }

def calculate_lexical_diversity(words: List[str]) -> Dict[str, Any]:
    """
    Computes vocabulary richness:
    - Type-Token Ratio (TTR = Unique / Total)
    - Root TTR (Guiraud's Index: Unique / sqrt(Total))
    - Hapax Legomena ratio (words that occur exactly once)
    - Word frequency entropy
    """
    cleaned_words = [w.lower() for w in words if re.match(r'^[a-zA-Z]+$', w)]
    total_tokens = len(cleaned_words)
    
    if total_tokens == 0:
        return {
            "ttr": 0.0,
            "root_ttr": 0.0,
            "hapax_ratio": 0.0,
            "entropy": 0.0,
            "unique_words": 0,
            "total_words": 0,
            "diversity_label": "No Words"
        }
        
    counts = Counter(cleaned_words)
    unique_words = len(counts)
    
    # Type-Token Ratio
    ttr = unique_words / total_tokens
    
    # Guiraud's Index (Root TTR) is less sensitive to document length
    root_ttr = unique_words / math.sqrt(total_tokens)
    
    # Hapax Legomena: words occurring exactly once
    hapax_count = sum(1 for count in counts.values() if count == 1)
    hapax_ratio = hapax_count / unique_words if unique_words > 0 else 0.0
    
    # Shannon Entropy of token distribution (in bits)
    entropy = 0.0
    for count in counts.values():
        p = count / total_tokens
        entropy -= p * math.log2(p)
        
    if root_ttr >= 7.5 or ttr >= 0.65:
        div_label = "Rich & Varied Vocabulary"
    elif root_ttr >= 5.0 or ttr >= 0.48:
        div_label = "Standard / Moderate Vocabulary"
    else:
        div_label = "Repetitive / Constrained Vocabulary"
        
    return {
        "ttr": round(ttr, 3),
        "root_ttr": round(root_ttr, 2),
        "hapax_count": hapax_count,
        "hapax_ratio": round(hapax_ratio, 3),
        "entropy": round(entropy, 2),
        "unique_words": unique_words,
        "total_words": total_tokens,
        "diversity_label": div_label
    }

def find_repeated_ngrams(words: List[str], n: int = 3, min_freq: int = 2) -> List[Dict[str, Any]]:
    """
    Finds recurring n-grams (phrases of length n) that repeat throughout the document.
    """
    cleaned = [w.lower() for w in words if re.match(r'^[a-zA-Z]+$', w)]
    if len(cleaned) < n:
        return []
        
    ngrams = [" ".join(cleaned[i:i+n]) for i in range(len(cleaned) - n + 1)]
    counts = Counter(ngrams)
    
    # Filter common stopword-only ngrams that naturally repeat
    common_stops = {"of the", "in the", "to the", "on the", "and the", "at the", "for the", "with the", "as a", "is a"}
    
    repeats = []
    for phrase, count in counts.most_common(10):
        if count >= min_freq and phrase not in common_stops:
            repeats.append({
                "phrase": phrase,
                "count": count
            })
    return repeats

def check_sentence_starter_uniformity(sentences: List[str]) -> Dict[str, Any]:
    """
    Checks if multiple sentences begin with the same words or transitions.
    """
    starters = []
    for s in sentences:
        s_clean = s.strip()
        first_word = re.findall(r'^[A-Za-z]+', s_clean)
        if first_word:
            starters.append(first_word[0].lower())
            
    if not starters:
        return {"uniformity_score": 0.0, "common_starters": []}
        
    counts = Counter(starters)
    top_starter_freq = counts.most_common(1)[0][1] if counts else 0
    ratio = top_starter_freq / len(starters) if starters else 0.0
    
    return {
        "starter_entropy": round(len(counts) / max(1, len(starters)), 2),
        "most_frequent_starter_ratio": round(ratio, 2),
        "common_starters": [{"word": k, "count": v} for k, v in counts.most_common(5) if v > 1]
    }
