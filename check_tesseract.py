"""
Helper script to check Tesseract OCR installation and provide setup guidance.
"""

import shutil
import platform
import os
from pathlib import Path


def check_tesseract():
    """Check if Tesseract is installed and provide setup instructions."""
    
    print("=" * 60)
    print("🔍 Checking Tesseract OCR Installation")
    print("=" * 60)
    print()
    
    # Check if Tesseract is in PATH
    tesseract_path = shutil.which("tesseract")
    
    if tesseract_path:
        print("✅ Tesseract OCR is installed!")
        print(f"   Location: {tesseract_path}")
        print()
        
        # Try to get version
        try:
            import subprocess
            result = subprocess.run(
                ["tesseract", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"   Version: {version_line}")
        except:
            pass
        
        # Check for Arabic language pack
        print()
        print("Checking for Arabic language pack...")
        try:
            import subprocess
            result = subprocess.run(
                ["tesseract", "--list-langs"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                langs = result.stdout.strip().split('\n')
                if 'ara' in langs:
                    print("✅ Arabic language pack is installed!")
                else:
                    print("⚠️  Arabic language pack not found")
                    print("   Install it for better Arabic invoice processing")
                    print("   Download from: https://github.com/tesseract-ocr/tessdata")
                    print("   Place in: C:\\Program Files\\Tesseract-OCR\\tessdata\\")
        except Exception as e:
            print(f"⚠️  Could not check language packs: {e}")
        
        print()
        print("=" * 60)
        print("✅ Setup Complete! You can use Tesseract OCR.")
        print("=" * 60)
        return True
        
    else:
        print("❌ Tesseract OCR is NOT installed or not in PATH")
        print()
        
        system = platform.system()
        
        if system == "Windows":
            print("📥 Installation Instructions for Windows:")
            print()
            print("1. Download Tesseract:")
            print("   https://github.com/UB-Mannheim/tesseract/wiki")
            print()
            print("2. Install the .exe file")
            print("   ⚠️  IMPORTANT: Check 'Add to PATH' during installation")
            print()
            print("3. Restart your terminal/IDE")
            print()
            print("4. Verify installation:")
            print("   tesseract --version")
            print()
            print("5. Install Arabic language pack:")
            print("   - Download: https://github.com/tesseract-ocr/tessdata/raw/main/ara.traineddata")
            print("   - Place in: C:\\Program Files\\Tesseract-OCR\\tessdata\\")
            print()
            print("💡 Alternative: Use EasyOCR in the UI (works without Tesseract)")
            print()
            
            # Check common installation paths
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            
            found_paths = []
            for path in common_paths:
                if Path(path).exists():
                    found_paths.append(path)
            
            if found_paths:
                print("⚠️  Found Tesseract in common locations but not in PATH:")
                for path in found_paths:
                    print(f"   {path}")
                print()
                print("To fix:")
                print("1. Add Tesseract to your system PATH:")
                print("   - Win+R → sysdm.cpl → Advanced → Environment Variables")
                print("   - Edit 'Path' → Add: C:\\Program Files\\Tesseract-OCR")
                print("2. Restart your terminal/IDE")
                print()
                
        elif system == "Darwin":  # macOS
            print("📥 Installation Instructions for macOS:")
            print()
            print("Run in terminal:")
            print("  brew install tesseract")
            print("  brew install tesseract-lang  # For Arabic support")
            print()
            
        else:  # Linux
            print("📥 Installation Instructions for Linux:")
            print()
            print("Run in terminal:")
            print("  sudo apt-get update")
            print("  sudo apt-get install tesseract-ocr")
            print("  sudo apt-get install tesseract-ocr-ara  # For Arabic support")
            print()
        
        print("=" * 60)
        print("📚 See INSTALL_TESSERACT_WINDOWS.md for detailed instructions")
        print("=" * 60)
        return False


if __name__ == "__main__":
    check_tesseract()
