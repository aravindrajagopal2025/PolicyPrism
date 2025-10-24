"""Confidence scoring for extraction quality assessment."""
from typing import Dict, List
from .schemas import PolicyExtraction, PolicySectionExtraction


class ConfidenceScorer:
    """Calculate and evaluate extraction confidence scores."""
    
    def __init__(self, threshold: float = 0.85):
        """
        Initialize confidence scorer.
        
        Args:
            threshold: Minimum confidence threshold for auto-approval
        """
        self.threshold = threshold
    
    def calculate_overall_confidence(self, extraction: PolicyExtraction) -> float:
        """
        Calculate overall confidence score for policy extraction.
        
        Args:
            extraction: PolicyExtraction result
            
        Returns:
            Overall confidence score (0.0-1.0)
        """
        scores = []
        
        # Base confidence from extraction
        if extraction.overall_confidence_score:
            scores.append(extraction.overall_confidence_score)
        
        # Section-level confidences
        if extraction.sections:
            section_scores = [s.confidence_score for s in extraction.sections if s.confidence_score]
            if section_scores:
                scores.append(sum(section_scores) / len(section_scores))
        
        # Coverage criteria confidences
        coverage_scores = []
        for section in extraction.sections:
            coverage_scores.extend([c.confidence_score for c in section.coverage_criteria if c.confidence_score])
        if coverage_scores:
            scores.append(sum(coverage_scores) / len(coverage_scores))
        
        # Exclusion confidences
        exclusion_scores = []
        for section in extraction.sections:
            exclusion_scores.extend([e.confidence_score for e in section.exclusions if e.confidence_score])
        if exclusion_scores:
            scores.append(sum(exclusion_scores) / len(exclusion_scores))
        
        # Calculate weighted average
        if not scores:
            return 0.5  # Default if no scores available
        
        return sum(scores) / len(scores)
    
    def requires_manual_review(
        self,
        extraction: PolicyExtraction,
        payer_policy_count: int,
        first_n_threshold: int = 5
    ) -> Dict[str, any]:
        """
        Determine if extraction requires manual review.
        
        Args:
            extraction: PolicyExtraction result
            payer_policy_count: Number of policies already processed for this payer
            first_n_threshold: Number of first policies per payer requiring review
            
        Returns:
            Dictionary with review decision and reasons
        """
        reasons = []
        requires_review = False
        
        # Check if this is one of the first N policies for the payer
        if payer_policy_count < first_n_threshold:
            requires_review = True
            reasons.append(f"First {first_n_threshold} policies per payer require manual review")
        
        # Check overall confidence
        overall_confidence = self.calculate_overall_confidence(extraction)
        if overall_confidence < self.threshold:
            requires_review = True
            reasons.append(f"Overall confidence ({overall_confidence:.2f}) below threshold ({self.threshold})")
        
        # Check for missing critical fields
        if not extraction.policy_name:
            requires_review = True
            reasons.append("Missing policy name")
        
        if not extraction.effective_date:
            requires_review = True
            reasons.append("Missing effective date")
        
        # Check section quality
        if not extraction.sections:
            requires_review = True
            reasons.append("No sections extracted")
        elif len(extraction.sections) < 2:
            requires_review = True
            reasons.append("Very few sections extracted (possible incomplete extraction)")
        
        # Check for low-confidence sections
        low_confidence_sections = [
            s for s in extraction.sections
            if s.confidence_score and s.confidence_score < self.threshold
        ]
        if low_confidence_sections:
            requires_review = True
            reasons.append(f"{len(low_confidence_sections)} sections with low confidence")
        
        return {
            "requires_review": requires_review,
            "reasons": reasons,
            "overall_confidence": overall_confidence,
            "low_confidence_sections": len(low_confidence_sections) if low_confidence_sections else 0
        }
    
    def get_quality_metrics(self, extraction: PolicyExtraction) -> Dict[str, any]:
        """
        Get detailed quality metrics for extraction.
        
        Args:
            extraction: PolicyExtraction result
            
        Returns:
            Dictionary with quality metrics
        """
        return {
            "overall_confidence": self.calculate_overall_confidence(extraction),
            "section_count": len(extraction.sections),
            "coverage_criteria_count": sum(len(s.coverage_criteria) for s in extraction.sections),
            "exclusion_count": sum(len(s.exclusions) for s in extraction.sections),
            "has_policy_name": bool(extraction.policy_name),
            "has_effective_date": bool(extraction.effective_date),
            "has_policy_number": bool(extraction.policy_number),
            "avg_section_confidence": sum(s.confidence_score for s in extraction.sections if s.confidence_score) / len(extraction.sections) if extraction.sections else 0.0
        }
