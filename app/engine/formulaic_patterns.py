"""
Textora AI - Formulaic LLM Discourse Markers & Linguistic Tropes
A comprehensive catalog of statistical patterns, transitional clichés,
hedging phrases, and rhetorical hallmarks common in synthetic text.
"""
import re
from typing import List, Dict, Any, Tuple

FORMULAIC_PATTERNS: Dict[str, List[str]] = {
    "llm_hallmark_phrases": [
        "delve into", "delves into", "delving into",
        "serves as a testament", "stands as a testament", "testament to",
        "tapestry of", "rich tapestry", "vibrant tapestry", "woven into",
        "beacon of", "beacon of hope",
        "pivotal role", "plays a pivotal role", "crucial role", "plays a crucial role",
        "in the realm of", "within the realm of",
        "multifaceted", "plethora of", "myriad of",
        "cornerstone of", "bedrock of",
        "ever-evolving landscape", "dynamic landscape",
        "nuanced understanding", "nuanced perspective",
        "harness the power", "unlock the potential",
        "fosters a sense of", "foster meaningful",
        "at its core", "deep dive", "shed light on",
        "paves the way", "poised to", "poised for",
        "integral part", "paramount importance",
        "quintessential", "underpins", "underpinning"
    ],
    "transitional_cliches": [
        "in conclusion", "to sum up", "in summary",
        "first and foremost", "moreover", "furthermore",
        "additionally", "consequently", "last but not least",
        "it is worth noting", "it is important to note", "it should be noted",
        "it is essential to", "it is crucial to remember",
        "one cannot overlook", "one must acknowledge",
        "needless to say", "all in all", "in essence",
        "ultimately, it is clear", "by doing so",
        "not only does this", "not only is this"
    ],
    "generic_intros": [
        "in today's fast-paced world", "in today's digital age",
        "in today's interconnected world", "in an era of rapid",
        "since time immemorial", "throughout history, humans have",
        "from the dawn of time", "as we look toward the future",
        "in this article, we will delve", "in this essay, we will explore"
    ],
    "overused_modifiers": [
        "seamlessly", "meticulously", "relentlessly", "holistic",
        "transformative", "revolutionize", "unwavering", "inextricably linked",
        "profound impact", "significant milestone"
    ]
}

# Compile patterns for fast regex matching (word-boundary aware)
COMPILED_PATTERNS: List[Tuple[str, str, re.Pattern]] = []

for category, phrases in FORMULAIC_PATTERNS.items():
    for phrase in phrases:
        pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
        COMPILED_PATTERNS.append((category, phrase, pattern))

def scan_formulaic_patterns(text: str) -> Dict[str, Any]:
    """
    Scans input text for known formulaic markers and returns match details and density.
    """
    matches_found: List[Dict[str, Any]] = []
    category_counts: Dict[str, int] = {cat: 0 for cat in FORMULAIC_PATTERNS.keys()}
    matched_phrases = set()
    
    words = re.findall(r'\b\w+\b', text)
    total_words = len(words)
    
    for category, phrase, pattern in COMPILED_PATTERNS:
        matches = list(pattern.finditer(text))
        if matches:
            count = len(matches)
            category_counts[category] += count
            matched_phrases.add(phrase)
            for m in matches:
                matches_found.append({
                    "phrase": phrase,
                    "category": category,
                    "start": m.start(),
                    "end": m.end(),
                    "snippet": text[max(0, m.start() - 25):min(len(text), m.end() + 25)]
                })
                
    total_markers = len(matches_found)
    # Density: markers per 100 words
    density_per_100_words = (total_markers / max(1, total_words)) * 100.0
    
    return {
        "total_markers": total_markers,
        "unique_markers": len(matched_phrases),
        "density_per_100_words": round(density_per_100_words, 2),
        "category_counts": category_counts,
        "matched_phrases": sorted(list(matched_phrases)),
        "matches": matches_found
    }

def find_sentence_markers(sentence: str) -> List[Dict[str, str]]:
    """
    Finds formulaic markers present in an individual sentence.
    """
    found = []
    for category, phrase, pattern in COMPILED_PATTERNS:
        if pattern.search(sentence):
            found.append({
                "phrase": phrase,
                "category": category
            })
    return found
