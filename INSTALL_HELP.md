# INSTALLATION GUIDE - Universal Sentiment Analysis Platform

## ⚠️ Virtual Environment Issue Detected

Your `.venv` folder is pointing to a non-existent Python installation. Here are solutions:

---

## 🔧 Solution 1: Recreate Virtual Environment (Recommended)

### Step 1: Delete old virtual environment
```bash
# In PowerShell or Command Prompt
rmdir /s .venv
```

### Step 2: Create new virtual environment
```bash
# Find your Python installation
where python
# or
python3 --version

# Create new venv with working Python
python -m venv .venv
# or if python doesn't work:
python3 -m venv .venv
# or use full path:
C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe -m venv .venv
```

### Step 3: Activate and install
```bash
.venv\Scripts\activate
pip install flask flask-cors vaderSentiment pandas beautifulsoup4 lxml
```

### Step 4: Run the app
```bash
python app.py
```

---

## 🚀 Solution 2: Use System Python (Quick Fix)

If you have Python installed system-wide with pip:

### Step 1: Install packages globally
```bash
pip install flask flask-cors vaderSentiment pandas beautifulsoup4 lxml
```

### Step 2: Run directly
```bash
python app.py
```

---

## 💡 Solution 3: Use Anaconda/Miniconda

If you have Anaconda or Miniconda:

```bash
conda create -n sentiment python=3.11
conda activate sentiment
pip install flask flask-cors vaderSentiment pandas beautifulsoup4 lxml
python app.py
```

---

## 🔍 Troubleshooting

### Check if Python has pip:
```bash
python -m pip --version
```

### If pip is missing:
```bash
# Download get-pip.py from https://bootstrap.pypa.io/get-pip.py
python get-pip.py
```

### Check Python version:
```bash
python --version
# Should be Python 3.7 or higher
```

---

## ✅ Once Installed

1. Run: `python app.py`
2. Open browser: `http://localhost:5000`
3. Start analyzing!

---

## 📦 Required Packages

- flask
- flask-cors
- vaderSentiment
- pandas
- beautifulsoup4
- lxml

All other dependencies (numpy, matplotlib) will be installed automatically.
