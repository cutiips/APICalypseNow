# 🌐 Eden AI Moderation Script
## A Python tool for text moderation using Eden AI's workflow API.

## 📜 Description

This script leverages the [Eden AI](https://www.edenai.co/) moderation workflow to evaluate and categorize text content for appropriateness. 
Results include rejection chances, categories, and validation status for better content management.

## 📋 Requirements / Pré-requis

- **Python:** Version 3.8 or later. 
- **Dependencies:** Install `requests`, `python-dotenv`, `tqdm`, and `pandas`.

## ⚡ Setup Instructions 
### Step 1: Clone the repository
```bash
git clone <repository-url>
cd <repository-directory>
```
### Step 2: Set up the environment

Create a `.env` file at the project root:
```bash
API_URL_POST=https://api.edenai.run/v2/workflow/WORKFLOW_ID/execution/
API_URL_GET=https://api.edenai.run/v2/workflow/WORKFLOW_ID/execution/{execution_id}/
API_KEY=YOUR_API_KEY_HERE
```

### Step 3: Install dependencies

Create and activate a virtual environment, then install requirements:
```bash
python -m venv env
source env\Scripts\activate # ON WINDOWS
pip install -r requirements.txt
```
## 🚀 Usage 
1. Run the script:
    ```bash
    python scripts.py
    ```
2. Choose an option:
   - Option 1: Process an entire Excel file with batch texts. 
   - Option 2: Test a single text manually.
3. For batch mode, provide the input Excel file path and a name for the output file.

### Example Output (Batch or Single)
```bash
Chance of Rejection (%): 80.60
Category: Violence
Status: Rejected
```