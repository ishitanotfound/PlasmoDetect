import streamlit as st
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np
import os
from datetime import datetime
from fpdf import FPDF

# Set page config
st.set_page_config(page_title="PlasmoDetect", page_icon="🧬", layout="centered")

# Load model
model = load_model("malaria_model.keras")

# Languages
translations = {
    "en": {
        "title": "🧬 PlasmoDetect: Malaria Detection & Report",
        "upload": "Upload a blood smear image",
        "sample": "Or choose a sample image",
        "confidence": "Model Confidence",
        "prediction": "Prediction",
        "generate_report": "Generate Medical Report",
        "download_report": "📄 Download Report",
        "about": "About Malaria",
        "model_info": "Model Info",
        "patient_info": "Patient Information",
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "symptoms": "Symptoms",
        "doctor_note": "Doctor's Note",
        "about_text": "Malaria is a life-threatening disease caused by parasites transmitted through the bites of infected mosquitoes."
    },
    "hi": {
        "title": "🧬 PlasmoDetect: मलेरिया पहचान और रिपोर्ट",
        "upload": "एक रक्त स्मीयर छवि अपलोड करें",
        "sample": "या एक नमूना छवि चुनें",
        "confidence": "मॉडल आत्मविश्वास",
        "prediction": "पूर्वानुमान",
        "generate_report": "चिकित्सा रिपोर्ट बनाएं",
        "download_report": "📄 रिपोर्ट डाउनलोड करें",
        "about": "मलेरिया के बारे में",
        "model_info": "मॉडल जानकारी",
        "patient_info": "रोगी की जानकारी",
        "name": "नाम",
        "age": "आयु",
        "gender": "लिंग",
        "symptoms": "लक्षण",
        "doctor_note": "डॉक्टर की टिप्पणी",
        "about_text": "मलेरिया एक जानलेवा बीमारी है जो संक्रमित मच्छरों के काटने से फैलने वाले परजीवियों के कारण होती है।"
    }
}

# Language Selector with Labels
language_options = {"English": "en", "Hindi": "hi"}
selected_lang_label = st.sidebar.selectbox("🌐 Language / भाषा", list(language_options.keys()))
lang = language_options[selected_lang_label]
t = translations[lang]

# Title
st.title(t["title"])

# Patient Info
st.sidebar.header(t["patient_info"])
name = st.sidebar.text_input(t["name"])
age = st.sidebar.text_input(t["age"])
gender = st.sidebar.selectbox(t["gender"], ["Male", "Female", "Other"])
symptoms = st.sidebar.text_area(t["symptoms"])

# Image Input
uploaded_file = st.file_uploader(t["upload"], type=["jpg", "jpeg", "png"])
image = None
if uploaded_file:
    image = Image.open(uploaded_file)
else:
    sample_images = os.listdir("samples")
    sample_choice = st.selectbox(t["sample"], sample_images)
    if sample_choice:
        image = Image.open(f"samples/{sample_choice}")

# Prediction function
def predict(img):
    img_resized = img.resize((64, 64))
    img_array = np.array(img_resized) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    prob = model.predict(img_array)[0][0]
    label = "Uninfected" if prob > 0.5 else "Parasitized"  # 🔁 swapped here
    confidence = round(float(prob if label == "Uninfected" else 1 - prob) * 100, 2)
    return label, confidence


# PDF report generator
def generate_pdf(image, result, confidence):
    pdf = FPDF()
    pdf.add_page()
    
    # Title (no emoji)
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(30, 30, 120)
    pdf.cell(200, 10, "PlasmoDetect Medical Report", ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    pdf.ln(5)

    # Date
    pdf.cell(200, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    # Patient Info Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Patient Information", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 8, f"Name: {name}", ln=True)
    pdf.cell(200, 8, f"Age: {age}    Gender: {gender}", ln=True)
    pdf.multi_cell(0, 8, f"Symptoms: {symptoms}")
    pdf.ln(5)

    # Diagnostic Result Section (no emoji)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "Diagnostic Result", ln=True)
    pdf.set_font("Arial", size=12)

    # Set result text color
    if result == "Parasitized":
        pdf.set_text_color(220, 20, 60)  # red
    else:
        pdf.set_text_color(34, 139, 34)  # green

    pdf.cell(200, 10, f"Result: {result}", ln=True)
    pdf.cell(200, 10, f"Model Confidence: {confidence}%", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    pdf.set_font("Arial", 'I', 11)
    pdf.multi_cell(0, 8, f"Doctor's Note: This blood smear appears {result.lower()} based on AI analysis. It is advised to consult a certified medical professional for further diagnosis and confirmation.")
    pdf.ln(5)

    # Insert image
    img_path = "temp_image.jpg"
    image.save(img_path)
    pdf.image(img_path, x=55, y=140, w=100)
    pdf.ln(85)

    # Doctor Sign Box
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "________________________", ln=True, align='R')
    pdf.cell(200, 6, "Doctor's Signature", ln=True, align='R')


    # Save and return path
    pdf.output("malaria_report.pdf")
    return "malaria_report.pdf"


# If image is provided
if image:
    st.image(image, caption="Uploaded Image", use_container_width=True)
    result, confidence = predict(image)

# Show prediction with colored box
if result == "Parasitized":
    st.error(f"🔴 {t['prediction']}: **{result}**")
else:
    st.success(f"🟢 {t['prediction']}: **{result}**")

# Show confidence
st.info(f"{t['confidence']}: {confidence}%")

st.markdown(f"**{t['doctor_note']}:** This image appears {result.lower()}. Please consult a doctor.")

if st.button(t["generate_report"]):
    pdf_path = generate_pdf(image, result, confidence)
    with open(pdf_path, "rb") as f:
        st.download_button(t["download_report"], f, file_name="malaria_report.pdf")

# About & Model Info Tabs
with st.expander(t["about"]):
    st.write(t["about_text"])
    st.markdown("**Symptoms:** Fever, chills, headache, nausea, vomiting")

with st.expander(t["model_info"]):
    st.markdown("- Model: CNN trained on Kaggle Malaria Dataset")
    st.markdown("- Input size: 64x64 pixels")
    st.markdown("- Balanced data (Parasitized vs. Uninfected)")
    st.markdown("- Accuracy: ~95%")
