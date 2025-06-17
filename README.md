# Blood-Report-Insight
# Blood Report Health Insight Extractor

## Overview
This project is designed to automatically extract and analyze blood test results from a medical PDF report. It uses Python and Streamlit to deliver meaningful health insights — both direct abnormalities and deeper health patterns — all presented through a user-friendly interface.

---

## Features
- Uploads and reads PDF blood reports (semi-structured)
- Extracts test values like Hemoglobin, Glucose, Iron, etc.
- Detects high/low levels using reference ranges (first-order insights)
- Recognizes combined patterns such as anemia or insulin resistance (second-order insights)
- Outputs structured results as JSON
- Streamlit web app to make it interactive and usable by anyone

---

## Technologies Used
- Python 3
- Streamlit
- pdfplumber
- pandas
- regex

---

## How to Use

### 🔹 Option 1: Run the Web App
1. Launch the Streamlit app:
   ```bash
   streamlit run appclean.py
