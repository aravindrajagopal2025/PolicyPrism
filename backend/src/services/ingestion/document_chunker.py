"""Document chunking for semantic section splitting."""
import re
from typing import List, Dict


class DocumentChunker:
    """Split extracted text into semantic sections."""
    
    def __init__(self, max_chunk_size: int = 4000):
        """
        Initialize document chunker.
        
        Args:
            max_chunk_size: Maximum characters per chunk
        """
        self.max_chunk_size = max_chunk_size
    
    def chunk_by_sections(self, text: str) -> List[Dict[str, any]]:
        """
        Split document into sections based on common policy document patterns.
        
        Args:
            text: Full document text
            
        Returns:
            List of section dictionaries with text and metadata
        """
        # Common section headers in policy documents
        section_patterns = [
            r'\n\s*(?:SECTION|Section)\s+\d+[:\.\s]+(.+?)\n',
            r'\n\s*(?:COVERAGE|Coverage)\s+(?:CRITERIA|Criteria)[:\s]*\n',
            r'\n\s*(?:EXCLUSIONS|Exclusions)[:\s]*\n',
            r'\n\s*(?:REQUIREMENTS|Requirements)[:\s]*\n',
            r'\n\s*(?:DEFINITIONS|Definitions)[:\s]*\n',
            r'\n\s*(?:PRIOR AUTHORIZATION|Prior Authorization)[:\s]*\n',
            r'\n\s*(?:LIMITATIONS|Limitations)[:\s]*\n',
            r'\n\s*(?:APPEALS|Appeals)\s+(?:PROCESS|Process)[:\s]*\n',
            r'\n\s*\d+\.\s+(.+?)\n',  # Numbered sections
            r'\n\s*[A-Z][:\.\s]+(.+?)\n',  # Lettered sections
        ]
        
        # Find all section boundaries
        boundaries = []
        for pattern in section_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                boundaries.append({
                    'position': match.start(),
                    'title': match.group(0).strip(),
                    'pattern': pattern
                })
        
        # Sort boundaries by position
        boundaries.sort(key=lambda x: x['position'])
        
        # If no sections found, treat entire document as one section
        if not boundaries:
            return self._chunk_large_text(text, "Full Document")
        
        # Split text into sections
        sections = []
        for i, boundary in enumerate(boundaries):
            start = boundary['position']
            end = boundaries[i + 1]['position'] if i + 1 < len(boundaries) else len(text)
            
            section_text = text[start:end].strip()
            
            # If section is too large, split it further
            if len(section_text) > self.max_chunk_size:
                subsections = self._chunk_large_text(section_text, boundary['title'])
                sections.extend(subsections)
            else:
                sections.append({
                    'title': boundary['title'],
                    'text': section_text,
                    'char_count': len(section_text),
                    'order_index': len(sections)
                })
        
        return sections
    
    def _chunk_large_text(self, text: str, base_title: str) -> List[Dict[str, any]]:
        """
        Split large text into smaller chunks.
        
        Args:
            text: Text to split
            base_title: Base title for chunks
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for para in paragraphs:
            para_size = len(para)
            
            if current_size + para_size > self.max_chunk_size and current_chunk:
                # Save current chunk
                chunks.append({
                    'title': f"{base_title} (Part {chunk_index + 1})",
                    'text': '\n\n'.join(current_chunk),
                    'char_count': current_size,
                    'order_index': chunk_index
                })
                
                # Start new chunk
                current_chunk = [para]
                current_size = para_size
                chunk_index += 1
            else:
                current_chunk.append(para)
                current_size += para_size
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'title': f"{base_title} (Part {chunk_index + 1})" if chunk_index > 0 else base_title,
                'text': '\n\n'.join(current_chunk),
                'char_count': current_size,
                'order_index': chunk_index
            })
        
        return chunks
    
    def identify_section_type(self, section_title: str, section_text: str) -> str:
        """
        Identify the type of policy section based on title and content.
        
        Args:
            section_title: Section title
            section_text: Section text content
            
        Returns:
            Section type string
        """
        title_lower = section_title.lower()
        text_lower = section_text.lower()
        
        # Check title first
        if any(keyword in title_lower for keyword in ['coverage', 'covered', 'benefits']):
            return 'COVERAGE_CRITERIA'
        elif any(keyword in title_lower for keyword in ['exclusion', 'not covered', 'excluded']):
            return 'EXCLUSIONS'
        elif any(keyword in title_lower for keyword in ['requirement', 'documentation', 'medical necessity']):
            return 'REQUIREMENTS'
        elif any(keyword in title_lower for keyword in ['definition', 'terms', 'glossary']):
            return 'DEFINITIONS'
        elif any(keyword in title_lower for keyword in ['prior authorization', 'pre-authorization', 'preauth']):
            return 'PRIOR_AUTHORIZATION'
        elif any(keyword in title_lower for keyword in ['limitation', 'limit', 'frequency']):
            return 'LIMITATIONS'
        elif any(keyword in title_lower for keyword in ['appeal', 'grievance', 'dispute']):
            return 'APPEALS_PROCESS'
        
        # Check content if title is ambiguous
        if 'not covered' in text_lower or 'excluded' in text_lower:
            return 'EXCLUSIONS'
        elif 'covered when' in text_lower or 'coverage criteria' in text_lower:
            return 'COVERAGE_CRITERIA'
        
        return 'OTHER'
