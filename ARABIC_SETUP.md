# Arabic Invoice Processing Setup Guide

## 🌍 Arabic-Optimized Stack

This system is optimized for Arabic invoices using the best tools for Arabic text, RTL layouts, and mixed Arabic/English content.

## ✅ Required Tools

### 1. Tesseract OCR with Arabic Language Pack

**Installation:**

#### Windows:
1. Download Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install the executable
3. Download Arabic language data: `ara.traineddata`
4. Place it in: `C:\Program Files\Tesseract-OCR\tessdata\`

#### macOS:
```bash
brew install tesseract
brew install tesseract-lang  # Includes Arabic
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-ara  # Arabic language pack
```

**Verify installation:**
```bash
tesseract --list-langs
# Should show: ara, eng, and others
```

### 2. PyMuPDF (fitz) - Already in requirements.txt

Best for Arabic PDFs with RTL (Right-to-Left) support.

### 3. EasyOCR (Optional - for low-quality images)

Already in requirements.txt. Slower but better for:
- Photos of invoices
- Low-quality scans
- Handwritten text

### 4. GPT-4o Model

**Recommended:** Use GPT-4o for best Arabic understanding.

Set in `.env`:
```bash
OPENAI_MODEL=gpt-4o
```

Or use `gpt-4o-mini` for cost-effective processing.

## 🚀 Quick Setup

1. **Install Tesseract with Arabic:**
   ```bash
   # Follow platform-specific instructions above
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up `.env` file:**
   ```bash
   OPENAI_API_KEY=your_key_here
   OPENAI_MODEL=gpt-4o  # Best for Arabic
   ```

4. **Run the UI:**
   ```bash
   streamlit run app.py
   ```

## 📋 What Makes This Arabic-Optimized?

### ✅ OCR Layer
- **Tesseract with `ara+eng`** - Handles Arabic digits (٠١٢٣٤٥٦٧٨٩) and Arabic text
- **PyMuPDF** - Better RTL support than PyPDF2
- **EasyOCR fallback** - For low-quality images

### ✅ LLM Layer
- **GPT-4o** - Best Arabic understanding
- **Arabic-aware prompt** - Understands Arabic invoice terms:
  - فاتورة (invoice)
  - المبلغ الإجمالي (total amount)
  - تاريخ الاستحقاق (due date)
  - شامل الضريبة (including tax)

### ✅ Extraction Rules
- Handles Arabic digits → converts to numbers
- Understands Arabic date formats
- Semantic extraction (not position-based)
- Handles mixed Arabic/English invoices

## 🧪 Testing Arabic Invoices

Test with Arabic invoices that have:
- ✅ Arabic text (RTL layout)
- ✅ Arabic digits (٠١٢٣٤٥٦٧٨٩)
- ✅ Mixed Arabic/English
- ✅ Various date formats (Hijri, Gregorian)

## 🔧 Troubleshooting

### Issue: "Arabic OCR not available"
**Solution:** Install Arabic language pack for Tesseract (see installation above)

### Issue: Poor Arabic text extraction
**Solutions:**
1. Use EasyOCR option in UI (checkbox)
2. Ensure Tesseract Arabic pack is installed
3. Use GPT-4o model (not gpt-4o-mini)

### Issue: Wrong date format
**Solution:** The system normalizes dates. Check validation errors in UI.

## 📊 Arabic Invoice Fields Supported

- **biller_name** (اسم الجهة)
- **biller_address** (العنوان)
- **total_amount** (المبلغ الإجمالي النهائي)
- **due_date** (تاريخ الاستحقاق)

## 🎯 Why This Stack?

> "Arabic invoices require semantic understanding, not keyword matching. GPT-4o combined with Arabic OCR provides robust handling of RTL layouts, mixed numerals, and regional invoice terminology."

This combination ensures:
- ✅ Accurate Arabic text extraction
- ✅ Understanding of Arabic business terms
- ✅ Handling of Arabic digits
- ✅ RTL layout support
- ✅ Mixed language invoices

---

**Ready to process Arabic invoices!** 🚀
