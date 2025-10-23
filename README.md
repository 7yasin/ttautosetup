# TTGM Automatic Setup

## Simple Installation Instructions

This project is intended to run **after an automated ISO installation**. Two installation methods are provided.

---

### 1) Easy Method (Recommended)

If no antivirus software is actively running on your system, download and run:

- **TTAutoSetup.exe:**  
  https://github.com/7yasin/ttautosetup/releases/download/supportassist/TTAutoSetup.exe

During installation, Windows may display security prompts. Select “Run anyway” to proceed.

---

### 2) Alternative Method (if antivirus blocks the .exe)

If your antivirus prevents the executable from running, download the archive below and execute the batch file inside:

- **autoSetup.zip:**  
  https://github.com/7yasin/ttautosetup/releases/download/supportassist/autoSetup.zip

**Contents**
- `kurulum.bat` — Checks for Python and starts the setup.
- `main.py` — Main installer script (invoked automatically by the batch file).

> Note: The installers are safe. Some antivirus tools may show false positives.

---

## For Developers and Technical Users

Two distribution options are available:

### A. Single Executable (Standalone .exe)
- **File:** `TTAutoSetup.exe`  
- **Purpose:** Run on systems without a pre-installed Python runtime.  
- **Details:** `main.py` is packaged with PyInstaller and starts configuration tasks directly.  
- **Antivirus:** Some environments may still flag the binary as a false positive.

### B. Source + Batch-Based Installer (Fallback)
- **Package:** `autoSetup.zip`  
- **Includes:** `main.py` (Python script) and `kurulum.bat` (checks/installs Python and runs the script).  
- **Behavior:** If Python is missing, the batch file installs it (Microsoft Store or direct installer) and then executes `main.py`.

---

## Additional Information

- `kurulum.bat` verifies Python availability on Windows and installs it if necessary.  
- After prerequisites are met, the script applies all required system configuration steps automatically.

---

## Security Note

The source files are provided openly. You may review `main.py` and build your own executable if needed.
