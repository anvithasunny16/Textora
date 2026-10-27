"""
Textora AI - Master Analysis Pipeline
Coordinates document metrics, lexical richness, formulaic pattern detection,
sentence-level classification, and actionable recommendation synthesis.
"""
import re
from typing import Dict, Any, List, Optional
from app.engine.formulaic_patterns import scan_formulaic_patterns
from app.engine.readability import calculate_readability
from app.engine.metrics import (
    calculate_burstiness,
    calculate_lexical_diversity,
    find_repeated_ngrams,
    check_sentence_starter_uniformity
)
from app.engine.sentence_parser import split_into_sentences, analyze_sentence

def generate_recommendations(
    ai_score: float,
    burstiness: Dict[str, Any],
    diversity: Dict[str, Any],
    formulaic: Dict[str, Any],
    readability: Dict[str, Any],
    word_count: int
) -> List[Dict[str, str]]:
    recs = []
    
    # 1. Burstiness recommendation
    cv = burstiness.get("coefficient_of_variation", 0.0)
    if cv < 0.38:
        recs.append({
            "category": "Sentence Rhythm & Pacing",
            "title": "Vary Your Sentence Lengths",
            "description": f"Your sentences have a uniform average length of {burstiness.get('mean_length', 0)} words (low variance CV: {cv}). Blend short, punchy statements (4–8 words) with longer compound clauses to create natural cadence and narrative momentum."
        })
    elif cv >= 0.55:
        recs.append({
            "category": "Sentence Rhythm & Pacing",
            "title": "Strong Syntactic Rhythm",
            "description": f"Excellent variation in sentence structures (CV: {cv}). The natural contrast between short and extended thoughts gives the prose an authentic, dynamic human voice."
        })
        
    # 2. Formulaic marker recommendation
    markers_count = formulaic.get("total_markers", 0)
    matched_phrases = formulaic.get("matched_phrases", [])
    if markers_count > 0:
        sample_phrases = ", ".join([f"'{p}'" for p in matched_phrases[:4]])
        recs.append({
            "category": "Word Choice & Clichés",
            "title": "Eliminate Predictable Transition Tropes",
            "description": f"Found {markers_count} characteristic algorithmic markers ({sample_phrases}). Replace generic transitions like 'Moreover' or 'In conclusion' with direct semantic connections that directly tie paragraphs together."
        })
        
    # 3. Lexical richness
    ttr = diversity.get("ttr", 0.0)
    hapax_ratio = diversity.get("hapax_ratio", 0.0)
    if ttr < 0.48 and word_count > 60:
        recs.append({
            "category": "Vocabulary Diversity",
            "title": "Diversify Vocabulary & Expressions",
            "description": f"The Type-Token Ratio is {ttr}, reflecting repeated words. Introduce concrete nouns, sensory verbs, and idiomatic phrasing to enrich the texture of your writing."
        })
        
    # 4. Readability
    grade = readability.get("flesch_kincaid_grade", 8.0)
    if grade > 14.0:
        recs.append({
            "category": "Readability & Clarity",
            "title": "Simplify Dense Phrasing",
            "description": f"The estimated reading level is Grade {grade} (academic/dense). Break down multi-clause sentences with simpler terminology to make your arguments accessible to a broader audience."
        })
    elif grade < 6.0 and word_count > 60:
        recs.append({
            "category": "Readability & Clarity",
            "title": "Elevate Thought Complexity",
            "description": f"Reading level is Grade {grade}. If this is intended for academic or professional contexts, consider deepening analytical context and sentence nuance."
        })
        
    # 5. General voice recommendation
    if not recs:
        recs.append({
            "category": "Originality & Tone",
            "title": "Maintain Authentic Voice",
            "description": "Your text exhibits a healthy balance of lexical variety, natural syntactic pacing, and clean structure. Continue preserving your distinct authorial perspective."
        })
        
    return recs

def analyze_text(
    text: str,
    sensitivity: str = "balanced",
    custom_provider: Optional[str] = None
) -> Dict[str, Any]:
    """
    Primary analysis entry point.
    Executes modular linguistic pipeline, computes holistic scores,
    and returns comprehensive audit payload.
    """
    clean_text = text.strip()
    if not clean_text:
        return {
            "success": False,
            "error": "Input text is empty. Please provide written content or upload a document."
        }
        
    words = re.findall(r'\b[a-zA-Z0-9\'-]+\b', clean_text)
    word_count = len(words)
    char_count = len(clean_text)
    
    if word_count < 5:
        return {
            "success": False,
            "error": "Text is too short for linguistic analysis. Please provide at least 10 words."
        }
        
    sentences = split_into_sentences(clean_text)
    sentence_count = len(sentences)
    
    # 1. Linguistic Metrics
    sentence_lengths = [len(re.findall(r'\b\w+\b', s)) for s in sentences]
    burstiness = calculate_burstiness(sentence_lengths)
    diversity = calculate_lexical_diversity(words)
    readability = calculate_readability(clean_text, sentences, words)
    formulaic = scan_formulaic_patterns(clean_text)
    repeated_ngrams = find_repeated_ngrams(words, n=3, min_freq=2)
    starters = check_sentence_starter_uniformity(sentences)
    
    # 2. Sentence-by-Sentence Breakdown
    doc_mean_len = burstiness["mean_length"]
    doc_cv = burstiness["coefficient_of_variation"]
    
    analyzed_sentences: List[Dict[str, Any]] = []
    ai_sentence_count = 0
    human_sentence_count = 0
    mixed_sentence_count = 0
    
    for idx, s in enumerate(sentences):
        s_eval = analyze_sentence(s, idx + 1, doc_mean_len, doc_cv, sensitivity)
        analyzed_sentences.append(s_eval)
        if s_eval["signal"] == "ai":
            ai_sentence_count += 1
        elif s_eval["signal"] == "human":
            human_sentence_count += 1
        else:
            mixed_sentence_count += 1
            
    # 3. Composite Score Calculation
    # Factor weights:
    # - Low burstiness (uniform lengths): +AI signal
    # - Formulaic marker density: +AI signal
    # - Low Hapax Legomena / Low TTR: +AI signal
    # - Sentence starter repetition: +AI signal
    
    # Base calculation
    cv_penalty = max(0.0, (0.50 - doc_cv) * 110.0) if doc_cv < 0.50 else -((doc_cv - 0.50) * 80.0)
    marker_penalty = min(45.0, formulaic["density_per_100_words"] * 18.0)
    
    # Hapax / TTR influence
    hapax_factor = 0.0
    if diversity["hapax_ratio"] < 0.40 and word_count > 60:
        hapax_factor = (0.40 - diversity["hapax_ratio"]) * 50.0
    elif diversity["hapax_ratio"] > 0.55:
        hapax_factor = -12.0
        
    # Starter uniformity
    starter_penalty = 0.0
    if starters.get("most_frequent_starter_ratio", 0) > 0.35 and sentence_count > 4:
        starter_penalty = 12.0
        
    # Average individual sentence scores
    sentence_scores_avg = sum(s["score"] for s in analyzed_sentences) / max(1, len(analyzed_sentences))
    
    raw_ai_score = (0.45 * sentence_scores_avg) + (0.25 * (50.0 + cv_penalty)) + (0.20 * (marker_penalty * 2.0)) + (0.10 * (50.0 + hapax_factor + starter_penalty))
    
    # Apply sensitivity modifiers
    if sensitivity == "sensitive":
        raw_ai_score *= 1.10
    elif sensitivity == "conservative":
        raw_ai_score *= 0.90
        
    ai_score = max(3.0, min(97.0, round(raw_ai_score, 1)))
    human_score = max(3.0, min(97.0, round(100.0 - ai_score, 1)))
    
    # Mixed score estimation (degree to which human & AI traits intermingle)
    mixed_ratio = (mixed_sentence_count + min(ai_sentence_count, human_sentence_count)) / max(1, sentence_count)
    mixed_score = round(min(100.0, mixed_ratio * 100.0), 1)
    
    # 4. Confidence & Classification
    if word_count < 40:
        confidence = "Low"
        confidence_explanation = "Sample is under 40 words. Linguistic variance indicators require larger text samples for reliable statistical signals."
        classification = "Inconclusive / Short Text"
    elif word_count < 100:
        confidence = "Moderate"
        confidence_explanation = "Sample is between 40 and 100 words. Key metrics are discernible, though broader context improves confidence."
        if ai_score >= 65:
            classification = "Likely AI-Generated"
        elif human_score >= 65:
            classification = "Likely Human-Written"
        else:
            classification = "Mixed / Collaborative Content"
    else:
        confidence = "High"
        confidence_explanation = f"Solid statistical sample size ({word_count} words across {sentence_count} sentences)."
        if ai_score >= 68:
            classification = "Likely AI-Generated"
        elif human_score >= 68:
            classification = "Likely Human-Written"
        else:
            classification = "Mixed / Collaborative Content"
            
    # Synthesis summary narrative
    if classification == "Likely AI-Generated":
        summary_text = (
            f"The analyzed text demonstrates strong algorithmic markers, including uniform sentence pacing (CV: {doc_cv}), "
            f"{formulaic['total_markers']} typical synthetic discourse patterns, and standard lexical distributions."
        )
    elif classification == "Likely Human-Written":
        summary_text = (
            f"The text exhibits natural human hallmarks: high structural burstiness (CV: {doc_cv}), "
            f"dynamic rhythm, authentic idiom usage, and low formulaic transition density."
        )
    elif classification == "Mixed / Collaborative Content":
        summary_text = (
            f"The text exhibits an intermingled blend of natural human cadence alongside formulaic or heavily edited segments. "
            f"{ai_sentence_count} sentences lean synthetic while {human_sentence_count} show organic human variety."
        )
    else:
        summary_text = (
            "The sample is too brief to draw confident statistical conclusions. Provide a longer passage for a complete audit."
        )
        
    recommendations = generate_recommendations(
        ai_score, burstiness, diversity, formulaic, readability, word_count
    )
    
    method_name = "Built-in Linguistic Heuristics v1.0"
    if custom_provider and custom_provider != "heuristic":
        method_name = f"External API ({custom_provider})"
        
    return {
        "success": True,
        "method": method_name,
        "classification": classification,
        "confidence": confidence,
        "confidence_explanation": confidence_explanation,
        "summary": summary_text,
        "disclaimer": "This analysis provides an automated linguistic assessment of writing patterns. It does not establish authorship with certainty, and false positives or false negatives are possible.",
        "scores": {
            "ai_score": ai_score,
            "human_score": human_score,
            "mixed_score": mixed_score
        },
        "statistics": {
            "word_count": word_count,
            "char_count": char_count,
            "sentence_count": sentence_count,
            "reading_time_seconds": round((word_count / 225) * 60)
        },
        "sentence_breakdown": {
            "total_sentences": sentence_count,
            "ai_leaning_count": ai_sentence_count,
            "human_leaning_count": human_sentence_count,
            "mixed_neutral_count": mixed_sentence_count,
            "sentences": analyzed_sentences
        },
        "metrics": {
            "burstiness": burstiness,
            "lexical_diversity": diversity,
            "readability": readability,
            "formulaic_patterns": formulaic,
            "repeated_ngrams": repeated_ngrams,
            "sentence_starters": starters
        },
        "recommendations": recommendations
    }
