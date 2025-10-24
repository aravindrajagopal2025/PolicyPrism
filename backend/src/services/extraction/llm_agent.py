"""Pydantic AI agent for policy document extraction."""
from pydantic_ai import Agent
from typing import Dict, Any

from .schemas import PolicyExtraction, PolicySectionExtraction
from ...config import settings


class PolicyExtractionAgent:
    """Pydantic AI agent for extracting structured data from policy documents."""
    
    def __init__(self):
        """Initialize the Pydantic AI agent."""
        # Determine model based on configuration
        if settings.llm_provider == "openai":
            model = f"openai:{settings.pydantic_ai_model}"
        elif settings.llm_provider == "anthropic":
            model = f"anthropic:{settings.pydantic_ai_model}"
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
        
        # Create agent for full policy extraction
        self.policy_agent = Agent(
            model=model,
            result_type=PolicyExtraction,
            system_prompt="""You are an expert at extracting structured information from healthcare policy documents.

Your task is to:
1. Identify the policy name, number, payer, and dates
2. Categorize sections by type (coverage criteria, exclusions, requirements, etc.)
3. Extract specific coverage criteria including procedure names, codes, and conditions
4. Extract exclusions with rationale
5. Provide confidence scores for each extraction (0.0-1.0)

Be precise and conservative with confidence scores. If information is unclear or ambiguous, reflect that in lower confidence scores.

For dates, use ISO format (YYYY-MM-DD). For procedure codes, use standard CPT/HCPCS codes if mentioned.
"""
        )
        
        # Create agent for section-level extraction
        self.section_agent = Agent(
            model=model,
            result_type=PolicySectionExtraction,
            system_prompt="""You are an expert at extracting structured information from policy document sections.

Analyze the section and extract:
1. Section type (COVERAGE_CRITERIA, EXCLUSIONS, REQUIREMENTS, etc.)
2. Title and section number
3. Coverage criteria with specific details
4. Exclusions with rationale
5. Confidence score for the extraction

Be thorough but precise. Extract all relevant coverage criteria and exclusions mentioned in the section.
"""
        )
    
    async def extract_policy(self, document_text: str, payer_name: str) -> PolicyExtraction:
        """
        Extract complete policy information from document text.
        
        Args:
            document_text: Full policy document text
            payer_name: Name of the payer (helps with context)
            
        Returns:
            PolicyExtraction with structured data
        """
        # Prepare context
        context = f"Payer: {payer_name}\n\nDocument:\n{document_text}"
        
        # Run extraction
        result = await self.policy_agent.run(
            context,
            message_history=[]
        )
        
        return result.data
    
    async def extract_section(self, section_text: str, section_title: str) -> PolicySectionExtraction:
        """
        Extract structured data from a single policy section.
        
        Args:
            section_text: Section text content
            section_title: Section title/heading
            
        Returns:
            PolicySectionExtraction with structured data
        """
        # Prepare context
        context = f"Section Title: {section_title}\n\nContent:\n{section_text}"
        
        # Run extraction
        result = await self.section_agent.run(
            context,
            message_history=[]
        )
        
        return result.data
    
    async def extract_with_retry(
        self,
        document_text: str,
        payer_name: str,
        max_retries: int = 2
    ) -> PolicyExtraction:
        """
        Extract policy with automatic retry on failure.
        
        Args:
            document_text: Full policy document text
            payer_name: Name of the payer
            max_retries: Maximum number of retry attempts
            
        Returns:
            PolicyExtraction with structured data
            
        Raises:
            Exception if all retries fail
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await self.extract_policy(document_text, payer_name)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    # Wait before retry (exponential backoff)
                    import asyncio
                    wait_time = (2 ** attempt) * settings.retry_backoff_base
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    raise last_error
