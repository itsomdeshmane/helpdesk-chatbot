"""
Answer Quality Scoring Module - Production Ready
Evaluates response quality, detects hallucinations, and provides confidence scores
"""

from openai import OpenAI
from config import OPENAI_API_KEY, GPT_MODEL
from typing import Dict, List, Optional, Tuple
import re
import json
from dataclasses import dataclass
from enum import Enum


# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


class ConfidenceLevel(Enum):
    """Confidence levels for answers"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNCERTAIN = "uncertain"


@dataclass
class QualityScore:
    """Represents the quality assessment of an answer"""
    overall_score: float  # 0.0 to 1.0
    confidence: ConfidenceLevel
    groundedness_score: float  # How well grounded in context
    relevance_score: float  # How relevant to the question
    completeness_score: float  # How complete the answer is
    issues: List[str]  # List of identified issues
    suggestions: List[str]  # Suggestions for improvement
    needs_escalation: bool  # Whether to suggest human support
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'overall_score': self.overall_score,
            'confidence': self.confidence.value,
            'groundedness_score': self.groundedness_score,
            'relevance_score': self.relevance_score,
            'completeness_score': self.completeness_score,
            'issues': self.issues,
            'suggestions': self.suggestions,
            'needs_escalation': self.needs_escalation
        }


def score_answer_quality(
    query: str,
    context: str,
    answer: str,
    use_ai: bool = True
) -> QualityScore:
    """
    Score the quality of an answer based on multiple criteria.
    
    Args:
        query: The user's question
        context: The document context used to generate the answer
        answer: The generated answer
        use_ai: Whether to use AI for scoring (more accurate but slower)
    
    Returns:
        QualityScore object with detailed assessment
    """
    # First, run rule-based checks (fast)
    rule_score = _rule_based_scoring(query, context, answer)
    
    # If answer fails basic checks, return early
    if rule_score.overall_score < 0.3:
        return rule_score
    
    # If AI scoring is enabled, enhance with AI assessment
    if use_ai:
        try:
            ai_score = _ai_based_scoring(query, context, answer)
            # Combine rule-based and AI scores
            return _combine_scores(rule_score, ai_score)
        except Exception as e:
            print(f"⚠️ AI scoring failed, using rule-based only: {e}", flush=True)
    
    return rule_score


def _rule_based_scoring(
    query: str,
    context: str,
    answer: str
) -> QualityScore:
    """
    Fast rule-based quality scoring.
    
    Checks:
    - Answer length
    - Keyword overlap with query
    - Context grounding indicators
    - Uncertainty phrases
    - Error indicators
    """
    issues = []
    suggestions = []
    
    # Initialize scores
    groundedness = 1.0
    relevance = 1.0
    completeness = 1.0
    
    answer_lower = answer.lower()
    query_lower = query.lower()
    context_lower = context.lower() if context else ""
    
    # Check 1: Answer length
    word_count = len(answer.split())
    if word_count < 10:
        completeness -= 0.3
        issues.append("Answer is very short")
        suggestions.append("Consider providing more detailed explanation")
    elif word_count > 500:
        issues.append("Answer may be too verbose")
        suggestions.append("Consider being more concise")
    
    # Check 2: Uncertainty indicators
    uncertainty_phrases = [
        "i don't have", "not in the documentation", "i'm not sure",
        "please contact support", "i cannot find", "no information",
        "unable to find", "doesn't exist", "not available",
        "i apologize", "sorry", "unfortunately"
    ]
    
    uncertainty_count = sum(1 for phrase in uncertainty_phrases if phrase in answer_lower)
    if uncertainty_count > 0:
        groundedness -= 0.2 * uncertainty_count
        if uncertainty_count >= 2:
            issues.append("Answer indicates uncertainty")
    
    # Check 3: Error indicators
    error_phrases = [
        "error", "failed", "exception", "could not process",
        "something went wrong", "try again"
    ]
    
    if any(phrase in answer_lower for phrase in error_phrases):
        groundedness -= 0.4
        issues.append("Answer contains error indicators")
    
    # Check 4: Query keyword presence in answer
    query_keywords = _extract_keywords(query_lower)
    answer_keywords = set(answer_lower.split())
    keyword_overlap = len(query_keywords & answer_keywords) / max(len(query_keywords), 1)
    
    if keyword_overlap < 0.2:
        relevance -= 0.3
        issues.append("Answer may not directly address the question")
    
    # Check 5: Context grounding - check if answer uses context
    if context_lower:
        context_keywords = _extract_keywords(context_lower)
        context_overlap = len(context_keywords & answer_keywords) / max(len(context_keywords), 1)
        
        if context_overlap < 0.1:
            groundedness -= 0.2
            issues.append("Answer may not be grounded in provided context")
    
    # Check 6: Hallucination indicators (generic statements)
    hallucination_phrases = [
        "in general", "typically", "usually", "most systems",
        "as an ai", "based on my training", "from my knowledge"
    ]
    
    if any(phrase in answer_lower for phrase in hallucination_phrases):
        groundedness -= 0.3
        issues.append("Answer may contain information not from documentation")
    
    # Check 7: Completeness - look for list indicators
    if ":" in query_lower or "list" in query_lower or "what are" in query_lower:
        if not any(char in answer for char in ['•', '-', '1.', '2.', '*']):
            completeness -= 0.2
            suggestions.append("Consider using bullet points or numbered lists")
    
    # Normalize scores
    groundedness = max(0.0, min(1.0, groundedness))
    relevance = max(0.0, min(1.0, relevance))
    completeness = max(0.0, min(1.0, completeness))
    
    # Calculate overall score
    overall = (groundedness * 0.4 + relevance * 0.35 + completeness * 0.25)
    
    # Determine confidence level
    confidence = _determine_confidence(overall, issues)
    
    # Determine if escalation is needed
    needs_escalation = overall < 0.4 or len(issues) >= 3
    
    if needs_escalation and "Would you like to connect with support" not in answer:
        suggestions.append("Consider suggesting human support for complex issues")
    
    return QualityScore(
        overall_score=overall,
        confidence=confidence,
        groundedness_score=groundedness,
        relevance_score=relevance,
        completeness_score=completeness,
        issues=issues,
        suggestions=suggestions,
        needs_escalation=needs_escalation
    )


def _ai_based_scoring(
    query: str,
    context: str,
    answer: str
) -> QualityScore:
    """
    AI-based quality scoring using GPT.
    More accurate but slower than rule-based.
    """
    # Truncate for API limits
    context_truncated = context[:2000] if context else ""
    answer_truncated = answer[:1500]
    
    system_prompt = """You are a quality evaluator for helpdesk AI responses.
Evaluate the answer based on these criteria:

1. GROUNDEDNESS (0-10): Is the answer fully supported by the provided context? 
   - 10 = Every claim is directly from context
   - 0 = Answer contains information not in context (hallucination)

2. RELEVANCE (0-10): Does the answer address the user's question?
   - 10 = Directly and completely answers the question
   - 0 = Completely off-topic

3. COMPLETENESS (0-10): Is the answer thorough?
   - 10 = Covers all aspects of the question
   - 0 = Missing critical information

Also identify any ISSUES and provide SUGGESTIONS for improvement.

Return JSON format:
{
    "groundedness": 8,
    "relevance": 9,
    "completeness": 7,
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1"],
    "needs_escalation": false
}"""

    user_prompt = f"""Evaluate this response:

CONTEXT:
{context_truncated}

QUESTION:
{query}

ANSWER:
{answer_truncated}

Return only valid JSON."""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Use faster model for evaluation
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.0,
        max_tokens=300
    )
    
    content = response.choices[0].message.content.strip()
    
    # Parse JSON response
    try:
        # Handle markdown code blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1].split("```")[0]
        
        result = json.loads(content)
        
        return QualityScore(
            overall_score=0.0,  # Will be calculated in combine
            confidence=ConfidenceLevel.MEDIUM,  # Will be updated in combine
            groundedness_score=result.get('groundedness', 5) / 10,
            relevance_score=result.get('relevance', 5) / 10,
            completeness_score=result.get('completeness', 5) / 10,
            issues=result.get('issues', []),
            suggestions=result.get('suggestions', []),
            needs_escalation=result.get('needs_escalation', False)
        )
    except json.JSONDecodeError:
        # Return neutral score if parsing fails
        return QualityScore(
            overall_score=0.5,
            confidence=ConfidenceLevel.MEDIUM,
            groundedness_score=0.5,
            relevance_score=0.5,
            completeness_score=0.5,
            issues=["Could not evaluate with AI"],
            suggestions=[],
            needs_escalation=False
        )


def _combine_scores(rule_score: QualityScore, ai_score: QualityScore) -> QualityScore:
    """
    Combine rule-based and AI-based scores.
    Uses weighted average with more weight on AI for groundedness.
    """
    # Weight: 40% rule-based, 60% AI-based for groundedness
    # Weight: 50-50 for others
    groundedness = rule_score.groundedness_score * 0.4 + ai_score.groundedness_score * 0.6
    relevance = rule_score.relevance_score * 0.5 + ai_score.relevance_score * 0.5
    completeness = rule_score.completeness_score * 0.5 + ai_score.completeness_score * 0.5
    
    # Combine issues (deduplicate)
    all_issues = list(set(rule_score.issues + ai_score.issues))
    all_suggestions = list(set(rule_score.suggestions + ai_score.suggestions))
    
    # Calculate overall
    overall = groundedness * 0.4 + relevance * 0.35 + completeness * 0.25
    
    # Determine confidence
    confidence = _determine_confidence(overall, all_issues)
    
    # Needs escalation if either says so
    needs_escalation = rule_score.needs_escalation or ai_score.needs_escalation
    
    return QualityScore(
        overall_score=overall,
        confidence=confidence,
        groundedness_score=groundedness,
        relevance_score=relevance,
        completeness_score=completeness,
        issues=all_issues[:5],  # Limit to top 5
        suggestions=all_suggestions[:3],  # Limit to top 3
        needs_escalation=needs_escalation
    )


def _determine_confidence(score: float, issues: List[str]) -> ConfidenceLevel:
    """Determine confidence level based on score and issues"""
    if score >= 0.8 and len(issues) <= 1:
        return ConfidenceLevel.HIGH
    elif score >= 0.6 and len(issues) <= 2:
        return ConfidenceLevel.MEDIUM
    elif score >= 0.4:
        return ConfidenceLevel.LOW
    else:
        return ConfidenceLevel.UNCERTAIN


def _extract_keywords(text: str) -> set:
    """Extract keywords from text"""
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'it', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'we', 'they', 'what', 'which', 'who',
        'where', 'when', 'why', 'how'
    }
    
    words = set(re.findall(r'\b[a-z]+\b', text.lower()))
    return {w for w in words if len(w) > 2 and w not in stopwords}


def detect_hallucination(
    answer: str,
    context: str,
    threshold: float = 0.3
) -> Tuple[bool, List[str]]:
    """
    Detect potential hallucinations in an answer.
    
    Args:
        answer: The generated answer
        context: The source context
        threshold: Groundedness threshold below which hallucination is suspected
    
    Returns:
        Tuple of (is_hallucination, list of suspicious statements)
    """
    # Quick rule-based check first
    answer_sentences = re.split(r'[.!?]', answer)
    context_lower = context.lower() if context else ""
    
    suspicious_statements = []
    
    for sentence in answer_sentences:
        sentence = sentence.strip()
        if len(sentence) < 10:
            continue
        
        # Check if sentence keywords are in context
        keywords = _extract_keywords(sentence.lower())
        if not keywords:
            continue
        
        # Check keyword overlap
        context_keywords = _extract_keywords(context_lower)
        overlap = len(keywords & context_keywords) / len(keywords)
        
        if overlap < 0.2:
            suspicious_statements.append(sentence)
    
    # Consider hallucination if more than 30% of statements are suspicious
    total_sentences = len([s for s in answer_sentences if len(s.strip()) > 10])
    if total_sentences > 0:
        suspicious_ratio = len(suspicious_statements) / total_sentences
        is_hallucination = suspicious_ratio > threshold
    else:
        is_hallucination = False
    
    return is_hallucination, suspicious_statements


def generate_escalation_message(
    query: str,
    quality_score: QualityScore
) -> str:
    """
    Generate a professional escalation message when answer quality is low.
    
    Args:
        query: The original user query
        quality_score: The quality assessment
    
    Returns:
        Escalation message string
    """
    confidence = quality_score.confidence.value
    
    if quality_score.overall_score < 0.3:
        return f"""I apologize, but I'm having difficulty finding the specific information you need about this topic in our documentation.

Would you like me to:
1. Connect you with a support specialist who can help
2. Try rephrasing your question more specifically
3. Point you to the relevant documentation section for manual lookup

Please let me know how I can best assist you."""
    
    elif quality_score.confidence == ConfidenceLevel.LOW:
        return f"""I found some information that may be relevant, but I want to make sure you get the most accurate answer.

Based on the documentation, here's what I found (though I recommend verifying with support):

If this doesn't fully answer your question, I can connect you with a specialist who can provide more detailed guidance."""
    
    else:
        return ""  # No escalation needed

