"""OCR processing using pytesseract for scanned/image-based PDFs."""
import pytesseract
from PIL import Image
from pathlib import Path
from typing import Dict, List
import io


class OCRProcessor:
    """Process scanned PDFs using OCR (Optical Character Recognition)."""
    
    def __init__(self, language: str = "eng"):
        """
        Initialize OCR processor.
        
        Args:
            language: Tesseract language code (default: 'eng' for English)
        """
        self.language = language
    
    def process_image(self, image_data: bytes, image_format: str = "PNG") -> str:
        """
        Extract text from a single image using OCR.
        
        Args:
            image_data: Image bytes
            image_format: Image format (PNG, JPEG, etc.)
            
        Returns:
            Extracted text
        """
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Perform OCR
        text = pytesseract.image_to_string(image, lang=self.language)
        
        return text
    
    def process_images_from_pdf(self, images: List[Dict]) -> Dict[str, any]:
        """
        Process multiple images extracted from a PDF.
        
        Args:
            images: List of image dictionaries from PDFExtractor.extract_images()
            
        Returns:
            Dictionary containing:
                - full_text: Complete OCR text
                - pages: List of page texts
                - page_count: Number of pages processed
        """
        pages_text = {}
        
        for img_data in images:
            page_num = img_data["page_number"]
            image_bytes = img_data["image_data"]
            
            # Perform OCR on image
            text = self.process_image(image_bytes)
            
            # Aggregate text by page
            if page_num not in pages_text:
                pages_text[page_num] = []
            pages_text[page_num].append(text)
        
        # Combine text for each page
        pages = []
        full_text_parts = []
        
        for page_num in sorted(pages_text.keys()):
            page_text = "\n".join(pages_text[page_num])
            pages.append({
                "page_number": page_num,
                "text": page_text,
                "char_count": len(page_text)
            })
            full_text_parts.append(page_text)
        
        full_text = "\n\n".join(full_text_parts)
        
        return {
            "full_text": full_text,
            "pages": pages,
            "page_count": len(pages)
        }
    
    def get_confidence(self, image_data: bytes) -> float:
        """
        Get OCR confidence score for an image.
        
        Args:
            image_data: Image bytes
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        image = Image.open(io.BytesIO(image_data))
        
        # Get detailed OCR data including confidence
        data = pytesseract.image_to_data(image, lang=self.language, output_type=pytesseract.Output.DICT)
        
        # Calculate average confidence (excluding -1 values which indicate no text)
        confidences = [int(conf) for conf in data['conf'] if int(conf) != -1]
        
        if not confidences:
            return 0.0
        
        avg_confidence = sum(confidences) / len(confidences)
        return avg_confidence / 100.0  # Convert to 0.0-1.0 range
