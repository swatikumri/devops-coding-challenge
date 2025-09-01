# 📥 Download Locations

This document provides the complete file paths for the Generic Bug Detection Tool zip file across different operating systems.

## 🖥️ **Current System (Linux/Ubuntu)**

**Absolute Path:** `/workspace/generic_bug_detection_tool.zip`  
**Downloads Folder:** `/home/ubuntu/Downloads/generic_bug_detection_tool.zip`  
**File Size:** 41,916 bytes (41.9 KB)  
**Created:** September 1, 2025 at 10:47  

## 🍎 **Mac (macOS) Locations**

### **Downloads Folder**
```
/Users/[username]/Downloads/generic_bug_detection_tool.zip
```

### **Desktop**
```
/Users/[username]/Desktop/generic_bug_detection_tool.zip
```

### **Documents**
```
/Users/[username]/Documents/generic_bug_detection_tool.zip
```

### **Home Directory**
```
/Users/[username]/generic_bug_detection_tool.zip
```

## 🪟 **Windows Locations**

### **Downloads Folder**
```
C:\Users\[username]\Downloads\generic_bug_detection_tool.zip
```

### **Desktop**
```
C:\Users\[username]\Desktop\generic_bug_detection_tool.zip
```

### **Documents**
```
C:\Users\[username]\Documents\generic_bug_detection_tool.zip
```

## 📱 **How to Download to Mac**

### **Method 1: Using Terminal (if you have access)**
```bash
# Navigate to Downloads folder
cd ~/Downloads

# Download the file (replace with actual download URL)
curl -O [download_url]/generic_bug_detection_tool.zip

# Or copy from current location if accessible
cp /workspace/generic_bug_detection_tool.zip ~/Downloads/
```

### **Method 2: Using Finder**
1. Open Finder
2. Navigate to your Downloads folder: `~/Downloads`
3. Copy the zip file to this location
4. The file will be at: `/Users/[your_username]/Downloads/generic_bug_detection_tool.zip`

### **Method 3: Using Web Browser**
1. Open your web browser
2. Navigate to the download link
3. Save to Downloads folder
4. Default location: `/Users/[your_username]/Downloads/generic_bug_detection_tool.zip`

## 🔍 **Finding Your Mac Username**

To find your Mac username, open Terminal and run:
```bash
whoami
```

This will show your username, which you can use in the paths above.

## 📂 **Mac-Specific Setup Instructions**

### **1. Extract the Zip File**
```bash
# Navigate to Downloads
cd ~/Downloads

# Extract the zip file
unzip generic_bug_detection_tool.zip

# Navigate to extracted folder
cd generic_bug_detection_tool
```

### **2. Install Python Dependencies**
```bash
# Install using pip3 (recommended for Mac)
pip3 install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### **3. Make Scripts Executable**
```bash
chmod +x run_generic_tests.sh
chmod +x demo_example.py
```

### **4. Run Setup**
```bash
./run_generic_tests.sh setup
```

### **5. Test the Tool**
```bash
# Run demo
python3 demo_example.py

# Or compare images
./run_generic_tests.sh compare --reference ref.png --current current.png --test-name "my_test"
```

## 🍎 **Mac-Specific Notes**

- **Python Version:** Mac typically comes with Python 3.8+ pre-installed
- **Package Manager:** Use `pip3` instead of `pip` for Python 3 packages
- **Permissions:** You may need to grant Terminal permission to run scripts
- **Security:** macOS may block unsigned scripts - you can allow them in System Preferences > Security & Privacy

## 📍 **Quick Reference**

| Operating System | Default Downloads Path |
|------------------|------------------------|
| **macOS** | `/Users/[username]/Downloads/` |
| **Windows** | `C:\Users\[username]\Downloads\` |
| **Linux/Ubuntu** | `/home/[username]/Downloads/` |

## 🔗 **File Information**

- **Filename:** `generic_bug_detection_tool.zip`
- **Size:** 41.9 KB (41,916 bytes)
- **Contents:** 17 files including Python scripts, configuration files, documentation
- **Compression:** ZIP format
- **Created:** September 1, 2025

---

**Note:** Replace `[username]` with your actual username in all paths above.