# Installing Tesseract OCR on Windows

## 🚀 Quick Installation Guide

### Step 1: Download Tesseract

1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer (`.exe` file)
3. Recommended: Download the installer with all language packs included

### Step 2: Install Tesseract

1. Run the downloaded `.exe` installer
2. **Important:** During installation, check the box to "Add to PATH"
3. Or note the installation path (usually: `C:\Program Files\Tesseract-OCR`)

### Step 3: Add to PATH (if not done during installation)

If you didn't add to PATH during installation:

1. **Find your Tesseract installation folder:**
   - Usually: `C:\Program Files\Tesseract-OCR`
   - Or: `C:\Program Files (x86)\Tesseract-OCR`

2. **Add to System PATH:**
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Go to "Advanced" tab → Click "Environment Variables"
   - Under "System variables", find "Path" → Click "Edit"
   - Click "New" → Add: `C:\Program Files\Tesseract-OCR`
   - Click "OK" on all dialogs

3. **Restart your terminal/IDE** (important!)

### Step 4: Verify Installation

Open a **new** PowerShell or Command Prompt and run:

```powershell
tesseract --version
```

You should see version information. If you see "command not found", PATH wasn't set correctly.

### Step 5: Install Arabic Language Pack

1. Download Arabic language data: `ara.traineddata`
   - From: https://github.com/tesseract-ocr/tessdata
   - Direct link: https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata

2. Place the file in:
   ```
   C:\Program Files\Tesseract-OCR\tessdata\
   ```

3. Verify Arabic is available:
   ```powershell
   tesseract --list-langs
   ```
   Should show: `ara` and `eng` in the list

## ✅ Quick Test

Test Tesseract with Arabic support:

```powershell
# Create a test image or use an existing one
tesseract test_image.png output -l ara+eng
```

## 🔧 Troubleshooting

### Issue: "tesseract is not installed or it's not in your PATH"

**Solution 1: Check PATH**
```powershell
$env:Path -split ';' | Select-String -Pattern "Tesseract"
```
Should show your Tesseract path.

**Solution 2: Manually set PATH in PowerShell (temporary)**
```powershell
$env:Path += ";C:\Program Files\Tesseract-OCR"
```

**Solution 3: Set TESSDATA_PREFIX (if language packs not found)**
```powershell
$env:TESSDATA_PREFIX = "C:\Program Files\Tesseract-OCR\tessdata"
```

### Issue: Arabic language pack not found

1. Check if `ara.traineddata` exists in `tessdata` folder
2. Verify file name is exactly `ara.traineddata` (not `ara.traineddata.txt`)
3. Restart terminal after adding language pack

## 💡 Alternative: Use EasyOCR

If Tesseract installation is problematic, you can use EasyOCR instead:

1. **In the Streamlit UI:**
   - Enable the "Use EasyOCR" checkbox
   - Works without Tesseract installation

2. **EasyOCR is already installed** (in requirements.txt)
   - Just enable it in the UI
   - Slower but works immediately

## 📚 Additional Resources

- Tesseract Windows Installation: https://github.com/UB-Mannheim/tesseract/wiki
- Language Packs: https://github.com/tesseract-ocr/tessdata
- Tesseract Documentation: https://tesseract-ocr.github.io/

---

**After installation, restart your terminal/IDE and run the app again!** 🚀
