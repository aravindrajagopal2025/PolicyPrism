"""PDF text extraction using pymupdf for text-based PDFs."""
import pymupdf  # PyMuPDF
from pathlib import Path
from typing import Dict, List


class PDFExtractor:
    """Extract text from text-based PDF documents."""
    
    def extract_text(self, pdf_path: str | Path) -> Dict[str, any]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing:
                - full_text: Complete extracted text
                - pages: List of page texts
                - page_count: Number of pages
                - metadata: PDF metadata
                - is_text_based: Whether PDF contains extractable text
        """
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Open PDF
        doc = pymupdf.open(pdf_path)
        
        try:
            # Extract metadata
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "mod_date": doc.metadata.get("modDate", ""),
            }
            
            # Extract text from each page
            pages = []
            full_text_parts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                pages.append({
                    "page_number": page_num + 1,
                    "text": page_text,
                    "char_count": len(page_text)
                })
                full_text_parts.append(page_text)
            
            full_text = "\n\n".join(full_text_parts)
            
            # Determine if PDF is text-based (has extractable text)
            is_text_based = len(full_text.strip()) > 100  # Arbitrary threshold
            
            return {
                "full_text": full_text,
                "pages": pages,
                "page_count": len(doc),
                "metadata": metadata,
                "is_text_based": is_text_based,
                "file_size_bytes": pdf_path.stat().st_size
            }
            
        finally:
            doc.close()
    
    def extract_images(self, pdf_path: str | Path) -> List[Dict]:
        """
        Extract images from PDF (useful for OCR processing).
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of dictionaries containing image data
        """
        pdf_path = Path(pdf_path)
        doc = pymupdf.open(pdf_path)
        
        images = []
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    
                    images.append({
                        "page_number": page_num + 1,
                        "image_index": img_index,
                        "image_data": base_image["image"],
                        "image_ext": base_image["ext"],
                        "width": base_image["width"],
                        "height": base_image["height"]
                    })
            
            return images
            
        finally:
            doc.close()
