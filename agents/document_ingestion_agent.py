"""
Agent 1: Document Ingestion Agent
Converts PDF or image invoices into raw text using OCR or PDF parsing.
"""

import uuid
import json
import shutil
import warnings
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import PyPDF2  # Fallback
import fitz  # PyMuPDF - Best for Arabic PDFs
import pytesseract
from PIL import Image
import io

# Suppress EasyOCR/PyTorch warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torch')

try:
    import easyocr  # Fallback for low-quality images
except ImportError:
    easyocr = None

from prompts import AGENT_1_DOCUMENT_INGESTION_PROMPT


def check_tesseract_installed() -> Tuple[bool, str]:
    """
    Check if Tesseract OCR is installed and accessible.
    
    Returns:
        Tuple of (is_installed: bool, error_message: str)
    """
    tesseract_path = shutil.which("tesseract")
    if tesseract_path:
        return True, ""
    
    # Platform-specific error messages
    import platform
    system = platform.system()
    
    if system == "Windows":
        error_msg = (
            "Tesseract OCR is not installed or not in your PATH.\n\n"
            "To install Tesseract on Windows:\n"
            "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n"
            "2. Install the executable\n"
            "3. Add Tesseract to your PATH:\n"
            "   - Add 'C:\\Program Files\\Tesseract-OCR' to your system PATH\n"
            "   - Or set TESSDATA_PREFIX environment variable\n"
            "4. Restart your terminal/IDE\n\n"
            "Alternative: Enable EasyOCR in the UI (works without Tesseract)"
        )
    elif system == "Darwin":  # macOS
        error_msg = (
            "Tesseract OCR is not installed or not in your PATH.\n\n"
            "To install Tesseract on macOS:\n"
            "1. Install Homebrew if not already installed\n"
            "2. Run: brew install tesseract\n"
            "3. For Arabic support: brew install tesseract-lang\n\n"
            "Alternative: Enable EasyOCR in the UI (works without Tesseract)"
        )
    else:  # Linux
        error_msg = (
            "Tesseract OCR is not installed or not in your PATH.\n\n"
            "To install Tesseract on Linux:\n"
            "1. Run: sudo apt-get update\n"
            "2. Run: sudo apt-get install tesseract-ocr\n"
            "3. For Arabic support: sudo apt-get install tesseract-ocr-ara\n\n"
            "Alternative: Enable EasyOCR in the UI (works without Tesseract)"
        )
    
    return False, error_msg


class DocumentIngestionAgent:
    """Converts documents to raw text - does NOT extract meaning.
    
    Optimized for Arabic invoices with:
    - PyMuPDF for Arabic PDFs (RTL support)
    - Tesseract OCR with Arabic+English language support
    - EasyOCR as fallback for low-quality images
    """
    
    def __init__(self, use_easyocr: bool = False):
        """
        Initialize document ingestion agent.
        
        Args:
            use_easyocr: Use EasyOCR instead of Tesseract (slower but better for low-quality images)
        """
        self.prompt = AGENT_1_DOCUMENT_INGESTION_PROMPT
        self.use_easyocr = use_easyocr
        self.easyocr_reader = None
        self.tesseract_available = False
        self.tesseract_error = ""
        
        # Check if Tesseract is installed
        self.tesseract_available, self.tesseract_error = check_tesseract_installed()
        
        # If Tesseract not available and EasyOCR not enabled, try to enable EasyOCR automatically
        if not self.tesseract_available and not use_easyocr:
            if easyocr is not None:
                try:
                    # Try to initialize EasyOCR as fallback
                    # Suppress warnings during initialization
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        self.easyocr_reader = easyocr.Reader(['ar', 'en'], gpu=True, verbose=False)
                    self.use_easyocr = True
                    print("⚠️  Tesseract not found. Using EasyOCR as fallback.")
                except Exception as e:
                    print(f"⚠️  Warning: Neither Tesseract nor EasyOCR available. {e}")
            else:
                print("⚠️  Warning: EasyOCR not installed. Install with: pip install easyocr")
        
        # Initialize EasyOCR if explicitly requested
        if use_easyocr:
            if easyocr is None:
                print("⚠️  Warning: EasyOCR not installed. Install with: pip install easyocr")
                self.use_easyocr = False
            else:
                try:
                    # Initialize EasyOCR with Arabic and English
                    # Suppress warnings during initialization
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        self.easyocr_reader = easyocr.Reader(['ar', 'en'], gpu=True, verbose=False)
                except Exception as e:
                    print(f"Warning: EasyOCR initialization failed: {e}")
                    if not self.tesseract_available:
                        print("⚠️  No OCR engine available. Please install Tesseract or EasyOCR.")
                    self.use_easyocr = False
    
    def process(self, file_path: str) -> Dict[str, Any]:
        """
        Process a PDF or image file and extract raw text.
        
        Args:
            file_path: Path to the invoice file (PDF or image)
            
        Returns:
            Dictionary with document_id, raw_text, and source_type
        """
        file_path_obj = Path(file_path)
        document_id = str(uuid.uuid4())
        
        # Determine file type
        if file_path_obj.suffix.lower() == '.pdf':
            raw_text = self._extract_from_pdf(file_path)
            source_type = "pdf"
        else:
            # Assume image file
            raw_text = self._extract_from_image(file_path)
            source_type = "image"
        
        return {
            "document_id": document_id,
            "raw_text": raw_text,
            "source_type": source_type
        }
    
    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using PyMuPDF (best for Arabic)."""
        try:
            # Try PyMuPDF first (best for Arabic PDFs with RTL support)
            doc = fitz.open(file_path)
            text_parts = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(text)
            
            doc.close()
            extracted_text = "\n".join(text_parts)
            
            # If PDF has no extractable text, use OCR
            if not extracted_text.strip():
                extracted_text = self._ocr_pdf(file_path)
            
            return extracted_text
            
        except Exception as e:
            # Fallback 1: Try PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text_parts = []
                    
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text.strip():
                            text_parts.append(text)
                    
                    extracted_text = "\n".join(text_parts)
                    if extracted_text.strip():
                        return extracted_text
            except:
                pass
            
            # Fallback 2: Use OCR
            return self._ocr_pdf(file_path)
    
    def _extract_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR with Arabic+English support."""
        try:
            image = Image.open(file_path)
            
            # Use EasyOCR if enabled and initialized
            if self.use_easyocr and self.easyocr_reader:
                try:
                    results = self.easyocr_reader.readtext(file_path)
                    text_parts = [result[1] for result in results]
                    extracted_text = "\n".join(text_parts)
                    if extracted_text.strip():
                        return extracted_text
                    else:
                        return "[EasyOCR: No text detected in image]"
                except Exception as e:
                    print(f"EasyOCR failed: {e}")
                    if not self.tesseract_available:
                        return f"EasyOCR Error: {str(e)}\n\n{self.tesseract_error}"
            
            # Check if Tesseract is available
            if not self.tesseract_available:
                return (
                    f"❌ Tesseract OCR is not installed or not in PATH.\n\n"
                    f"{self.tesseract_error}\n\n"
                    f"💡 Tip: Enable 'Use EasyOCR' option in the UI to process images without Tesseract."
                )
            
            # Use Tesseract with Arabic+English language support
            # This handles Arabic digits (٠١٢٣٤٥٦٧٨٩) and Arabic text
            try:
                text = pytesseract.image_to_string(
                    image,
                    lang='ara+eng'  # Arabic + English
                )
                if text.strip():
                    return text
            except pytesseract.TesseractNotFoundError:
                return (
                    f"❌ Tesseract OCR is not installed or not in PATH.\n\n"
                    f"{self.tesseract_error}\n\n"
                    f"💡 Tip: Enable 'Use EasyOCR' option in the UI to process images without Tesseract."
                )
            except Exception as e:
                # If Arabic language pack not installed, try English only
                if 'ara' in str(e).lower() or 'language' in str(e).lower():
                    try:
                        text = pytesseract.image_to_string(image, lang='eng')
                        return text + "\n\n[Note: Arabic OCR language pack not available. Install Arabic language pack for better results with Arabic invoices.]"
                    except Exception as e2:
                        return f"Error: {str(e2)}\n\nOriginal error: {str(e)}"
                else:
                    return f"Tesseract Error: {str(e)}"
            
            return "[No text extracted from image]"
            
        except Exception as e:
            error_msg = f"Error extracting text from image: {str(e)}"
            if not self.tesseract_available and not (self.use_easyocr and self.easyocr_reader):
                error_msg += f"\n\n{self.tesseract_error}"
            return error_msg
    
    def _ocr_pdf(self, file_path: str) -> str:
        """Use OCR on PDF pages with Arabic+English support."""
        try:
            # Use PyMuPDF (fitz) to convert PDF pages to images
            # This avoids the need for poppler/pdf2image
            doc = fitz.open(file_path)
            text_parts = []
            
            for page_num in range(len(doc)):
                try:
                    page = doc[page_num]
                    # Render page to image (zoom=2 for better OCR quality)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    
                    # Convert fitz Pixmap to PIL Image
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Use EasyOCR if enabled
                    if self.use_easyocr and self.easyocr_reader:
                        try:
                            # Convert PIL image to numpy array for EasyOCR
                            import numpy as np
                            img_array = np.array(image)
                            results = self.easyocr_reader.readtext(img_array)
                            page_text = "\n".join([result[1] for result in results])
                            text_parts.append(page_text)
                            continue
                        except Exception as e:
                            print(f"EasyOCR failed for page {page_num}: {e}")
                            if not self.tesseract_available:
                                continue
                    
                    # Check if Tesseract is available
                    if not self.tesseract_available:
                        continue
                    
                    # Use Tesseract with Arabic+English
                    try:
                        text = pytesseract.image_to_string(image, lang='ara+eng')
                        text_parts.append(text)
                    except pytesseract.TesseractNotFoundError:
                        return (
                            f"❌ Tesseract OCR is not installed or not in PATH.\n\n"
                            f"{self.tesseract_error}\n\n"
                            f"💡 Tip: Enable 'Use EasyOCR' option in the UI to process PDFs without Tesseract."
                        )
                    except Exception as e:
                        # Fallback to English-only OCR
                        try:
                            text = pytesseract.image_to_string(image, lang='eng')
                            text_parts.append(text)
                        except:
                            text_parts.append(f"[Page {page_num} OCR Error: {str(e)}]")
                            
                except Exception as e:
                     text_parts.append(f"[Page {page_num} Processing Error: {str(e)}]")
            
            doc.close()
            
            if text_parts:
                result = "\n".join(text_parts)
                if not self.tesseract_available and self.use_easyocr:
                    result += "\n\n[Note: Using EasyOCR - Arabic language pack not available]"
                return result
            else:
                return (
                    f"❌ No OCR engine available.\n\n"
                    f"{self.tesseract_error}\n\n"
                    f"💡 Tip: Enable 'Use EasyOCR' option in the UI."
                )
        except Exception as e:
            error_msg = f"Error performing OCR on PDF: {str(e)}"
            if not self.tesseract_available and not (self.use_easyocr and self.easyocr_reader):
                error_msg += f"\n\n{self.tesseract_error}"
            return error_msg
