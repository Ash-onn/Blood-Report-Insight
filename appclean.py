# app.py
import streamlit as st
import pdfplumber
import re
import pandas as pd
import json
from io import BytesIO

st.set_page_config(page_title="Blood Report Analyzer", layout="wide")

st.title("Blood Report Health Insight Extractor")

uploaded_pdf = st.file_uploader("Upload your blood report PDF", type="pdf")

def extract_text_from_pdf(file):
    extracted_text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            extracted_text += page.extract_text() + "\n"
    return extracted_text

def extract_tests(text):
    pattern = re.compile(
        r'(?P<test>[A-Z0-9 /()-]{3,})\s+(?P<value>[0-9.]+)\s+(?P<range>[<>=/\s0-9.-]+)?\s*(?P<unit>[a-zA-Z/%µμ.]+)?',
        re.IGNORECASE
    )
    matches = pattern.finditer(text)
    results = []
    for match in matches:
        test = match.group("test").strip()
        value = match.group("value")
        ref_range = match.group("range").strip() if match.group("range") else "-"
        unit = match.group("unit").strip() if match.group("unit") else "-"
        results.append({"Test": test, "Result": value, "Reference Range": ref_range, "Unit": unit})
    return pd.DataFrame(results)

def get_flag(value, ref_range):
    try:
        val = float(value)
        nums = re.findall(r'\d+\.?\d*', ref_range)
        if len(nums) == 2:
            low, high = float(nums[0]), float(nums[1])
            if val < low:
                return "Low"
            elif val > high:
                return "High"
            else:
                return "Normal"
    except:
        return "Unknown"
    return "Unknown"

def second_order_insights(df):
    insights = []
    try:
        glucose = float(df[df["Test"].str.contains("GLUCOSE", case=False)]["Result"].values[0])
        trig = float(df[df["Test"].str.contains("TRIGLYCERIDES", case=False)]["Result"].values[0])
        if glucose > 100 and trig > 150:
            insights.append("Possible insulin resistance: High glucose + high triglycerides")
    except:
        pass

    try:
        hb = float(df[df["Test"].str.contains("HEMOGLOBIN", case=False)]["Result"].values[0])
        iron = float(df[df["Test"].str.contains("IRON", case=False)]["Result"].values[0])
        if hb < 13 and iron < 65:
            insights.append("Possible anemia: Low hemoglobin and iron")
    except:
        pass

    return insights

def generate_output_json(df, insights):
    first_order = df[df["Flag"] != "Normal"]
    first_order_dict = dict(zip(first_order["Test"], first_order["Flag"]))

    causal = []
    if "glucose" in df["Test"].str.lower().values and "triglycerides" in df["Test"].str.lower().values:
        causal.append("High triglycerides + glucose suggest poor glucose metabolism")
    if "vitamin d" in df["Test"].str.lower().values:
        try:
            vit_d_val = float(df[df["Test"].str.contains("VITAMIN D", case=False)]["Result"].values[0])
            if vit_d_val < 20:
                causal.append("Low Vitamin D may reduce insulin sensitivity")
        except:
            pass

    narrative = "Based on the blood report, the following concerns were noted: " + (
        ", ".join([f"{k} is {v}" for k, v in first_order_dict.items()])
        + ". " + " ".join(insights)
        if insights else "mostly normal values."
    )

    return {
        "FirstOrderFindings": first_order_dict,
        "SecondOrderInsights": insights,
        "CausalHypotheses": causal,
        "NarrativeExplanation": narrative
    }

if uploaded_pdf:
    st.info("Extracting text from PDF...")
    text = extract_text_from_pdf(uploaded_pdf)
    df = extract_tests(text)
    df["Flag"] = df.apply(lambda row: get_flag(row["Result"], row["Reference Range"]), axis=1)

    st.subheader("Extracted Test Results")
    st.dataframe(df, use_container_width=True)

    insights = second_order_insights(df)

    st.subheader("🩺 First-order Findings")
    st.dataframe(df[df["Flag"] != "Normal"], use_container_width=True)

    st.subheader("Second-order Insights")
    if insights:
        for i in insights:
            st.warning(i)
    else:
        st.success("No second-order patterns detected.")

    output_json = generate_output_json(df, insights)

    st.subheader("JSON-Formatted Output")
    st.json(output_json)

    # Download as JSON file
    json_str = json.dumps(output_json, indent=4)
    json_bytes = BytesIO(json_str.encode('utf-8'))

    st.download_button(
        label="Download Report as JSON",
        data=json_bytes,
        file_name="blood_report_insights.json",
        mime="application/json"
    )
