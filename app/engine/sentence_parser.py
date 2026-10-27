"""
Textora AI - Sentence Parser & Sentence-by-Sentence Evaluator
Splits text into sentences, assesses per-sentence signal scores,
and attaches observable linguistic rationales for interactive highlighting.
"""
import re
from typing import List, Dict, Any
from app.engine.formulaic_patterns import find_sentence_markers
from app.engine.readability import count_syllables_in_word

ABBREVIATIONS = r'(?:[A-Z]\.|Dr\.|Mr\.|Mrs\.|Ms\.|Prof\.|Sr\.|Jr\.|vs\.|etc\.|i\.e\.|e\.g\.|al\.)'

def split_into_sentences(text: str) -> List[str]:
    """
    Robust sentence segmenter that preserves abbreviations and quotation marks.
    """
    # Replace newlines with space while preserving paragraph structure
    cleaned = re.sub(r'[\r\n]+', ' ', text).strip()
    if not cleaned:
        return []
        
    # Protect common abbreviations temporarily
    protected = cleaned
    placeholders: Dict[str, str] = {}
    
    def replacer(match):
        token = match.group(0)
        key = f"__ABBR_{len(placeholders)}__"
        placeholders[key] = token
        return key
        
    protected = re.sub(ABBREVIATIONS, replacer, protected, flags=re.IGNORECASE)
    
    # Split on sentence boundaries: punctuation followed by space and capital letter or end of string
    raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"\'\(\[])', protected)
    
    # Restore placeholders
    final_sentences = []
    for s in raw_sentences:
        s_restored = s.strip()
        for key, val in placeholders.items():
            s_restored = s_restored.replace(key, val)
        if s_restored:
            final_sentences.append(s_restored)
            
    if not final_sentences and cleaned:
        final_sentences = [cleaned]
        
    return final_sentences

def analyze_sentence(
    sentence: str,
    index: int,
    mean_doc_length: float,
    doc_cv: float,
    sensitivity: str = "balanced"
) -> Dict[str, Any]:
    """
    Scores an individual sentence for AI-like vs Human-like writing signals.
    """
    words = re.findall(r'\b\w+\b', sentence)
    word_count = len(words)
    syllables = sum(count_syllables_in_word(w) for w in words)
    avg_syllable = syllables / max(1, word_count)
    
    # Find formulaic markers in this sentence
    markers = find_sentence_markers(sentence)
    
    # Base heuristic calculation
    # Factors:
    # 1. Formulaic markers (strong signal)
    # 2. Length deviation from the typical AI "sweet spot" (15-24 words)
    # 3. Syllable density / vocabulary formality
    # 4. Passive / formulaic hedge patterns
    
    reasons: List[str] = []
    score = 45.0  # neutral starting point
    
    # Check markers
    if markers:
        marker_names = [f"'{m['phrase']}'" for m in markers]
        reasons.append(f"Contains formulaic AI discourse marker: {', '.join(marker_names)}")
        score += min(35.0, len(markers) * 18.0)
        
    # Check sentence length characteristics
    if 15 <= word_count <= 24:
        # Typical LLM modal sentence length
        if doc_cv < 0.35:
            reasons.append(f"Standard synthetic length ({word_count} words) with low variation")
            score += 12.0
    elif word_count <= 8:
        # Short punchy sentence - human trait
        reasons.append(f"Punchy, concise sentence ({word_count} words) - natural pacing trait")
        score -= 22.0
    elif word_count >= 32:
        # Complex extended sentence
        reasons.append(f"Extended complex structure ({word_count} words) with compound phrasing")
        score -= 10.0
        
    # Passive or repetitive structural patterns
    lower_s = sentence.lower()
    if re.search(r'\b(it is|there are|there is|it can be seen that|one of the most)\b', lower_s):
        score += 8.0
        reasons.append("Formulaic impersonal passive construction")
        
    if re.search(r'\b(not only .+ but also)\b', lower_s):
        score += 14.0
        reasons.append("Formulaic correlative conjunction ('not only... but also')")
        
    # Sensitivity adjustment
    if sensitivity == "sensitive":
        score = min(100.0, score * 1.12)
    elif sensitivity == "conservative":
        score = max(0.0, score * 0.90)
        
    score = max(5.0, min(95.0, score))
    
    if score >= 62.0:
        signal = "ai"
    elif score <= 38.0:
        signal = "human"
    else:
        signal = "mixed"
        if not reasons:
            reasons.append("Balanced syntax with neutral linguistic signals")
            
    return {
        "index": index,
        "text": sentence,
        "word_count": word_count,
        "syllables": syllables,
        "avg_syllable_per_word": round(avg_syllable, 2),
        "score": round(score, 1),
        "signal": signal,
        "reasons": reasons,
        "markers": [m["phrase"] for m in markers]
    }
